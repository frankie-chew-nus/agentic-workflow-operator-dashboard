"""Unit tests for proposed fail-closed B policy; not yet active-adapter integration."""
import unittest
from b_boundary_policy_v1 import validate_boundary
class BBoundaryPolicyTests(unittest.TestCase):
 def check(self,candidate,**kw):
  return validate_boundary(candidate,available_resources={"OHLC"},approved_dependencies={"stdlib"},released_count=0,**kw)
 def test_T04_missing_resource(self):
  self.assertIn("RESOURCE_UNAVAILABLE:LIBRARY_Z",self.check({"required_resources":["LIBRARY_Z"]}))
 def test_T05_opaque_dependency(self):
  self.assertIn("DEPENDENCY_NOT_APPROVED:BLACK_BOX",self.check({"dependencies":["BLACK_BOX"]}))
 def test_T09_fourth_candidate(self):
  self.assertIn("COMMISSION_LIMIT_REACHED",validate_boundary({},available_resources=set(),approved_dependencies=set(),released_count=3))
 def test_T09_candidate_supplied_count_is_untrusted(self):
  self.assertIn("UNTRUSTED_COMMISSION_COUNT",self.check({"research_commission_release_count":3}))
 def test_T10_ai_rule_change(self):
  self.assertIn("UNAUTHORIZED_RULE_CHANGE",self.check({"governance_rule_change":{"actor":"AI_AGENT"}}))
 def test_fail_closed_without_inventories(self):
  f=validate_boundary({},available_resources=None,approved_dependencies=None,released_count=None)
  self.assertIn("RESOURCE_INVENTORY_UNAVAILABLE",f)
  self.assertIn("DEPENDENCY_ALLOWLIST_UNAVAILABLE",f)
  self.assertIn("RELEASE_COUNT_UNVERIFIED",f)
 def test_ordinary_candidate(self):
  self.assertEqual(self.check({"required_resources":["OHLC"],"dependencies":["stdlib"]}),[])
if __name__=="__main__":unittest.main()
