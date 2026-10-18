"""W6 T04/T05 negative enforcement tests against historical B checker.
Expected to FAIL when enforcement is missing; no strategy or production changes.
"""
import importlib.util,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
def load(path,name):
 if not path.is_file():raise unittest.SkipTest("Historical checker absent: "+str(path))
 spec=importlib.util.spec_from_file_location(name,path)
 mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
class W6T04T05Enforcement(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.b=load(ROOT/"gate2_build_v03B2"/"b_v2.py","historical_b_v2")
 def candidate(self):
  return {"candidate_id":"CAND-B-001","evidence_refs":["SRC-A-003"],
   "parameter_ranges":{"atr_period":[10,20]},"required_inputs":["Open","High","Low","Close"],
   "candle_definition":"abs(Close - Open)"}
 def test_T04_missing_required_resource_must_hold(self):
  c=self.candidate();c["required_resources"]=["unavailable_test_library_z"]
  self.assertTrue(self.b.checks(c),"T04 GAP: missing resource accepted by historical checker")
 def test_T05_prohibited_black_box_must_hold(self):
  c=self.candidate();c["dependencies"]=["opaque_external_prediction_service"]
  c["prohibited_dependencies"]=["Martingale","Grid","Black-box"]
  self.assertTrue(self.b.checks(c),"T05 GAP: black-box dependency accepted by historical checker")
if __name__=="__main__":unittest.main()
