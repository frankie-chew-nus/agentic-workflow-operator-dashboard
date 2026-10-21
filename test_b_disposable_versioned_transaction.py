"""End-to-end version-bound approval in disposable SQLite."""
import os,sqlite3,tempfile,time,unittest
from pathlib import Path
from b_disposable_trusted_approval import sign
from b_disposable_versioned_transaction import attempt
class VersionedTransactionTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.path=Path(self.tmp.name)/"test.sqlite"
  self.key=os.urandom(32);self.keys={"operator-test-key-1":self.key}
  c=sqlite3.connect(self.path)
  try:
   c.executescript("""CREATE TABLE candidates(id TEXT PRIMARY KEY,research_id TEXT,state TEXT,stage TEXT,version TEXT);
CREATE TABLE decisions(id TEXT PRIMARY KEY,research_id TEXT,candidate_id TEXT,decision TEXT,rationale TEXT,created_at TEXT);
CREATE TABLE disposable_authority_nonces(nonce TEXT PRIMARY KEY,candidate_id TEXT,research_id TEXT,used_at TEXT);
INSERT INTO candidates VALUES('A','R','B_REVIEW','B','v1');""")
   c.commit()
  finally:c.close()
 def tearDown(self):self.tmp.cleanup()
 def ctx(self,version="v1"):
  p={"candidate_id":"A","candidate_version":version,"research_id":"R","decision":"RELEASE_TO_C",
     "expires_at":int(time.time())+300,"nonce":"versioned-test-nonce-00001","signer_id":"operator-test-key-1"}
  return {"authority_source":"INDEPENDENT_OPERATOR_REGISTER","candidate_id":"A","research_id":"R",
   "production_authority":False,"controls":{k:{"status":"VERIFIED","evidence_sha256":"a"*64} for k in ("T04","T05","T09","T10")},
   "approval":p,"signature":sign(p,self.key)}
 def run_attempt(self,ctx,revoked=None):
  c=sqlite3.connect(self.path)
  try:return attempt(c,"A","R",ctx,self.keys,revoked=revoked,disposable=True)
  finally:c.close()
 def counts(self):
  c=sqlite3.connect(self.path)
  try:return (c.execute("SELECT state FROM candidates WHERE id='A'").fetchone()[0],
   c.execute("SELECT COUNT(*) FROM decisions WHERE decision='RELEASE_TO_C'").fetchone()[0],
   c.execute("SELECT COUNT(*) FROM disposable_authority_nonces").fetchone()[0])
  finally:c.close()
 def test_version_bound_release(self):
  self.assertEqual(self.run_attempt(self.ctx())["state"],"DISPOSABLE_RELEASED")
  self.assertEqual(self.counts(),("READY_FOR_C",1,1))
 def test_version_mismatch_hold(self):
  self.assertEqual(self.run_attempt(self.ctx("v2"))["state"],"HOLD")
  self.assertEqual(self.counts(),("B_REVIEW",0,0))
 def test_revoked_signer_hold(self):
  self.assertEqual(self.run_attempt(self.ctx(),revoked={"operator-test-key-1"})["state"],"HOLD")
  self.assertEqual(self.counts(),("B_REVIEW",0,0))
 def test_duplicate_hold(self):
  ctx=self.ctx()
  self.assertEqual(self.run_attempt(ctx)["state"],"DISPOSABLE_RELEASED")
  self.assertEqual(self.run_attempt(ctx)["state"],"HOLD")
  self.assertEqual(self.counts(),("READY_FOR_C",1,1))
if __name__=="__main__":unittest.main()
