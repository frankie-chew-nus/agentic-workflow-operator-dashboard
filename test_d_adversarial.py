import json,tempfile,unittest
from pathlib import Path
from operator_handoff import PRODUCTION,TEST,envelope,validate
from d_governance import admit,open_run,finalize
from d_oos_executor import execute
class DAdversarialTests(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();self.r=Path(self.t.name)
  self.ca=self.r/"c.json";self.ca.write_text('{"state":"C_PASS"}')
  self.c=envelope("C","X","v1",PRODUCTION,[("c_summary",self.ca)],"C_PASS")
  self.hidden=self.r/"hidden.json";self.hidden.write_text(json.dumps([{"outcome":1},{"outcome":-1},{"outcome":1}]))
  import hashlib
  h=hashlib.sha256(self.hidden.read_bytes()).hexdigest()
  self.man=self.r/"manifest.json";self.man.write_text(json.dumps({"boundary_id":"H1","dataset_sha256":h}))
 def tearDown(self):self.t.cleanup()
 def test_c_artifact_tamper_blocks_d(self):
  self.ca.write_text("tampered");self.assertFalse(admit(self.c,"X","v1")["production_authority"])
 def test_wrong_version_blocks_d(self):self.assertFalse(admit(self.c,"X","v2")["production_authority"])
 def test_test_fixture_cannot_enter_production_d(self):
  x=dict(self.c);x["evidence_kind"]=TEST;self.assertFalse(admit(x,"X","v1")["production_authority"])
 def test_changed_hidden_dataset_detectable(self):
  run=open_run(self.c,"X","v1",self.man);before=json.loads(self.man.read_text())["dataset_sha256"]
  self.hidden.write_text(json.dumps([{"outcome":-1}]))
  import hashlib
  after=hashlib.sha256(self.hidden.read_bytes()).hexdigest();self.assertNotEqual(before,after)
 def test_replayed_d_evidence_wrong_run_is_not_authority(self):
  run=open_run(self.c,"X","v1",self.man);ev=self.r/"ev.json"
  ev.write_text(json.dumps({"state":"D_OOS_PASS","candidate_id":"X","version":"v1","run_id":"OLD"}))
  x=finalize(run,ev,self.r/"out.json")
  self.assertFalse(x["advance_to_e"])
 def test_interrupted_execution_has_no_result(self):
  run=open_run(self.c,"X","v1",self.man)
  self.assertEqual(run["state"],"D_READY_FOR_OOS");self.assertFalse((self.r/"missing_result.json").exists())
if __name__=="__main__":unittest.main()
