import json,tempfile,unittest
from pathlib import Path
from evidence_discovery import discover,report
class EvidenceDiscoveryTests(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();self.root=Path(self.t.name)
 def tearDown(self):self.t.cleanup()
 def write(self,rel,obj):
  p=self.root/rel;p.parent.mkdir(parents=True,exist_ok=True)
  p.write_text(json.dumps(obj),encoding="utf-8")
 def test_empty_directory_produces_no_invented_claims(self):
  self.assertEqual(discover(self.root),[])
 def test_d_sandbox_is_never_in_vivo(self):
  self.write("d_sandbox_demo/dashboard_summary.json",{"state":"D_SANDBOX_PASS","candidate_id":"FIX-D-001"})
  x=report(self.root)
  self.assertEqual(x["claims"][0]["proof_type"],"SANDBOX")
  self.assertEqual(x["verification"][0]["verification"],"VERIFIED_ARTIFACTS")
  self.assertFalse(x["production_authority"])
 def test_e_blocked_commissioning_is_a_sandbox_pass_not_commission(self):
  self.write("e_sandbox_demo/dashboard_summary.json",{"state":"E_COMMISSIONING_BLOCKED_TEST_ARTIFACT"})
  x=report(self.root);self.assertEqual(x["claims"][0]["proof_type"],"SANDBOX")
  self.assertFalse(x["commissioning_authority"])
 def test_unknown_state_cannot_claim_pass(self):
  self.write("d_sandbox_demo/dashboard_summary.json",{"state":"D_OOS_PASS"})
  self.assertEqual(discover(self.root)[0]["verdict"],"HOLD")
 def test_discovery_does_not_change_source_bytes(self):
  self.write("d_sandbox_demo/dashboard_summary.json",{"state":"D_SANDBOX_PASS"})
  p=self.root/"d_sandbox_demo/dashboard_summary.json";before=p.read_bytes()
  report(self.root);self.assertEqual(before,p.read_bytes())
 def test_invalid_json_cannot_claim_pass(self):
  p=self.root/"d_sandbox_demo/dashboard_summary.json";p.parent.mkdir(parents=True)
  p.write_text("broken")
  self.assertEqual(discover(self.root)[0]["verdict"],"HOLD")
if __name__=="__main__":unittest.main()
