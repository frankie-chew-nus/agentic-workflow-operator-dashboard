"""Disposable-only B->C governance release, invoked by the actual dashboard HTTP handler.

The only positive path requires BOTH an isolated disposable dashboard directory
and a host-injected trusted context. Neither form fields nor policy JSON authorize
a release. Production never calls this function.
"""
import hashlib,json
from pathlib import Path

def canonical_hash(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()

def evaluate(conn,candidate_id,research_id,version,context):
    errors=[]
    if not isinstance(context,dict) or context.get("source")!="DISPOSABLE_TEST_HOST":
        return ["TRUSTED_CONTEXT_MISSING"]
    if (context.get("candidate_id"),context.get("research_id"),context.get("version"))!=(candidate_id,research_id,version):
        errors.append("IDENTITY_VERSION_MISMATCH")
    if context.get("operator_decision")!="APPROVE_B_TO_C" or not context.get("decision_id"):
        errors.append("HUMAN_DECISION_MISSING")
    controls=context.get("controls")
    if not isinstance(controls,dict): controls={}
    for code in ("T04","T05","T09","T10"):
        rec=controls.get(code)
        if not isinstance(rec,dict) or rec.get("status")!="VERIFIED" or not isinstance(rec.get("evidence_sha256"),str) or len(rec["evidence_sha256"])!=64:
            errors.append(code+"_NOT_VERIFIED")
    if not context.get("required_resources_available",False):
        errors.append("T04_MISSING_RESOURCE")
    if context.get("prohibited_dependencies") or not context.get("dependency_inventory_reviewed",False):
        errors.append("T05_PROHIBITED_OR_UNVERIFIED_DEPENDENCY")
    if context.get("policy_change_requested") and not context.get("policy_change_approved_by_operator",False):
        errors.append("T10_UNAUTHORIZED_RULE_CHANGE")
    if context.get("policy_change_actor")=="AI_AGENT":
        errors.append("T10_AI_RULE_CHANGE")
    c=conn.execute("SELECT state,research_id,version FROM candidates WHERE id=?",(candidate_id,)).fetchone()
    if not c or (c[0],c[1],c[2])!=("B_REVIEW",research_id,version):
        errors.append("CANDIDATE_NOT_IN_B_REVIEW")
    releases=conn.execute("SELECT candidate_id FROM decisions WHERE research_id=? AND decision='RELEASE_TO_C'",(research_id,)).fetchall()
    released=[r[0] for r in releases]
    if candidate_id in released:errors.append("T09_DUPLICATE_RELEASE")
    if len(set(released))>=3:errors.append("T09_COMMISSION_LIMIT")
    if len(released)!=len(set(released)):errors.append("T09_UNRECONCILED_LEDGER")
    return sorted(set(errors))

def attempt(conn,candidate_id,research_id,version,rationale,context):
    # Caller owns the disposable connection. BEGIN IMMEDIATE serializes competing
    # requests and ensures release ledger + candidate state are one transaction.
    conn.execute("BEGIN IMMEDIATE")
    try:
        failures=evaluate(conn,candidate_id,research_id,version,context)
        if failures:
            conn.rollback()
            return {"state":"GOVERNANCE_HOLD","failures":failures,"released":False}
        import uuid,datetime
        now=datetime.datetime.now(datetime.timezone.utc).isoformat()
        conn.execute("INSERT INTO decisions(id,research_id,candidate_id,decision,rationale,created_at) VALUES(?,?,?,?,?,?)",
            ("DEC-DISPOSABLE-"+uuid.uuid4().hex[:12],research_id,candidate_id,"RELEASE_TO_C",rationale,now))
        conn.execute("UPDATE candidates SET state='READY_FOR_C',stage='B',detail=? WHERE id=?",
            ("DISPOSABLE_TEST_RELEASE_ONLY; no C execution queued",candidate_id))
        conn.commit()
        return {"state":"READY_FOR_C","failures":[],"released":True}
    except BaseException:
        conn.rollback()
        raise
