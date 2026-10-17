import hashlib,json,tempfile,unittest
from pathlib import Path
from gate2_archive import build
from gate2_test_log_sanitize import sanitize
class ArchiveV3Tests(unittest.TestCase):
 def test_log_whitelist_excludes_secrets(self):
  log="test_ok (test_example.TestCase.test_ok) ... ok\nSECRET_API_KEY=abc\nRan 1 test in 0.001s\nOK\n"
  clean=sanitize(log);self.assertNotIn("SECRET_API_KEY",clean);self.assertIn("Ran 1 test",clean)
 def test_v3_includes_log_and_unapproved_judgement(self):
  with tempfile.TemporaryDirectory() as t:
   base=Path(t);root=base/"evidence";root.mkdir();out=base/"archive"
   log="test_ok (test_example.TestCase.test_ok) ... ok\nRan 1 test in 0.001s\nOK\n"
   cap=base/"test.json";cap.write_text(json.dumps({"schema":"gate2-test-run-v1","result":"PASS","log":log,"log_sha256":hashlib.sha256(log.encode()).hexdigest()}))
   x=build(root,out,cap);self.assertEqual(x["archive_version"],"v3")
   self.assertTrue((out/"04_automated_tests/sanitized_test_log.json").is_file())
   j=json.loads((out/"06_operator_judgement/judgement_record_template.json").read_text())
   self.assertEqual(j["status"],"HUMAN_REVIEW_REQUIRED")
   self.assertTrue(all(e["human_statement"] is None for e in j["entries"]))
if __name__=="__main__":unittest.main()
