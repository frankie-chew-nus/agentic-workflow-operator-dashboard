"""Batch disposable release transaction checks; no active SQLite writes."""
import sqlite3,unittest
from b_disposable_release_transaction import attempt
class DisposableTransactionTests(unittest.TestCase):
 def setUp(self):
  self.c=sqlite3.connect(":memory:")
  self.c.executescript("""CREATE TABLE candidates(id TEXT PRIMARY KEY,research_id TEXT,state TEXT,stage TEXT);
  CREATE TABLE decisions(id TEXT PRIMARY KEY,research_id TEXT,candidate_id TEXT,decision TEXT,rationale TEXT,created_at TEXT);
  INSERT INTO candidates VALUES('CAND-B-002','RES-XAUUSD','B_REVIEW','B');""")
  self.ctx={"authority_source":"INDEPENDENT_OPERATOR_REGISTER","candidate_id":"CAND-B-002",
   "research_id":"RES-XAUUSD","production_authority":False,
   "controls":{k:{"status":"VERIFIED","evidence_sha256":"a"*64} for k in ("T04","T05","T09","T10")}}
 def tearDown(self):self.c.close()
 def run_gate(self,ctx=None,verifier=None,disposable=True):
  return attempt(self.c,"CAND-B-002","RES-XAUUSD",self.ctx if ctx is None else ctx,
                 verifier,disposable=disposable)
 def test_missing_verifier_no_write(self):
  self.assertEqual(self.run_gate()["state"],"HOLD")
  self.assertEqual(self.c.execute("SELECT COUNT(*) FROM decisions").fetchone()[0],0)
 def test_tampered_t09_no_write(self):
  ctx={**self.ctx,"controls":{**self.ctx["controls"],"T09":{"status":"UNVERIFIED"}}}
  self.assertEqual(self.run_gate(ctx,lambda *args:True)["state"],"HOLD")
  self.assertEqual(self.c.execute("SELECT COUNT(*) FROM decisions").fetchone()[0],0)
 def test_verifier_denial_no_write(self):
  self.assertEqual(self.run_gate(verifier=lambda *args:False)["state"],"HOLD")
 def test_disposable_positive_exactly_once(self):
  self.assertEqual(self.run_gate(verifier=lambda *args:True)["state"],"DISPOSABLE_RELEASED")
  self.assertEqual(self.c.execute("SELECT COUNT(*) FROM decisions").fetchone()[0],1)
  self.assertEqual(self.c.execute("SELECT state FROM candidates").fetchone()[0],"READY_FOR_C")
  self.assertEqual(self.run_gate(verifier=lambda *args:True)["state"],"HOLD")
  self.assertEqual(self.c.execute("SELECT COUNT(*) FROM decisions").fetchone()[0],1)
 def test_active_mode_never_writes(self):
  self.assertEqual(self.run_gate(verifier=lambda *args:True,disposable=False)["state"],"HOLD")
  self.assertEqual(self.c.execute("SELECT COUNT(*) FROM decisions").fetchone()[0],0)
if __name__=="__main__":unittest.main()
