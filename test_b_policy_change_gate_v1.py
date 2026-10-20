"""T10 synthetic Human-only policy-change gate tests; no real approval implied."""
import unittest
from b_policy_change_gate_v1 import authorize_change,digest
class PolicyChangeTests(unittest.TestCase):
 def setUp(self):
  self.old={"production_authority":False,"max_released_candidates":3,"revision":1}
  self.new={**self.old,"revision":2}
  self.decision={"actor_type":"HUMAN_OPERATOR","decision_id":"SYN-DEC",
   "decision":"APPROVE_POLICY_CHANGE",
   "previous_policy_sha256":digest(self.old),"proposed_policy_sha256":digest(self.new)}
 def check(self,decision=None,proposed=None,**kw):
  return authorize_change(self.old,self.new if proposed is None else proposed,
   self.decision if decision is None else decision,
   trusted_decision_ids=kw.get("trusted_decision_ids",{"SYN-DEC"}),
   trusted_previous_digest=kw.get("trusted_previous_digest",digest(self.old)))
 def test_T10_synthetic_valid_shape(self):
  self.assertEqual(self.check(),[])
 def test_T10_ai_actor_denied(self):
  self.assertIn("NON_HUMAN_ACTOR",self.check({**self.decision,"actor_type":"AI_AGENT"}))
 def test_T10_unregistered_decision_denied(self):
  self.assertIn("DECISION_NOT_IN_TRUSTED_REGISTER",self.check(trusted_decision_ids=set()))
 def test_T10_tampered_proposal_denied(self):
  self.assertIn("PROPOSED_POLICY_HASH_MISMATCH",self.check(proposed={**self.new,"revision":3}))
 def test_T10_unverified_prior_policy_denied(self):
  self.assertIn("PRIOR_POLICY_UNVERIFIED",self.check(trusted_previous_digest="0"*64))
 def test_T10_candidate_limit_expansion_denied(self):
  x={**self.new,"max_released_candidates":4}
  self.assertIn("COMMISSION_LIMIT_CHANGE_FORBIDDEN",self.check(proposed=x))
 def test_T10_production_authority_denied(self):
  self.assertIn("PRODUCTION_AUTHORITY_FORBIDDEN",self.check(proposed={**self.new,"production_authority":True}))
if __name__=="__main__":unittest.main()
