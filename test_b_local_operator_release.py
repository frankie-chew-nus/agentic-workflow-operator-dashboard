"""Real-file manifest and local PIN transaction, disposable SQLite only."""
import hashlib,json,sqlite3,tempfile,unittest
from pathlib import Path
from b_disposable_pin_authority import enroll
from b_local_operator_release import release
class LocalReleaseTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
  self.db=self.root/"test.sqlite";self.pin=enroll("736291")
  c=sqlite3.connect(self.db)
  try:
   c.executescript("""CREATE TABLE candidates(id TEXT PRIMARY KEY,research_id TEXT,state TEXT,stage TEXT,version TEXT);
CREATE TABLE decisions(id TEXT PRIMARY KEY,research_id TEXT,candidate_id TEXT,decision TEXT,rationale TEXT,created_at TEXT);
INSERT INTO candidates VALUES('A','R','B_REVIEW','B','v1');""")
   c.commit()
  finally:c.close()
  controls={}
  for name in ("T04","T05","T09","T10"):
   p=self.root/(name+".txt");p.write_text(name+" independently reviewed fixture",encoding="utf-8")
   controls[name]={"status":"VERIFIED","file":str(p),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
  self.manifest=self.root/"manifest.json"
  self.obj={"candidate_id":"A","candidate_version":"v1","research_id":"R","operator_approved":True,"controls":controls}
  self.save()
 def save(self):self.manifest.write_text(json.dumps(self.obj),encoding="utf-8")
 def tearDown(self):self.tmp.cleanup()
 def call(self,pin="736291",enabled=True):
  c=sqlite3.connect(self.db)
  try:return release(c,"A","R",pin,self.pin,self.manifest,enabled=enabled)
  finally:c.close()
 def count(self):
  c=sqlite3.connect(self.db)
  try:return c.execute("SELECT COUNT(*) FROM decisions WHERE decision='RELEASE_TO_C'").fetchone()[0]
  finally:c.close()
 def test_valid_release_once(self):
  self.assertEqual(self.call()["state"],"RELEASED")
  self.assertEqual(self.call()["state"],"HOLD")
  self.assertEqual(self.count(),1)
 def test_disabled_holds(self):self.assertEqual(self.call(enabled=False)["state"],"HOLD")
 def test_wrong_pin_holds(self):
  self.assertEqual(self.call(pin="000000")["reason"],"PIN_INVALID");self.assertEqual(self.count(),0)
 def test_unapproved_holds(self):
  self.obj["operator_approved"]=False;self.save()
  self.assertEqual(self.call()["reason"],"OPERATOR_APPROVAL_MISSING")
 def test_tampered_evidence_holds(self):
  p=Path(self.obj["controls"]["T04"]["file"]);p.write_text("changed",encoding="utf-8")
  self.assertEqual(self.call()["reason"],"T04_EVIDENCE_HASH_MISMATCH")
 def test_version_change_holds(self):
  self.obj["candidate_version"]="v2";self.save()
  self.assertEqual(self.call()["reason"],"MANIFEST_IDENTITY_MISMATCH")
if __name__=="__main__":unittest.main()
