"""Disposable-only PIN-gated B release. PIN is never logged or stored.
The database must be disposable. Host caller supplies PIN from request and
trusted scrypt verifier from a separate local configuration, not the request.
"""
import datetime
from b_disposable_pin_authority import verify
from b_disposable_versioned_transaction import attempt as signed_attempt

def attempt(conn,candidate_id,research_id,pin,pin_record,context,trusted_keys,*,revoked=None,disposable=False,now=None):
 if not disposable:return {"state":"HOLD","reason":"ACTIVE_INTEGRATION_NOT_APPROVED"}
 if not isinstance(pin_record,dict):return {"state":"HOLD","reason":"PIN_NOT_ENROLLED"}
 # Lockout counter must persist across requests and process restarts.
 conn.execute("""CREATE TABLE IF NOT EXISTS disposable_pin_attempts(
  candidate_id TEXT PRIMARY KEY,failures INTEGER NOT NULL,locked_until INTEGER NOT NULL)""")
 conn.commit()
 now=int(datetime.datetime.now(datetime.timezone.utc).timestamp()) if now is None else int(now)
 row=conn.execute("SELECT failures,locked_until FROM disposable_pin_attempts WHERE candidate_id=?",(candidate_id,)).fetchone()
 if row and row[1]>now:return {"state":"HOLD","reason":"PIN_LOCKED"}
 if not verify(pin,pin_record):
  failures=(row[0] if row and row[1]<=now else 0)+1
  locked=now+300 if failures>=3 else 0
  conn.execute("""INSERT INTO disposable_pin_attempts(candidate_id,failures,locked_until)
   VALUES(?,?,?) ON CONFLICT(candidate_id) DO UPDATE SET failures=excluded.failures,locked_until=excluded.locked_until""",
   (candidate_id,failures,locked))
  conn.commit()
  return {"state":"HOLD","reason":"PIN_LOCKED" if locked else "PIN_INVALID"}
 result=signed_attempt(conn,candidate_id,research_id,context,trusted_keys,revoked=revoked,disposable=True)
 if result["state"]=="DISPOSABLE_RELEASED":
  conn.execute("DELETE FROM disposable_pin_attempts WHERE candidate_id=?",(candidate_id,))
  conn.commit()
 return result
