"""Disposable dashboard source integration checks; no server or SQLite writes."""
import ast,tempfile,unittest
from pathlib import Path
from make_disposable_b_dashboard_guard import make_disposable_copy,ORIGINAL
ROOT=Path(__file__).resolve().parent
class DashboardGuardIntegrationTests(unittest.TestCase):
 def test_disposable_copy_has_guard_and_no_original_release_branch(self):
  with tempfile.TemporaryDirectory() as td:
   folder=Path(td)/"w6_disposable_dashboard"
   dest=make_disposable_copy(ROOT/"gate2.py",folder/"gate2.py")
   code=dest.read_text(encoding="utf-8")
   self.assertNotIn(ORIGINAL,code)
   self.assertIn("release_preflight(candidate_id=cid,research_id=r['id'],verified_context=None)",code)
   self.assertIn("B release blocked:",code)
   self.assertNotIn("elif d=='RELEASE_TO_C':decision(",code)
   ast.parse(code)
 def test_cannot_overwrite_active_dashboard(self):
  with self.assertRaises(ValueError):
   make_disposable_copy(ROOT/"gate2.py",ROOT/"gate2.py")
 def test_unexpected_source_change_fails_closed(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/"source.py";p.write_text("print('no release branch')",encoding="utf-8")
   with self.assertRaises(ValueError):
    make_disposable_copy(p,Path(td)/"w6_disposable_dashboard"/"gate2.py")
if __name__=="__main__":unittest.main()
