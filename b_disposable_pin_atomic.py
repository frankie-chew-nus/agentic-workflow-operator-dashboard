"""Disposable-only atomic PIN + signed release. No active dashboard integration."""
import datetime,uuid
from b_disposable_pin_authority import verify as verify_pin
from b_disposable_trusted_approval import verify as verify_signed
from b_release_guard_candidate import release_preflight

def attempt(conn,candidate_id,research_id,pin,pin_record,context,trusted_keys,*,revoked=None,now=None,disposable=False):
 if not disposable:return {"state":"HOLD","reason":"ACTIVE_INTEGRATION_NOT_APPROVED"}
 moment=int(datetime.datetime.now(datetime.timezone.utc).timestamp()) if now is None else int(now)
 conn.execute("BEGIN IMMEDIATE")
 try:
  # Tables must be initialized by disposable setup, outside this transaction.
  row=conn.execute("SELECT state,research_id,version FROM candidates WHERE id=?",(candidate_id,)).fetchone()
  if not row or row[0]!="B_REVIEW" or row[1]!=research_id or not row[2]:
   conn.rollback();return {"state":"HOLD","reason":"CANDIDATE_STATE_OR_VERSION"}
  lock=conn.execute("SELECT failures,locked_until FROM disposable_pin_attempts WHERE candidate_id=?",(candidate_id,)).fetchone()
  if lock and lock[1]>moment:
   conn.rollback();return {"state":"HOLD","reason":"PIN_LOCKED"}
  if not verify_pin(pin,pin_record):
   failures=(lock[0] if lock and lock[1]<=moment else 0)+1
   locked_until=moment+300 if failures>=3 else 0
   conn.execute("""INSERT INTO disposable_pin_attempts(candidate_id,failures,locked_until)
    VALUES(?,?,?) ON CONFLICT(candidate_id) DO UPDATE SET
    failures=excluded.failures,locked_until=excluded.locked_until""",(candidate_id,failures,locked_until))
   conn.commit()
   return {"state":"HOLD","reason":"PIN_LOCKED" if locked_until else "PIN_INVALID"}
  baseline=release_preflight(candidate_id=candidate_id,research_id=research_id,verified_context=context)
  failures=[x for x in baseline["failures"] if x!="LIVE_AUTHORITY_BINDING_NOT_IMPLEMENTED"]
  if failures:
   conn.rollback();return {"state":"HOLD","reason":",".join(failures)}
  if not verify_signed(candidate_id,row[2],research_id,context,trusted_keys=trusted_keys,revoked=revoked,now=moment):
   conn.rollback();return {"state":"HOLD","reason":"SIGNED_AUTHORITY_INVALID"}
  nonce=context["approval"]["nonce"]
  if conn.execute("SELECT 1 FROM disposable_authority_nonces WHERE nonce=?",(nonce,)).fetchone():
   conn.rollback();return {"state":"HOLD","reason":"NONCE_REPLAY"}
  if conn.execute("SELECT 1 FROM decisions WHERE candidate_id=? AND decision='RELEASE_TO_C'",(candidate_id,)).fetchone():
   conn.rollback();return {"state":"HOLD","reason":"DUPLICATE_RELEASE"}
  timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
  conn.execute("INSERT INTO disposable_authority_nonces VALUES(?,?,?,?)",(nonce,candidate_id,research_id,timestamp))
  conn.execute("INSERT INTO decisions(id,research_id,candidate_id,decision,rationale,created_at) VALUES(?,?,?,?,?,?)",
   ("SYN-"+uuid.uuid4().hex[:10],research_id,candidate_id,"RELEASE_TO_C","Disposable PIN verified",timestamp))
  updated=conn.execute("UPDATE candidates SET state='READY_FOR_C',stage='B' WHERE id=? AND state='B_REVIEW' AND version=?",(candidate_id,row[2]))
  if updated.rowcount!=1:raise RuntimeError("ATOMIC_CANDIDATE_UPDATE_FAILED")
  conn.execute("DELETE FROM disposable_pin_attempts WHERE candidate_id=?",(candidate_id,))
  conn.commit()
  return {"state":"DISPOSABLE_RELEASED","production_authority":False}
 except Exception:
  conn.rollback();raise
