"""Signed authority through existing disposable SQLite transaction."""
import os,sqlite3,time,unittest
from b_disposable_signed_authority import sign,verify
from b_disposable_release_transaction import attempt
class SignedTransactionTests(unittest.TestCase):
 def setUp(self):
  self.key=os.urandom(32);self.db=sqlite3.connect(":memory:")
  self.db.executescript("""CREATE TABLE candidates(id TEXT PRIMARY KEY,research_id TEXT,state TEXT,stage TEXT);
CREATE TABLE decisions(id TEXT PRIMARY KEY,research_id TEXT,candidate_id TEXT,decision TEXT,rationale TEXT,created_at TEXT);
INSERT INTO candidates VALUES('CAND-B-002','RES-XAUUSD','B_REVIEW','B');""")
  self.p={"candidate_id":"CAND-B-002","research_id":"RES-XAUUSD","decision":"RELEASE_TO_C","expires_at":int(time.time())+300,"nonce":"disposable-signed-0001"}
  self.ctx={"authority_source":"INDEPENDENT_OPERATOR_REGISTER","candidate_id":"CAND-B-002","research_id":"RES-XAUUSD","production_authority":False,"controls":{k:{"status":"VERIFIED","evidence_sha256":"a"*64} for k in ("T04","T05","T09","T10")},"approval":self.p}
  self.ctx["signature"]=sign(self.p,self.key)
 def tearDown(self):self.db.close()
 def call(self):
  return attempt(self.db,"CAND-B-002","RES-XAUUSD",self.ctx,lambda cid,rid,ctx:verify(cid,rid,ctx,key=self.key),disposable=True)
 def state(self):
  return (self.db.execute("SELECT state FROM candidates").fetchone()[0],self.db.execute("SELECT COUNT(*) FROM decisions WHERE decision='RELEASE_TO_C'").fetchone()[0])
 def test_signed_release_once(self):
  self.assertEqual(self.call()["state"],"DISPOSABLE_RELEASED")
  self.assertEqual(self.state(),("READY_FOR_C",1))
  self.assertEqual(self.call()["state"],"HOLD")
  self.assertEqual(self.state(),("READY_FOR_C",1))
 def test_tampered_approval_holds(self):
  self.ctx["approval"]["decision"]="REJECT"
  self.assertEqual(self.call()["state"],"HOLD")
  self.assertEqual(self.state(),("B_REVIEW",0))
 def test_expired_approval_holds(self):
  self.ctx["approval"]["expires_at"]=int(time.time())-1
  self.ctx["signature"]=sign(self.p,self.key)
  self.assertEqual(self.call()["state"],"HOLD")
  self.assertEqual(self.state(),("B_REVIEW",0))
if __name__=="__main__":unittest.main()
