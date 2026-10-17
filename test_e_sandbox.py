import json,tempfile,unittest
from pathlib import Path
from operator_handoff import TEST,PRODUCTION,envelope
from e_sandbox import audit
class ESandboxTests(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();self.r=Path(self.t.name);self.d=self.r/"d.json";self.d.write_text('{"state":"D_SANDBOX_PASS"}')
  self.h=envelope("D","FIX-D-001","v0",TEST,[("d_summary",self.d)],"D_SANDBOX_PASS")
 def tearDown(self):self.t.cleanup()
 def test_test_d_pass_is_explicitly_blocked(self):
  x=audit(self.h,["D_REVIEW"],["D_REVIEW"],self.r/"e.json")
  self.assertEqual(x["state"],"E_COMMISSIONING_BLOCKED_TEST_ARTIFACT");self.assertFalse(x["commissioned"]);self.assertFalse(x["commissioning_authority"])
 def test_tampered_d_evidence_holds(self):
  self.d.write_text("tampered");self.assertEqual(audit(self.h,[],[],self.r/"e.json")["state"],"E_SANDBOX_HOLD")
 def test_missing_human_decision_recorded(self):
  x=audit(self.h,["D_REVIEW"],[],self.r/"e.json");self.assertFalse(x["checks"]["required_human_decisions_present"]);self.assertFalse(x["commissioned"])
 def test_production_evidence_not_accepted_by_sandbox(self):
  h=dict(self.h);h["evidence_kind"]=PRODUCTION
  self.assertEqual(audit(h,[],[],self.r/"e.json")["state"],"E_SANDBOX_HOLD")
if __name__=="__main__":unittest.main()
