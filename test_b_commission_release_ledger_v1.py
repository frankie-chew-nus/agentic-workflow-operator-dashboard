"""T09 synthetic commission ledger tests; no actual Human decisions asserted."""
import unittest
from b_commission_release_ledger_v1 import validate_ledger
class LedgerTests(unittest.TestCase):
 def ledger(self,n=0):
  return {"schema":"COMMISSION_LEDGER_V1","commission_id":"SYN-COMMISSION",
   "status":"VERIFIED_BY_OPERATOR",
   "releases":[{"candidate_id":f"SYN-{i}","human_decision_id":f"SYN-DEC-{i}",
    "release_artifact_sha256":"a"*64} for i in range(n)]}
 def test_T09_fourth_candidate_blocked(self):
  l=self.ledger(3)
  f=validate_ledger(l,"SYN-COMMISSION","SYN-4",verified_decision_ids={f"SYN-DEC-{i}" for i in range(3)})
  self.assertIn("COMMISSION_LIMIT_REACHED",f)
 def test_T09_two_releases_can_be_evaluated(self):
  l=self.ledger(2)
  self.assertEqual(validate_ledger(l,"SYN-COMMISSION","SYN-3",verified_decision_ids={"SYN-DEC-0","SYN-DEC-1"}),[])
 def test_T09_unverified_decision_blocks(self):
  self.assertIn("HUMAN_DECISION_NOT_VERIFIED",validate_ledger(self.ledger(1),"SYN-COMMISSION","SYN-2"))
 def test_T09_unverified_ledger_blocks(self):
  l=self.ledger();l["status"]="DRAFT"
  self.assertIn("LEDGER_NOT_VERIFIED",validate_ledger(l,"SYN-COMMISSION","SYN-1",verified_decision_ids=set()))
 def test_T09_duplicate_release_blocks(self):
  l=self.ledger(1);l["releases"].append(dict(l["releases"][0]))
  self.assertIn("DUPLICATE_CANDIDATE_RELEASE",validate_ledger(l,"SYN-COMMISSION","SYN-2",verified_decision_ids={"SYN-DEC-0"}))
 def test_T09_wrong_commission_blocks(self):
  self.assertIn("COMMISSION_ID_MISMATCH",validate_ledger(self.ledger(),"OTHER","SYN-1",verified_decision_ids=set()))
 def test_T09_missing_history_blocks(self):
  l=self.ledger();del l["releases"]
  self.assertIn("RELEASE_HISTORY_MISSING",validate_ledger(l,"SYN-COMMISSION","SYN-1",verified_decision_ids=set()))
if __name__=="__main__":unittest.main()
