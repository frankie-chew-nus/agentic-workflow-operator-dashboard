"""T04/T05/T09/T10 synthetic preflight integration, no active B adapter touched."""
import unittest
from isolated_b_preflight_adapter import preflight
class PreflightTests(unittest.TestCase):
 def ctx(self,**updates):
  d={"fixture_only":True,"policy_status":"SYNTHETIC_TEST_ONLY",
     "available_resources":{"OHLC","ATR"},"approved_dependencies":{"stdlib","numpy","pandas"},
     "released_count":0}
  d.update(updates);return d
 def test_T04_missing_resource_holds(self):
  self.assertIn("RESOURCE_UNAVAILABLE:PREVIOUS_DAY_OHLC",preflight({"required_resources":["PREVIOUS_DAY_OHLC"]},self.ctx())["failures"])
 def test_T05_opaque_dependency_holds(self):
  self.assertIn("DEPENDENCY_NOT_APPROVED:remote_black_box",preflight({"dependencies":["remote_black_box"]},self.ctx())["failures"])
 def test_T09_fourth_release_holds(self):
  self.assertIn("COMMISSION_LIMIT_REACHED",preflight({},self.ctx(released_count=3))["failures"])
 def test_T10_rule_change_holds(self):
  self.assertIn("UNAUTHORIZED_RULE_CHANGE",preflight({"governance_rule_change":{"max_released_candidates":99}},self.ctx())["failures"])
 def test_untrusted_context_holds(self):
  self.assertEqual(preflight({},{"released_count":0})["state"],"GOVERNANCE_HOLD")
 def test_missing_count_holds(self):
  self.assertIn("RELEASE_COUNT_UNVERIFIED",preflight({},self.ctx(released_count=None))["failures"])
 def test_valid_fixture_cannot_grant_release(self):
  r=preflight({"required_resources":["OHLC"],"dependencies":["numpy"]},self.ctx())
  self.assertEqual(r["state"],"PREFLIGHT_PASS_TEST_ONLY")
  self.assertFalse(r["production_authority"])
if __name__=="__main__":unittest.main()
