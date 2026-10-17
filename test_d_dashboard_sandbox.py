import tempfile,unittest
from pathlib import Path
from d_dashboard_sandbox import execute
class DDashboardSandboxTests(unittest.TestCase):
 def test_dashboard_sandbox_never_has_production_authority(self):
  with tempfile.TemporaryDirectory() as d:
   x=execute(Path(d));self.assertEqual(x["mode"],"WORKFLOW_TEST_SANDBOX")
   self.assertFalse(x["production_authority"]);self.assertFalse(x["advance_to_e_production"])
   self.assertIn("NOT A C PASS",x["warning"])
if __name__=="__main__":unittest.main()
