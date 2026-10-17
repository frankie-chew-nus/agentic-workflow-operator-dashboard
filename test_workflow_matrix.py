import unittest
from workflow_matrix import *
class WorkflowMatrixTests(unittest.TestCase):
 def test_legitimate_production_handoffs(self):
  for a in [("A","B","A_PASS"),("B","C","READY_FOR_C"),("C","D","C_PASS"),("D","E","D_OOS_PASS")]:
   self.assertEqual(allowed(*a,PROD),(True,"AUTHORIZED"))
 def test_bad_states_block(self):
  for a in [("A","B","A_FAIL"),("B","C","B_REVIEW"),("C","D","C_FAIL"),("C","D","C_SYSTEM_HOLD"),("D","E","D_OOS_FAIL")]:
   self.assertFalse(allowed(*a,PROD)[0])
 def test_test_evidence_blocked_from_every_production_handoff(self):
  for a in [("A","B","A_PASS"),("B","C","READY_FOR_C"),("C","D","C_PASS"),("D","E","D_OOS_PASS")]:
   self.assertEqual(allowed(*a,TEST)[1],"EVIDENCE_KIND_HOLD")
 def test_authority_identity_hash_and_interruptions_fail_closed(self):
  self.assertFalse(allowed("C","D","C_PASS",PROD,human=False)[0])
  self.assertFalse(allowed("C","D","C_PASS",PROD,identity=False)[0])
  self.assertFalse(allowed("C","D","C_PASS",PROD,hash_ok=False)[0])
  self.assertFalse(allowed("C","D","C_PASS",PROD,interrupted=True)[0])
 def chain(self):
  return [{"stage":"A","state":"A_PASS","kind":PROD,"hash_ok":True,"identity":True},
          {"stage":"B","state":"READY_FOR_C","kind":PROD,"hash_ok":True,"identity":True},
          {"stage":"C","state":"C_PASS","kind":PROD,"hash_ok":True,"identity":True},
          {"stage":"D","state":"D_OOS_PASS","kind":PROD,"hash_ok":True,"identity":True}]
 def test_complete_valid_chain_only_reaches_human_e_decision(self):
  self.assertEqual(commissioning(self.chain()),(True,"E_HUMAN_DECISION_ELIGIBLE"))
  self.assertEqual(commissioning(self.chain(),human=False)[1],"HUMAN_COMMISSIONING_REQUIRED")
 def test_test_artifact_anywhere_blocks_e(self):
  for i in range(4):
   c=self.chain();c[i]=dict(c[i]);c[i]["kind"]=TEST
   self.assertEqual(commissioning(c)[1],"TEST_EVIDENCE_BLOCK")
 def test_tamper_or_identity_mismatch_anywhere_blocks_e(self):
  for field,reason in [("hash_ok","HASH_HOLD"),("identity","IDENTITY_HOLD")]:
   for i in range(4):
    c=self.chain();c[i]=dict(c[i]);c[i][field]=False
    self.assertEqual(commissioning(c)[1],reason)
 def test_wrong_order_and_missing_stage_block_e(self):
  c=self.chain();self.assertEqual(commissioning(c[:-1])[1],"PROVENANCE_CHAIN_HOLD")
  c=self.chain();c[1],c[2]=c[2],c[1];self.assertEqual(commissioning(c)[1],"PROVENANCE_CHAIN_HOLD")
if __name__=="__main__":unittest.main()
