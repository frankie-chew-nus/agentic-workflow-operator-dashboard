"""W6 T09/T10 executable negative tests against the existing B->C transition guard.
These intentionally fail if the guard authorizes a fourth candidate or an unauthorized rule change.
Scope is workflow_matrix.allowed, not a claim about the entire external B adapter.
"""
import unittest
from workflow_matrix import allowed,PROD

class W6T09T10Enforcement(unittest.TestCase):
 def test_T09_fourth_candidate_must_not_auto_release(self):
  # Three earlier releases in same commission; transition guard receives only state/kind.
  prior_releases=3
  self.assertEqual(prior_releases,3)
  authorized,reason=allowed("B","C","READY_FOR_C",PROD,human=True)
  self.assertFalse(authorized,"T09 GAP: fourth candidate authorized without commission-level limit check")

 def test_T10_ai_rule_change_must_not_authorize_release(self):
  # Synthetic attempt to change acceptance policy; guard receives no actor/policy version.
  actor="AI_AGENT";unauthorized_rule_change=True
  self.assertEqual((actor,unauthorized_rule_change),("AI_AGENT",True))
  authorized,reason=allowed("B","C","READY_FOR_C",PROD,human=True)
  self.assertFalse(authorized,"T10 GAP: release guard cannot distinguish unauthorized rule change")

if __name__=="__main__":unittest.main()
