import unittest
from pathlib import Path
class DashboardObservabilityTests(unittest.TestCase):
 def test_c_d_e_governance_checks_visible(self):
  s=Path("gate2.py").read_text(encoding="utf-8")
  for x in ["C governance status","Stage 1 evidence resolved","Execution equivalence validated","Production D authorization","PRODUCTION D GATE checks","PRODUCTION E GATE checks","Human final decision required"]:
   self.assertIn(x,s)
 def test_check_renderer_has_pass_hold_states(self):
  s=Path("gate2.py").read_text(encoding="utf-8")
  self.assertIn("'PASS' if ok else 'HOLD'",s)
if __name__=="__main__":unittest.main()
