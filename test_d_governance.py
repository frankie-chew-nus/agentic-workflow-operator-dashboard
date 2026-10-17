import json,tempfile,unittest
from pathlib import Path
from operator_handoff import PRODUCTION,TEST,envelope
from d_governance import admit,open_run,finalize
class DGovernanceTests(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();self.r=Path(self.t.name);self.a=self.r/"c.json";self.a.write_text('{"ok":true}')
  self.prod=envelope("C","X","v1",PRODUCTION,[("c_summary",self.a)],"C_PASS")
  self.man=self.r/"hidden.json";self.man.write_text(json.dumps({"boundary_id":"H1","dataset_sha256":"a"*64}))
 def tearDown(self):self.t.cleanup()
 def test_valid_c_pass_admitted(self):self.assertTrue(admit(self.prod,"X","v1")["production_authority"])
 def test_c_fail_blocked(self):
  x=dict(self.prod);x["state"]="C_FAIL";self.assertFalse(admit(x,"X","v1")["production_authority"])
 def test_test_fixture_blocked(self):
  x=dict(self.prod);x["evidence_kind"]=TEST;self.assertFalse(admit(x,"X","v1")["production_authority"])
 def test_hidden_boundary_required(self):
  self.assertEqual(open_run(self.prod,"X","v1",self.r/"missing.json")["state"],"D_GOVERNANCE_HOLD")
 def test_d_pass_still_requires_human_and_cannot_advance(self):
  run=open_run(self.prod,"X","v1",self.man);ev=self.r/"ev.json"
  ev.write_text(json.dumps({"state":"D_OOS_PASS","candidate_id":"X","version":"v1"}))
  x=finalize(run,ev,self.r/"out.json");self.assertEqual(x["state"],"D_OOS_PASS");self.assertTrue(x["human_review_required"]);self.assertFalse(x["advance_to_e"])
 def test_wrong_identity_holds(self):
  run=open_run(self.prod,"X","v1",self.man);ev=self.r/"ev.json"
  ev.write_text(json.dumps({"state":"D_OOS_PASS","candidate_id":"Y","version":"v1"}))
  self.assertEqual(finalize(run,ev,self.r/"out.json")["state"],"D_GOVERNANCE_HOLD")
if __name__=="__main__":unittest.main()
