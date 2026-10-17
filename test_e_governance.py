import unittest
from workflow_matrix import PROD,TEST
from e_governance import audit
class EGovernanceTests(unittest.TestCase):
 def chain(self):
  return [{"stage":"A","state":"A_PASS","kind":PROD,"hash_ok":True,"identity":True,"candidate_id":"X","version":"v1"},
   {"stage":"B","state":"READY_FOR_C","kind":PROD,"hash_ok":True,"identity":True,"candidate_id":"X","version":"v1"},
   {"stage":"C","state":"C_PASS","kind":PROD,"hash_ok":True,"identity":True,"candidate_id":"X","version":"v1"},
   {"stage":"D","state":"D_OOS_PASS","kind":PROD,"hash_ok":True,"identity":True,"candidate_id":"X","version":"v1"}]
 def test_valid_chain_only_offers_human_decision(self):
  x=audit(self.chain(),["A_REVIEW","B_RELEASE","C_REVIEW","D_REVIEW"],["A_REVIEW","B_RELEASE","C_REVIEW","D_REVIEW"])
  self.assertEqual(x["state"],"E_HUMAN_DECISION_ELIGIBLE");self.assertFalse(x["commissioned"]);self.assertFalse(x["automatic_commissioning"]);self.assertTrue(x["human_final_decision_required"])
 def test_missing_human_decision_holds(self):
  self.assertEqual(audit(self.chain(),[],["D_REVIEW"])["state"],"E_GOVERNANCE_HOLD")
 def test_test_evidence_anywhere_holds(self):
  for i in range(4):
   c=self.chain();c[i]=dict(c[i]);c[i]["kind"]=TEST;self.assertEqual(audit(c,[],[])["state"],"E_GOVERNANCE_HOLD")
 def test_hash_tamper_anywhere_holds(self):
  for i in range(4):
   c=self.chain();c[i]=dict(c[i]);c[i]["hash_ok"]=False;self.assertEqual(audit(c,[],[])["state"],"E_GOVERNANCE_HOLD")
 def test_identity_discontinuity_holds(self):
  c=self.chain();c[2]=dict(c[2]);c[2]["version"]="v2";self.assertEqual(audit(c,[],[])["state"],"E_GOVERNANCE_HOLD")
 def test_fail_or_hold_state_blocks(self):
  for i,bad in [(2,"C_FAIL"),(2,"C_SYSTEM_HOLD"),(3,"D_OOS_FAIL"),(3,"D_GOVERNANCE_HOLD")]:
   c=self.chain();c[i]=dict(c[i]);c[i]["state"]=bad;self.assertEqual(audit(c,[],[])["state"],"E_GOVERNANCE_HOLD")
 def test_missing_or_reordered_provenance_holds(self):
  self.assertEqual(audit(self.chain()[:-1],[],[])["state"],"E_GOVERNANCE_HOLD")
  c=self.chain();c[1],c[2]=c[2],c[1];self.assertEqual(audit(c,[],[])["state"],"E_GOVERNANCE_HOLD")
if __name__=="__main__":unittest.main()
