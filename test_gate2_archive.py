import json,tempfile,unittest
from pathlib import Path
from gate2_archive import build
class Gate2ArchiveTests(unittest.TestCase):
 def test_sandbox_archive_is_read_only_and_non_authoritative(self):
  with tempfile.TemporaryDirectory() as t:
   base=Path(t);root=base/"evidence";root.mkdir()
   p=root/"d_sandbox_demo/dashboard_summary.json";p.parent.mkdir()
   p.write_text(json.dumps({"state":"D_SANDBOX_PASS","candidate_id":"FIX-D-001"}))
   before=p.read_bytes();m=build(root,base/"archive")
   self.assertEqual(before,p.read_bytes())
   self.assertFalse(m["production_authority"])
   self.assertTrue((base/"archive/manifest.json").is_file())
   self.assertFalse((base/"archive"/"d_sandbox_demo").exists())
 def test_cannot_write_into_evidence(self):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t)/"evidence";root.mkdir()
   with self.assertRaises(ValueError):build(root,root/"archive")
 def test_does_not_copy_decision_rationale(self):
  import sqlite3
  with tempfile.TemporaryDirectory() as t:
   base=Path(t);root=base/"evidence";root.mkdir()
   db=root/"operator.db";con=sqlite3.connect(db)
   con.execute("CREATE TABLE decisions(id TEXT,candidate_id TEXT,decision TEXT,rationale TEXT,created_at TEXT)")
   con.execute("INSERT INTO decisions VALUES('D1','X','HOLD','SENSITIVE_REASON','2026-10-17')")
   con.commit();con.close()
   build(root,base/"archive")
   for p in (base/"archive").rglob("*"):
    if p.is_file():self.assertNotIn("SENSITIVE_REASON",p.read_text(encoding="utf-8"))
if __name__=="__main__":unittest.main()
