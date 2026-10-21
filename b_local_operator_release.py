"""Local single-operator B->C release. Fail closed; no remote identity service.

Operator-owned evidence manifest is OUTSIDE the repository. Each T04/T05/T09/T10
must point to a real file whose SHA256 matches the manifest. PIN hash stored
separately. The evidence manifest is a Human attestation, not an independent audit.
"""
import hashlib,json,sqlite3,time,datetime,uuid
from pathlib import Path
from b_disposable_pin_authority import verify as verify_pin
CONTROLS=("T04","T05","T09","T10")
def check_evidence(candidate_id,version,research_id,manifest_path):
 try:
  path=Path(manifest_path).resolve(strict=True)
  m=json.loads(path.read_text(encoding="utf-8"))
  if (m.get("candidate_id"),m.get("candidate_version"),m.get("research_id"))!=(candidate_id,version,research_id):
   return "MANIFEST_IDENTITY_MISMATCH"
  if m.get("operator_approved") is not True:return "OPERATOR_APPROVAL_MISSING"
  records=m.get("controls")
  if not isinstance(records,dict):return "CONTROL_REGISTER_MISSING"
  for name in CONTROLS:
   record=records.get(name)
   if not isinstance(record,dict) or record.get("status")!="VERIFIED":return name+"_NOT_VERIFIED"
   p=Path(record.get("file",""))
   if not p.is_absolute() or not p.is_file() or not p.resolve().is_relative_to(path.parent):
    return name+"_EVIDENCE_FILE_MISSING_OR_OUTSIDE_REGISTER"
   actual=hashlib.sha256(p.read_bytes()).hexdigest()
   if actual!=record.get("sha256"):return name+"_EVIDENCE_HASH_MISMATCH"
  return None
 except (OSError,ValueError,TypeError,KeyError,json.JSONDecodeError):
  return "EVIDENCE_MANIFEST_INVALID"
def release(conn,candidate_id,research_id,pin,pin_record,manifest_path,*,enabled=False):
 if not enabled:return {"state":"HOLD","reason":"LOCAL_RELEASE_NOT_ENABLED"}
 conn.execute("BEGIN IMMEDIATE")
 try:
  row=conn.execute("SELECT state,research_id,version FROM candidates WHERE id=?",(candidate_id,)).fetchone()
  if not row or row[0]!="B_REVIEW" or row[1]!=research_id or not row[2]:
   conn.rollback();return {"state":"HOLD","reason":"CANDIDATE_STATE_OR_VERSION_MISMATCH"}
  # No release without local PIN. Keep failed PINs out of decision ledger.
  if not verify_pin(pin,pin_record):
   conn.rollback();return {"state":"HOLD","reason":"PIN_INVALID"}
  failure=check_evidence(candidate_id,row[2],research_id,manifest_path)
  if failure:
   conn.rollback();return {"state":"HOLD","reason":failure}
  if conn.execute("SELECT 1 FROM decisions WHERE candidate_id=? AND decision='RELEASE_TO_C'",(candidate_id,)).fetchone():
   conn.rollback();return {"state":"HOLD","reason":"DUPLICATE_RELEASE"}
  count=conn.execute("""SELECT COUNT(DISTINCT candidate_id) FROM decisions
   WHERE research_id=? AND decision='RELEASE_TO_C'""",(research_id,)).fetchone()[0]
  if count>=3:
   conn.rollback();return {"state":"HOLD","reason":"T09_AGGREGATE_LIMIT"}
  stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
  conn.execute("INSERT INTO decisions(id,research_id,candidate_id,decision,rationale,created_at) VALUES(?,?,?,?,?,?)",
   ("DEC-"+uuid.uuid4().hex[:12],research_id,candidate_id,"RELEASE_TO_C","Local PIN + evidence manifest approval",stamp))
  changed=conn.execute("UPDATE candidates SET state='READY_FOR_C',stage='B' WHERE id=? AND state='B_REVIEW' AND version=?",(candidate_id,row[2]))
  if changed.rowcount!=1:raise RuntimeError("ATOMIC_RELEASE_UPDATE_FAILED")
  conn.commit()
  return {"state":"RELEASED","candidate_version":row[2]}
 except Exception:
  conn.rollback();raise
