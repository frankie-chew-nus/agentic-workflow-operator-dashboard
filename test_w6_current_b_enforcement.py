"""Isolated negative tests of actual b_resume.py B return/resume boundary.
Uses temporary SQLite, synthetic candidate files and subprocess; no provider or production data.
The tests FAIL if T04/T05/T09/T10 governance controls are missing.
"""
import json,sqlite3,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SCRIPT=ROOT.parent/"gate2_operator_app_v1"/"b_resume.py"

class W6CurrentBEnforcement(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  if not SCRIPT.is_file():raise unittest.SkipTest("Current B resume script unavailable; cannot verify")
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
  self.p=Path(self.temp.name)
  self.db=self.p/"operator.db";self.reg=self.p/"register.json";self.corrected=self.p/"candidate.json"
  c=sqlite3.connect(self.db)
  c.execute("CREATE TABLE decisions(id TEXT,research_id TEXT,candidate_id TEXT,decision TEXT,rationale TEXT,created_at TEXT)")
  c.execute("INSERT INTO decisions VALUES(?,?,?,?,?,?)",("DEC-1","R-1","CAND-B-002","RETURN_TO_B","Human correction approved","2026-10-18T00:00:00Z"))
  c.commit();c.close()
  self.base={"candidate_id":"CAND-B-002","version":"v2.1.1","research_domain":"Synthetic domain",
   "hypothesis":"Synthetic hypothesis","evidence_refs":["SRC-A-003"],"operator_assumptions":{},
   "candle_definition":"Synthetic candle","entry_logic":"Synthetic entry","exit_logic":"Synthetic exit",
   "parameter_ranges":{"lookback":[5,10]},"required_inputs":["Open","High","Low","Close"],
   "prohibited_dependencies":["Martingale","Grid","Black-box"],"unresolved_questions":[]}
  self.reg.write_text(json.dumps({"candidates":[self.base]}),encoding="utf-8")
 def run_case(self,changes=None,extra_candidates=None):
  candidate=dict(self.base);candidate["version"]="v2.1.2";candidate.update(changes or {})
  self.corrected.write_text(json.dumps(candidate),encoding="utf-8")
  if extra_candidates:
   self.reg.write_text(json.dumps({"candidates":[self.base]+extra_candidates}),encoding="utf-8")
  cmd=[sys.executable,str(SCRIPT),"--db",str(self.db),"--register",str(self.reg),
   "--candidate","CAND-B-002","--corrected-candidate",str(self.corrected),"--output-dir",str(self.p/"out")]
  result=subprocess.run(cmd,cwd=self.p,capture_output=True,text=True,timeout=20)
  output=self.p/"out"/"b_corrected_release.json"
  return result,output
 def assert_hold(self,result,output,label):
  self.assertFalse(output.exists(),label+": B corrected release was written")
  self.assertNotEqual(result.returncode,0,label+": expected governance HOLD")
 def test_T04_unavailable_required_resource_holds(self):
  r,o=self.run_case({"required_resources":["unavailable_test_library_z"]})
  self.assert_hold(r,o,"T04")
 def test_T05_opaque_dependency_holds(self):
  r,o=self.run_case({"dependencies":["opaque_external_prediction_service"]})
  self.assert_hold(r,o,"T05")
 def test_T09_fourth_candidate_holds(self):
  extra=[dict(self.base,candidate_id="CAND-B-001"),dict(self.base,candidate_id="CAND-B-003"),
         dict(self.base,candidate_id="CAND-B-004")]
  r,o=self.run_case(extra_candidates=extra)
  self.assert_hold(r,o,"T09")
 def test_T10_unauthorized_policy_change_holds(self):
  r,o=self.run_case({"governance_rule_change":{"actor":"AI_AGENT","max_candidates":999}})
  self.assert_hold(r,o,"T10")

if __name__=="__main__":unittest.main()
