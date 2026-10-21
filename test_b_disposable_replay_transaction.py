"""Atomic nonce replay tests using disposable SQLite database."""
import os,sqlite3,tempfile,time,unittest
from pathlib import Path
from b_disposable_signed_authority import sign
from b_disposable_replay_transaction import attempt
class ReplayTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.path=Path(self.tmp.name)/"disposable.sqlite"
  self.key=os.urandom(32)
  c=sqlite3.connect(self.path)
  c.executescript("""CREATE TABLE candidates(id TEXT PRIMARY KEY,research_id TEXT,state TEXT,stage TEXT);
CREATE TABLE decisions(id TEXT PRIMARY KEY,research_id TEXT,candidate_id TEXT,decision TEXT,rationale TEXT,created_at TEXT);
INSERT INTO candidates VALUES('A','R','B_REVIEW','B');
INSERT INTO candidates VALUES('B','R','B_REVIEW','B');""")
  c.execute("""CREATE TABLE disposable_authority_nonces(nonce TEXT PRIMARY KEY,candidate_id TEXT NOT NULL,research_id TEXT NOT NULL,used_at TEXT NOT NULL)""")
  c.commit();c.close()
 def tearDown(self):self.tmp.cleanup()
 def context(self,cid,nonce,expires=None):
  p={"candidate_id":cid,"research_id":"R","decision":"RELEASE_TO_C",
     "expires_at":expires if expires is not None else int(time.time())+300,"nonce":nonce}
  return {"authority_source":"INDEPENDENT_OPERATOR_REGISTER","candidate_id":cid,"research_id":"R",
   "production_authority":False,"controls":{k:{"status":"VERIFIED","evidence_sha256":"a"*64} for k in ("T04","T05","T09","T10")},
   "approval":p,"signature":sign(p,self.key)}
 def call(self,cid,ctx,key=None):
  c=sqlite3.connect(self.path,timeout=10)
  try:
   return attempt(c,cid,"R",ctx,self.key if key is None else key,disposable=True)
  finally:c.close()
 def count(self):
  c=sqlite3.connect(self.path)
  try:
   return (c.execute("SELECT COUNT(*) FROM decisions WHERE decision='RELEASE_TO_C'").fetchone()[0],
    c.execute("SELECT COUNT(*) FROM disposable_authority_nonces").fetchone()[0])
  finally:c.close()
 def test_valid_and_duplicate(self):
  ctx=self.context("A","unique-nonce-00000001")
  self.assertEqual(self.call("A",ctx)["state"],"DISPOSABLE_RELEASED")
  self.assertEqual(self.call("A",ctx)["state"],"HOLD")
  self.assertEqual(self.count(),(1,1))
 def test_cross_candidate_replay(self):
  self.assertEqual(self.call("A",self.context("A","unique-nonce-00000001"))["state"],"DISPOSABLE_RELEASED")
  self.assertEqual(self.call("B",self.context("B","unique-nonce-00000001"))["reason"],"AUTHORITY_NONCE_REPLAY")
  self.assertEqual(self.count(),(1,1))
 def test_new_nonce_different_candidate(self):
  self.assertEqual(self.call("A",self.context("A","unique-nonce-00000001"))["state"],"DISPOSABLE_RELEASED")
  self.assertEqual(self.call("B",self.context("B","unique-nonce-00000002"))["state"],"DISPOSABLE_RELEASED")
  self.assertEqual(self.count(),(2,2))
 def test_bad_signature_does_not_consume_nonce(self):
  ctx=self.context("A","unique-nonce-00000001")
  self.assertEqual(self.call("A",ctx,key=os.urandom(32))["state"],"HOLD")
  self.assertEqual(self.count(),(0,0))
  self.assertEqual(self.call("A",ctx)["state"],"DISPOSABLE_RELEASED")
 def test_expired_does_not_consume_nonce(self):
  self.assertEqual(self.call("A",self.context("A","unique-nonce-00000001",int(time.time())-1))["state"],"HOLD")
  self.assertEqual(self.count(),(0,0))
 def test_no_active_mode(self):
  ctx=self.context("A","unique-nonce-00000001")
  c=sqlite3.connect(self.path)
  try:
   self.assertEqual(attempt(c,"A","R",ctx,self.key)["reason"],"ACTIVE_INTEGRATION_NOT_APPROVED")
  finally:c.close()
  self.assertEqual(self.count()[0],0)
if __name__=="__main__":unittest.main()
