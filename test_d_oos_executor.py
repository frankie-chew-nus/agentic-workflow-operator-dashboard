import json,tempfile,unittest
from pathlib import Path
from d_oos_executor import execute
class DOOSTests(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();self.r=Path(self.t.name)
  self.run={"state":"D_READY_FOR_OOS","candidate_id":"X","version":"v1","run_id":"D-1"}
 def tearDown(self):self.t.cleanup()
 def test_pass_and_hidden_rows_not_emitted(self):
  h=self.r/"h.json";h.write_text(json.dumps([{"outcome":1},{"outcome":-1},{"outcome":1}]))
  x=execute(self.run,h,self.r/"o.json");self.assertEqual(x["state"],"D_OOS_PASS");self.assertFalse(x["hidden_rows_emitted"]);self.assertNotIn("rows",x)
 def test_fail(self):
  h=self.r/"h.json";h.write_text(json.dumps([{"outcome":-1}]))
  self.assertEqual(execute(self.run,h,self.r/"o.json")["state"],"D_OOS_FAIL")
 def test_unready_run_holds(self):
  h=self.r/"h.json";h.write_text(json.dumps([{"outcome":1}]));run=dict(self.run);run["state"]="D_GOVERNANCE_HOLD"
  self.assertEqual(execute(run,h,self.r/"o.json")["state"],"D_OOS_HOLD")
 def test_output_contains_hash_not_hidden_payload(self):
  h=self.r/"h.json";secret=[{"outcome":1,"secret":"HIDDEN-OOS-VALUE"}];h.write_text(json.dumps(secret))
  execute(self.run,h,self.r/"o.json");text=(self.r/"o.json").read_text();self.assertNotIn("HIDDEN-OOS-VALUE",text);self.assertIn("hidden_dataset_sha256",text)
if __name__=="__main__":unittest.main()
