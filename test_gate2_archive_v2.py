import hashlib,json,sqlite3,tempfile,unittest
from pathlib import Path
from gate2_archive import build
from gate2_decision_digest import digest
class ArchiveV2Tests(unittest.TestCase):
 def test_decision_digest_has_no_rationale(self):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t);db=root/"operator.db";c=sqlite3.connect(db)
   c.execute("CREATE TABLE decisions(id TEXT,candidate_id TEXT,decision TEXT,rationale TEXT,created_at TEXT)")
   c.execute("INSERT INTO decisions VALUES('D1','X','HOLD','PRIVATE_REASON','2026-10-17')");c.commit();c.close()
   x=digest(root);self.assertEqual(x["count"],1)
   self.assertNotIn("PRIVATE_REASON",json.dumps(x))
 def test_test_capture_hash_is_checked(self):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t)/"evidence";root.mkdir();cap=Path(t)/"run.json"
   cap.write_text(json.dumps({"schema":"gate2-test-run-v1","result":"PASS","log":"x","log_sha256":"bad"}))
   with self.assertRaises(ValueError):build(root,Path(t)/"archive",cap)
 def test_judgement_is_not_fabricated(self):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t)/"evidence";root.mkdir();out=Path(t)/"archive"
   build(root,out)
   x=json.loads((out/"06_operator_judgement/judgement_record_template.json").read_text())
   self.assertEqual(x["status"],"HUMAN_REVIEW_REQUIRED");self.assertTrue(x["entries"]);self.assertTrue(all(e["human_statement"] is None for e in x["entries"]))
if __name__=="__main__":unittest.main()
