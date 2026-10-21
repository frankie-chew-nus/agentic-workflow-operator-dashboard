"""Concurrent disposable PIN verification and release tests."""
import concurrent.futures,os,sqlite3,tempfile,time,unittest
from pathlib import Path
from b_disposable_pin_authority import enroll
from b_disposable_trusted_approval import sign
from b_disposable_pin_atomic import attempt
class AtomicPINTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.path=Path(self.temp.name)/"db.sqlite"
  self.pin=enroll("736291");self.key=os.urandom(32);self.keys={"operator-test":self.key}
  c=sqlite3.connect(self.path)
  try:
   c.executescript("""CREATE TABLE candidates(id TEXT PRIMARY KEY,research_id TEXT,state TEXT,stage TEXT,version TEXT);
CREATE TABLE decisions(id TEXT PRIMARY KEY,research_id TEXT,candidate_id TEXT,decision TEXT,rationale TEXT,created_at TEXT);
CREATE TABLE disposable_authority_nonces(nonce TEXT PRIMARY KEY,candidate_id TEXT,research_id TEXT,used_at TEXT);
CREATE TABLE disposable_pin_attempts(candidate_id TEXT PRIMARY KEY,failures INTEGER,locked_until INTEGER);
INSERT INTO candidates VALUES('A','R','B_REVIEW','B','v1');""")
   c.commit()
  finally:c.close()
  p={"candidate_id":"A","candidate_version":"v1","research_id":"R","decision":"RELEASE_TO_C",
     "expires_at":int(time.time())+300,"nonce":"atomic-pin-nonce-00001","signer_id":"operator-test"}
  self.ctx={"authority_source":"INDEPENDENT_OPERATOR_REGISTER","candidate_id":"A","research_id":"R",
   "production_authority":False,"controls":{k:{"status":"VERIFIED","evidence_sha256":"a"*64} for k in ("T04","T05","T09","T10")},
   "approval":p,"signature":sign(p,self.key)}
 def tearDown(self):self.temp.cleanup()
 def call(self,pin):
  c=sqlite3.connect(self.path,timeout=20)
  try:return attempt(c,"A","R",pin,self.pin,self.ctx,self.keys,disposable=True)
  finally:c.close()
 def snapshot(self):
  c=sqlite3.connect(self.path)
  try:
   return (c.execute("SELECT state FROM candidates").fetchone()[0],
    c.execute("SELECT COUNT(*) FROM decisions WHERE decision='RELEASE_TO_C'").fetchone()[0],
    c.execute("SELECT COUNT(*) FROM disposable_authority_nonces").fetchone()[0])
  finally:c.close()
 def test_concurrent_valid_release_once(self):
  with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
   outcomes=list(pool.map(self.call,["736291"]*5))
  self.assertEqual(sum(x["state"]=="DISPOSABLE_RELEASED" for x in outcomes),1)
  self.assertEqual(self.snapshot(),("READY_FOR_C",1,1))
 def test_concurrent_wrong_pin_locks(self):
  with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
   outcomes=list(pool.map(self.call,["000000"]*5))
  self.assertTrue(all(x["state"]=="HOLD" for x in outcomes))
  self.assertEqual(self.call("736291")["reason"],"PIN_LOCKED")
  self.assertEqual(self.snapshot(),("B_REVIEW",0,0))
 def test_valid_after_one_wrong_pin(self):
  self.assertEqual(self.call("000000")["reason"],"PIN_INVALID")
  self.assertEqual(self.call("736291")["state"],"DISPOSABLE_RELEASED")
 def test_wrong_version_holds(self):
  self.ctx["approval"]["candidate_version"]="v2"
  self.assertEqual(self.call("736291")["state"],"HOLD")
  self.assertEqual(self.snapshot(),("B_REVIEW",0,0))
if __name__=="__main__":unittest.main()
