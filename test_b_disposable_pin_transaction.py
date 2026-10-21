"""Disposable PIN + signed version-bound release and persistent lockout."""
import os,sqlite3,tempfile,time,unittest
from pathlib import Path
from b_disposable_pin_authority import enroll
from b_disposable_trusted_approval import sign
from b_disposable_pin_transaction import attempt
class PinTransactionTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.path=Path(self.temp.name)/"test.sqlite"
  self.key=os.urandom(32);self.keys={"test-signer":self.key};self.record=enroll("736291")
  c=sqlite3.connect(self.path)
  try:
   c.executescript("""CREATE TABLE candidates(id TEXT PRIMARY KEY,research_id TEXT,state TEXT,stage TEXT,version TEXT);
CREATE TABLE decisions(id TEXT PRIMARY KEY,research_id TEXT,candidate_id TEXT,decision TEXT,rationale TEXT,created_at TEXT);
CREATE TABLE disposable_authority_nonces(nonce TEXT PRIMARY KEY,candidate_id TEXT,research_id TEXT,used_at TEXT);
INSERT INTO candidates VALUES('A','R','B_REVIEW','B','v1');""")
   c.commit()
  finally:c.close()
 def tearDown(self):self.temp.cleanup()
 def context(self,version="v1"):
  p={"candidate_id":"A","candidate_version":version,"research_id":"R","decision":"RELEASE_TO_C",
     "expires_at":int(time.time())+300,"nonce":"pin-versioned-nonce-00001","signer_id":"test-signer"}
  return {"authority_source":"INDEPENDENT_OPERATOR_REGISTER","candidate_id":"A","research_id":"R",
   "production_authority":False,"controls":{k:{"status":"VERIFIED","evidence_sha256":"a"*64} for k in ("T04","T05","T09","T10")},
   "approval":p,"signature":sign(p,self.key)}
 def call(self,pin,ctx=None,now=None):
  c=sqlite3.connect(self.path)
  try:return attempt(c,"A","R",pin,self.record,self.context() if ctx is None else ctx,self.keys,disposable=True,now=now)
  finally:c.close()
 def snapshot(self):
  c=sqlite3.connect(self.path)
  try:return (c.execute("SELECT state FROM candidates").fetchone()[0],
   c.execute("SELECT COUNT(*) FROM decisions WHERE decision='RELEASE_TO_C'").fetchone()[0],
   c.execute("SELECT COUNT(*) FROM disposable_authority_nonces").fetchone()[0])
  finally:c.close()
 def test_correct_pin_and_signed_version_release(self):
  self.assertEqual(self.call("736291")["state"],"DISPOSABLE_RELEASED")
  self.assertEqual(self.snapshot(),("READY_FOR_C",1,1))
 def test_wrong_pin_holds(self):
  self.assertEqual(self.call("736292")["reason"],"PIN_INVALID")
  self.assertEqual(self.snapshot(),("B_REVIEW",0,0))
 def test_three_failures_lockout_persists(self):
  for i in range(3):self.call("000000")
  self.assertEqual(self.call("736291")["reason"],"PIN_LOCKED")
  self.assertEqual(self.snapshot(),("B_REVIEW",0,0))
 def test_version_mismatch_holds_after_correct_pin(self):
  self.assertEqual(self.call("736291",self.context("v2"))["state"],"HOLD")
  self.assertEqual(self.snapshot(),("B_REVIEW",0,0))
 def test_duplicate_after_valid_release(self):
  self.assertEqual(self.call("736291")["state"],"DISPOSABLE_RELEASED")
  self.assertEqual(self.call("736291")["state"],"HOLD")
  self.assertEqual(self.snapshot(),("READY_FOR_C",1,1))
 def test_no_pin_enrollment_holds(self):
  c=sqlite3.connect(self.path)
  try:self.assertEqual(attempt(c,"A","R","736291",None,self.context(),self.keys,disposable=True)["reason"],"PIN_NOT_ENROLLED")
  finally:c.close()
if __name__=="__main__":unittest.main()
