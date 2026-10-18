"""W6 B->C governance implementation coverage audit.

This is a coverage audit, not a simulation of the external B checker.
A passing audit test does not imply the corresponding W6 scenario passes.
"""
import ast,json,unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parent
SCENARIOS={
 "T01":"ordinary release","T02":"ambiguous specification",
 "T03":"unapproved source reference","T04":"unavailable resource",
 "T05":"prohibited black-box dependency",
}
def audit():
 tree=ast.parse((ROOT/"gate2.py").read_text(encoding="utf-8"))
 functions={n.name for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
 contract=json.loads((ROOT/"b002_revision_contract.json").read_text(encoding="utf-8"))
 rules={r["id"] for r in contract["rules"]}
 return {
  "scope":"DASHBOARD_AND_CONTRACT_ONLY",
  "external_b_adapter_inspected":False,
  "findings":{
   "T01":{"status":"PARTIAL","basis":"workflow_matrix.allowed checks READY_FOR_C; dashboard has RELEASE_TO_C action"},
   "T02":{"status":"NOT_VERIFIED","basis":"contract rules alone do not prove ambiguity checker execution"},
   "T03":{"status":"NOT_VERIFIED","basis":"A_ONLY and EVIDENCE are declared; external checker not inspected"},
   "T04":{"status":"NOT_VERIFIED","basis":"resource availability enforcement not established"},
   "T05":{"status":"NOT_VERIFIED","basis":"DEPENDENCIES declared; external checker not inspected"},
  },
  "observed_functions":sorted(x for x in functions if x in ("b_flow_cmd","sync_b_authority_to_existing_workflow","deterministic_b_patch_from_failed_rules")),
  "declared_contract_rules":sorted(rules),
  "production_authority":False,
 }
class W6ImplementationAudit(unittest.TestCase):
 def test_contract_declares_evidence_and_dependency_rules(self):
  x=audit();self.assertIn("EVIDENCE",x["declared_contract_rules"]);self.assertIn("DEPENDENCIES",x["declared_contract_rules"])
 def test_external_checker_not_falsely_claimed_verified(self):
  x=audit();self.assertFalse(x["external_b_adapter_inspected"])
  for t in ("T02","T03","T04","T05"):self.assertEqual(x["findings"][t]["status"],"NOT_VERIFIED")
 def test_real_dashboard_adapter_hook_exists(self):
  self.assertIn("b_flow_cmd",audit()["observed_functions"])
if __name__=="__main__":
 unittest.main()
