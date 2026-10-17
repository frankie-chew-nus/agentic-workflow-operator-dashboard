import unittest
from gate2 import action_authorized
class DashboardAdversarialTests(unittest.TestCase):
 def test_hidden_button_post_cannot_skip_c_to_d(self):
  for st in ["C_STAGE1_REVIEW_REQUIRED","C_FAIL","C_SYSTEM_HOLD","B_REVIEW"]:
   self.assertFalse(action_authorized(st,"START_PRODUCTION_D"))
 def test_hidden_button_post_cannot_skip_d_to_e(self):
  for st in ["C_PASS","C_FAIL","D_OOS_FAIL","D_GOVERNANCE_HOLD"]:
   self.assertFalse(action_authorized(st,"START_PRODUCTION_E"))
 def test_c_actions_require_exact_states(self):
  self.assertTrue(action_authorized("C_STAGE1_REVIEW_REQUIRED","RUN_C_STAGE1_EQUIVALENCE"))
  self.assertFalse(action_authorized("C_FAIL","RUN_C_STAGE1_EQUIVALENCE"))
  self.assertTrue(action_authorized("C_PREP_PATH_APPROVED","START_GOVERNED_C"))
  self.assertFalse(action_authorized("B_REVIEW","START_GOVERNED_C"))
 def test_b_release_requires_review(self):
  self.assertTrue(action_authorized("B_REVIEW","RELEASE_TO_C"))
  self.assertFalse(action_authorized("GOVERNANCE_HOLD","RELEASE_TO_C"))
 def test_unknown_action_fails_closed(self):
  self.assertFalse(action_authorized("C_PASS","INVENTED_BYPASS"))
if __name__=="__main__":unittest.main()
