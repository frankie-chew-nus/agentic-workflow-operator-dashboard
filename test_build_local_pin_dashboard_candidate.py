"""Build the real local PIN dashboard copy and assert no active source mutation."""
import tempfile,unittest
from pathlib import Path
from build_local_pin_dashboard_candidate import build
ROOT=Path(__file__).resolve().parent
class CandidateBuildTests(unittest.TestCase):
 def test_copy_contains_local_pin_and_evidence_release(self):
  original=(ROOT/"gate2.py").read_bytes()
  with tempfile.TemporaryDirectory() as td:
   target=Path(td)/"w6_disposable_dashboard"/"gate2.py"
   build(ROOT/"gate2.py",target)
   result=target.read_text(encoding="utf-8")
   compile(result,str(target),"exec")
   self.assertIn('name="pin"',result)
   self.assertIn("from b_local_operator_release import release",result)
   self.assertIn("GATE2_LOCAL_APPROVAL_CONFIG",result)
  self.assertEqual((ROOT/"gate2.py").read_bytes(),original)
if __name__=="__main__":unittest.main()
