"""Integration with copied active b_resume.py and disposable SQLite. No live data."""
import json,shutil,sqlite3,tempfile,unittest
from pathlib import Path
from disposable_b_integration import run_disposable
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/"gate2_operator_app_v1"/"b_resume.py"
class DisposableIntegrationTests(unittest.TestCase):
 def setUp(self):
  if not SOURCE.is_file():self.skipTest("Active B source missing")
  self.temp=tempfile.TemporaryDirectory()
  self.addCleanup(self.temp.cleanup)
  self.base=Path(self.temp.name)/"w6_disposable_fixture"
  self.base.mkdir()
  self.adapter=self.base/"b_resume.py";shutil.copyfile(SOURCE,self.adapter)
  self.db=self.base/"operator.db"
  conn=sqlite3.connect(self.db)
  conn.execute("CREATE TABLE decisions(id TEXT,research_id TEXT,candidate_id TEXT,decision TEXT,rationale TEXT,created_at TEXT)")
  conn.execute("INSERT INTO decisions VALUES(?,?,?,?,?,?)",("SYN","SYN","CAND-B-002","RETURN_TO_B","Synthetic authority","2026-10-20T00:00:00Z"))
  conn.commit();conn.close()
  self.candidate={"candidate_id":"CAND-B-002","version":"v2.1.1","research_domain":"SYN",
   "hypothesis":"SYN","evidence_refs":["SRC-A-003"],"prohibited_dependencies":["Martingale"],
   "parameter_ranges":{"lookback":[5,10]},"required_inputs":["High","Low","Close","ATR"],
   "operator_assumptions":{},"candle_definition":"range","entry_logic":"breakout",
   "exit_logic":"fixed stop","unresolved_questions":[]}
  self.register=self.base/"register.json"
  self.register.write_text(json.dumps({"candidates":[self.candidate]}))
  self.corrected=self.base/"corrected.json"
  self.out=self.base/"output"
 def ctx(self,**kw):
  d={"fixture_only":True,"policy_status":"SYNTHETIC_TEST_ONLY",
   "available_resources":{"OHLC","ATR"},"approved_dependencies":{"stdlib","numpy"},"released_count":0}
  d.update(kw);return d
 def run_case(self,extra=None,ctx=None):
  c=dict(self.candidate);c.update(extra or {})
  self.corrected.write_text(json.dumps(c))
  return run_disposable(c,ctx or self.ctx(),adapter=self.adapter,db=self.db,
    register=self.register,output_dir=self.out,corrected_candidate=self.corrected)
 def test_T04_blocks_before_adapter(self):
  r=self.run_case({"required_resources":["MISSING_LIB"]})
  self.assertEqual(r["state"],"GOVERNANCE_HOLD");self.assertFalse(r["adapter_executed"])
 def test_T05_blocks_before_adapter(self):
  r=self.run_case({"dependencies":["OPAQUE_REMOTE"]})
  self.assertEqual(r["state"],"GOVERNANCE_HOLD");self.assertFalse(r["adapter_executed"])
 def test_T09_blocks_before_adapter(self):
  r=self.run_case(ctx=self.ctx(released_count=3))
  self.assertEqual(r["state"],"GOVERNANCE_HOLD");self.assertFalse(r["adapter_executed"])
 def test_T10_blocks_before_adapter(self):
  r=self.run_case({"governance_rule_change":{"actor":"AI"}})
  self.assertEqual(r["state"],"GOVERNANCE_HOLD");self.assertFalse(r["adapter_executed"])
 def test_valid_fixture_reaches_copied_adapter_only(self):
  r=self.run_case({"required_resources":["OHLC"],"dependencies":["numpy"]})
  self.assertEqual(r["state"],"B_RESUME_TEST_ONLY");self.assertTrue(r["adapter_executed"])
  self.assertTrue((self.out/"b_corrected_release.json").exists())
  self.assertFalse(r["production_authority"])
if __name__=="__main__":unittest.main()
