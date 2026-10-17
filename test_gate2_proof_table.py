import json,tempfile,unittest
from pathlib import Path
from gate2_proof_table import proof_rows,csv_text
class Gate2ProofTableTests(unittest.TestCase):
 def test_sandbox_cannot_be_presented_as_empirical(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/"d_sandbox_demo/dashboard_summary.json";p.parent.mkdir(parents=True)
   p.write_text(json.dumps({"state":"D_SANDBOX_PASS","candidate_id":"FIX-D-001"}))
   x=proof_rows(t)[0]
   self.assertEqual(x["proof_type"],"SANDBOX")
   self.assertIn("not trading performance",x["limitations"])
 def test_c_completion_is_incomplete_not_qualification(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)/"c_runs/CAND-B-002/v2.1.3/stage1_output/summary.json";p.parent.mkdir(parents=True)
   p.write_text(json.dumps({"state":"STAGE1_COMPLETE","classification":"EXECUTION_EVIDENCE_ONLY_NO_PERFORMANCE_PASS","variant_count":54}))
   x=proof_rows(t)[0];self.assertEqual(x["proof_type"],"INCOMPLETE")
   self.assertEqual(x["n"],54);self.assertIn("Incomplete proof",x["limitations"])
 def test_empty_registry_produces_only_csv_header(self):
  with tempfile.TemporaryDirectory() as t:
   self.assertEqual(len(csv_text(t).splitlines()),1)
if __name__=="__main__":unittest.main()
