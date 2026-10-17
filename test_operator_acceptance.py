import unittest
from operator_acceptance import run,chain
from e_governance import audit
from workflow_matrix import TEST
class OperatorAcceptanceTests(unittest.TestCase):
 def test_complete_a_e_journey_reaches_human_e_only(self):
  x=run();self.assertEqual(x["state"],"OPERATOR_ACCEPTANCE_PASS")
  self.assertTrue(all(t["pass"] for t in x["transitions"]))
  self.assertEqual(x["e"]["state"],"E_HUMAN_DECISION_ELIGIBLE")
  self.assertFalse(x["e"]["commissioned"]);self.assertFalse(x["e"]["automatic_commissioning"])
 def test_test_contamination_blocks_acceptance_chain(self):
  c=chain();c[2]=dict(c[2]);c[2]["kind"]=TEST
  self.assertEqual(audit(c,["A_REVIEW","B_RELEASE","C_REVIEW","D_REVIEW"],["A_REVIEW","B_RELEASE","C_REVIEW","D_REVIEW"])["state"],"E_GOVERNANCE_HOLD")
 def test_missing_d_review_blocks_e(self):
  self.assertEqual(audit(chain(),["A_REVIEW","B_RELEASE","C_REVIEW"],["A_REVIEW","B_RELEASE","C_REVIEW","D_REVIEW"])["state"],"E_GOVERNANCE_HOLD")
if __name__=="__main__":unittest.main()
