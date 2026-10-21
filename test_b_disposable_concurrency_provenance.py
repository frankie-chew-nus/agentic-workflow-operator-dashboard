"""Disposable concurrency and approval provenance regression tests."""
import concurrent.futures,os,sqlite3,tempfile,time,unittest
from pathlib import Path
from b_disposable_signed_authority import sign
from b_disposable_replay_transaction import attempt

class ConcurrentReleaseTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory()
  self.path=Path(self.temp.name)/"disposable.sqlite"
  self.key=os.urandom(32)
  conn=sqlite3.connect(self.path)
  try:
   conn.executescript("""CREATE TABLE candidates(id TEXT PRIMARY KEY,research_id TEXT,state TEXT,stage TEXT);
CREATE TABLE decisions(id TEXT PRIMARY KEY,research_id TEXT,candidate_id TEXT,decision TEXT,rationale TEXT,created_at TEXT);
CREATE TABLE disposable_authority_nonces(nonce TEXT PRIMARY KEY,candidate_id TEXT NOT NULL,research_id TEXT NOT NULL,used_at TEXT NOT NULL);
INSERT INTO candidates VALUES('A','R','B_REVIEW','B');
INSERT INTO candidates VALUES('B','R','B_REVIEW','B');""")
   conn.commit()
  finally:conn.close()
 def tearDown(self):self.temp.cleanup()
 def context(self,cid,nonce):
  approval={"candidate_id":cid,"research_id":"R","decision":"RELEASE_TO_C",
            "expires_at":int(time.time())+300,"nonce":nonce}
  return {"authority_source":"INDEPENDENT_OPERATOR_REGISTER","candidate_id":cid,
          "research_id":"R","production_authority":False,
          "controls":{k:{"status":"VERIFIED","evidence_sha256":"a"*64} for k in ("T04","T05","T09","T10")},
          "approval":approval,"signature":sign(approval,self.key)}
 def call(self,cid,ctx):
  c=sqlite3.connect(self.path,timeout=15)
  try:return attempt(c,cid,"R",ctx,self.key,disposable=True)
  finally:c.close()
 def snapshot(self):
  c=sqlite3.connect(self.path)
  try:return (c.execute("SELECT COUNT(*) FROM decisions WHERE decision='RELEASE_TO_C'").fetchone()[0],
    c.execute("SELECT COUNT(*) FROM disposable_authority_nonces").fetchone()[0],
    c.execute("SELECT COUNT(*) FROM candidates WHERE state='READY_FOR_C'").fetchone()[0])
  finally:c.close()
 def test_same_candidate_concurrent_requests_release_once(self):
  ctx=self.context("A","concurrent-unique-nonce-0001")
  with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
   results=list(pool.map(lambda _:self.call("A",ctx),range(8)))
  self.assertEqual(sum(x["state"]=="DISPOSABLE_RELEASED" for x in results),1)
  self.assertEqual(self.snapshot(),(1,1,1))
 def test_cross_candidate_same_nonce_concurrent_requests_release_once(self):
  a=self.context("A","shared-concurrent-nonce-0001")
  b=self.context("B","shared-concurrent-nonce-0001")
  with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
   fa=pool.submit(self.call,"A",a);fb=pool.submit(self.call,"B",b)
   results=[fa.result(),fb.result()]
  self.assertEqual(sum(x["state"]=="DISPOSABLE_RELEASED" for x in results),1)
  self.assertEqual(self.snapshot(),(1,1,1))
 def test_independent_distinct_nonces_both_release(self):
  with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
   fa=pool.submit(self.call,"A",self.context("A","unique-nonce-a-000001"))
   fb=pool.submit(self.call,"B",self.context("B","unique-nonce-b-000002"))
   results=[fa.result(),fb.result()]
  self.assertEqual(sum(x["state"]=="DISPOSABLE_RELEASED" for x in results),2)
  self.assertEqual(self.snapshot(),(2,2,2))
 def test_claimed_provenance_is_not_independent_identity(self):
  # Structural source label alone cannot authenticate a person; wrong signing key must fail.
  ctx=self.context("A","provenance-claim-000001")
  ctx["operator_name"]="Human Operator"
  ctx["approval"]["operator_name"]="Human Operator"
  ctx["signature"]=sign(ctx["approval"],os.urandom(32))
  self.assertEqual(self.call("A",ctx)["state"],"HOLD")
  self.assertEqual(self.snapshot(),(0,0,0))
if __name__=="__main__":unittest.main()
