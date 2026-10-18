"""Executable W6 T01-T03 checks against the historical B v2 checker.
Requires local file ../gate2_build_v03B2/b_v2.py; skips rather than pretending coverage.
No API calls or strategy execution.
"""
import importlib.util,unittest
from pathlib import Path
CHECKER=Path(__file__).resolve().parent.parent/"gate2_build_v03B2"/"b_v2.py"
def load_checker():
 if not CHECKER.is_file():raise unittest.SkipTest("Historical B checker absent; no executable evidence")
 spec=importlib.util.spec_from_file_location("historical_b_v2",CHECKER)
 mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
def candidate():
 return {"candidate_id":"CAND-B-001","evidence_refs":["SRC-A-003"],
         "parameter_ranges":{"atr_period":[10,20]},"required_inputs":["Open","High","Low","Close"],
         "candle_definition":"Body uses abs(Close - Open)"}
class W6HistoricalBExecutable(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.b=load_checker()
 def test_T01_valid_candidate_passes_candidate_checks(self):
  self.assertEqual(self.b.checks(candidate()),[])
 def test_T02_ambiguous_signed_body_is_rejected(self):
  c=candidate();c["candle_definition"]="Body = (Close - Open)"
  self.assertIn("SIGNED_BODY_AMBIGUITY",self.b.checks(c))
 def test_T03_unapproved_evidence_is_rejected(self):
  c=candidate();c["evidence_refs"]=["SRC-X-099"]
  self.assertIn("GROUNDING_FAILURE",self.b.checks(c))
if __name__=="__main__":unittest.main()
