"""T04/T05/T09/T10 isolated integration tests; no production adapter or DB access."""
import unittest
from isolated_b_policy_harness import evaluate

class IsolatedBPolicyTests(unittest.TestCase):
 def context(self,**kw):
  c={"available_resources":{"OHLC"},"approved_dependencies":{"stdlib"},"released_count":0}
  c.update(kw);return c
 def test_T04_unavailable_resource(self):
  r=evaluate({"required_resources":["LIBRARY_Z"]},self.context())
  self.assertEqual(r["state"],"GOVERNANCE_HOLD")
  self.assertIn("RESOURCE_UNAVAILABLE:LIBRARY_Z",r["failures"])
 def test_T05_opaque_dependency(self):
  r=evaluate({"dependencies":["BLACK_BOX"]},self.context())
  self.assertIn("DEPENDENCY_NOT_APPROVED:BLACK_BOX",r["failures"])
 def test_T09_fourth_candidate(self):
  r=evaluate({},self.context(released_count=3))
  self.assertIn("COMMISSION_LIMIT_REACHED",r["failures"])
 def test_T10_unauthorized_rule_change(self):
  r=evaluate({"governance_rule_change":{"actor":"AI_AGENT"}},self.context())
  self.assertIn("UNAUTHORIZED_RULE_CHANGE",r["failures"])
 def test_missing_trusted_context_fail_closed(self):
  self.assertEqual(evaluate({},None)["state"],"GOVERNANCE_HOLD")
 def test_positive_candidate_not_auto_released(self):
  r=evaluate({"required_resources":["OHLC"],"dependencies":["stdlib"]},self.context())
  self.assertEqual(r["state"],"ELIGIBLE_FOR_EXISTING_B_CHECKS")
  self.assertFalse(r["production_authority"])
if __name__=="__main__":unittest.main()
