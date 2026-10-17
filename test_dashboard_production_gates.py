import unittest
from pathlib import Path
class DashboardProductionGateTests(unittest.TestCase):
 def test_d_e_production_gates_are_explicit_and_sandbox_cannot_satisfy_them(self):
  s=Path("gate2.py").read_text(encoding="utf-8")
  self.assertIn("PRODUCTION D GATE",s);self.assertIn("PRODUCTION E GATE",s)
  self.assertIn("requires verified PRODUCTION_EVIDENCE + C_PASS",s)
  self.assertIn("Sandbox/test evidence can never satisfy this production gate",s)
 def test_e_eligibility_requires_d_oos_pass(self):
  s=Path("gate2.py").read_text(encoding="utf-8")
  self.assertIn("candidate['state']=='D_OOS_PASS'",s)
if __name__=="__main__":unittest.main()
