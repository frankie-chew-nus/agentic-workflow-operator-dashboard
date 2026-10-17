import json,sqlite3,tempfile,unittest
from pathlib import Path
from evidence_c_discovery import discover_c,discover_decisions
class CEvidenceDiscoveryTests(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();self.root=Path(self.t.name)
 def tearDown(self):self.t.cleanup()
 def test_completed_execution_is_not_strategy_pass(self):
  p=self.root/"c_runs/CAND-B-002/v2.1.3/stage1_output/summary.json"
  p.parent.mkdir(parents=True);p.write_text(json.dumps({"state":"STAGE1_COMPLETE","classification":"EXECUTION_EVIDENCE_ONLY_NO_PERFORMANCE_PASS","variant_count":54}))
  x=discover_c(self.root)[0];self.assertEqual(x["n"],54);self.assertEqual(x["proof_type"],"INCOMPLETE");self.assertNotEqual(x["verdict"],"PASS")
 def test_equivalence_pass_label_does_not_upgrade_proof(self):
  p=self.root/"c_runs/CAND-B-002/v2.1.3/stage1_equivalence.json";p.parent.mkdir(parents=True)
  p.write_text(json.dumps({"state":"C_STAGE1_EXECUTION_EQUIVALENCE_PASS","comparisons":4}))
  x=discover_c(self.root)[0];self.assertEqual(x["verdict"],"INCOMPLETE")
 def test_missing_c_evidence_yields_no_claims(self):
  self.assertEqual(discover_c(self.root),[])
 def test_decisions_read_only(self):
  p=self.root/"operator.db";con=sqlite3.connect(p)
  con.execute("CREATE TABLE decisions(id TEXT,candidate_id TEXT,decision TEXT,rationale TEXT,created_at TEXT)")
  con.execute("INSERT INTO decisions VALUES('DEC-1','CAND-B-002','ACK_C_REVIEW','reviewed','2026-10-17')")
  con.commit();con.close();before=p.read_bytes()
  x=discover_decisions(self.root)
  self.assertEqual(len(x),1);self.assertEqual(x[0]["observed"],"ACK_C_REVIEW")
  self.assertEqual(x[0]["verdict"],"INCOMPLETE");self.assertEqual(p.read_bytes(),before)
 def test_no_ledger_is_not_invented(self):
  self.assertEqual(discover_decisions(self.root),[])
if __name__=="__main__":unittest.main()
