"""Active B resume boundary integration tests: disposable SQLite and synthetic fixtures.

These tests intentionally expose missing policy enforcement, without changing production
code or touching real workflow evidence. The adapter remains outside this repository.
Run: py -m unittest test_w6_active_b_governance -v
"""
import json,sqlite3,subprocess,sys,tempfile,unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parent
ADAPTER=ROOT.parent/"gate2_operator_app_v1"/"b_resume.py"
CID="CAND-B-002"

class ActiveBTests(unittest.TestCase):
 def setUp(self):
  if not ADAPTER.is_file():self.skipTest("Active adapter missing: "+str(ADAPTER))
  self.tmp=tempfile.TemporaryDirectory()
  self.addCleanup(self.tmp.cleanup)
  self.base=Path(self.tmp.name)
  self.db=self.base/"operator.db"
  con=sqlite3.connect(self.db)
  con.execute("CREATE TABLE decisions(id TEXT,research_id TEXT,candidate_id TEXT,decision TEXT,rationale TEXT,created_at TEXT)")
  con.execute("INSERT INTO decisions VALUES(?,?,?,?,?,?)",("DEC-SYN","RESEARCH-SYN",CID,"RETURN_TO_B","Synthetic review","2026-10-19T00:00:00+00:00"))
  con.commit();con.close()
  self.parent={"candidate_id":CID,"version":"v2.1.1","research_domain":"synthetic",
   "hypothesis":"synthetic rule","evidence_refs":["SRC-A-003"],
   "prohibited_dependencies":["Martingale","Grid","Black-box"],
   "parameter_ranges":{"lookback":[5,10]},"required_inputs":["Open","High","Low","Close"],
   "operator_assumptions":{},"candle_definition":"range","entry_logic":"breakout",
   "exit_logic":"fixed stop","unresolved_questions":[]}
  self.reg=self.base/"register.json"
  self.reg.write_text(json.dumps({"candidates":[self.parent]}),encoding="utf-8")
 def invoke(self,changes):
  cand=dict(self.parent);cand.update(changes)
  cp=self.base/"corrected.json";cp.write_text(json.dumps(cand),encoding="utf-8")
  out=self.base/"output"
  proc=subprocess.run([sys.executable,str(ADAPTER),"--db",str(self.db),"--register",str(self.reg),
   "--candidate",CID,"--corrected-candidate",str(cp),"--output-dir",str(out)],
   cwd=self.base,text=True,capture_output=True)
  return proc,(out/"b_resume_validation.json"),(out/"b_corrected_release.json")
 def assert_hold(self,changes,label):
  proc,hold,release=self.invoke(changes)
  self.assertEqual(proc.returncode,2,label+": expected governance HOLD")
  self.assertTrue(hold.exists(),label+": no HOLD evidence")
  self.assertFalse(release.exists(),label+": corrected release unexpectedly written")
 def test_T04_unavailable_resource_must_hold(self):
  self.assert_hold({"required_resources":["UNAVAILABLE_SYNTHETIC_LIBRARY_Z"]},"T04")
 def test_T05_opaque_dependency_must_hold(self):
  self.assert_hold({"dependencies":["OPAQUE_EXTERNAL_PREDICTION_SERVICE"]},"T05")
 def test_T09_fourth_candidate_must_hold(self):
  # Synthetic count is a distinct field; adapter has no commission count contract.
  self.assert_hold({"research_commission_release_count":3},"T09")
 def test_T10_unauthorized_governance_rule_change_must_hold(self):
  self.assert_hold({"governance_rule_change":{"actor":"AI_AGENT","new_candidate_limit":999}},"T10")

if __name__=="__main__":unittest.main()
