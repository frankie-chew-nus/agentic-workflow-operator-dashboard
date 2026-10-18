"""W6 T06-T10 executable transition tests and explicit coverage limitations.
Tests exercise existing workflow_matrix.allowed; no production authority changes.
A PASS here does not establish full historical W6.2 scenario enforcement.
"""
import unittest
from workflow_matrix import allowed,PROD

class W6T06T10TransitionTests(unittest.TestCase):
 def test_T06_missing_human_release_holds(self):
  self.assertEqual(allowed("B","C","READY_FOR_C",PROD,human=False),(False,"HUMAN_AUTHORITY_HOLD"))

 def test_T07_human_silence_does_not_auto_release(self):
  for _elapsed_hours in (0,24,48):
   self.assertEqual(allowed("B","C","READY_FOR_C",PROD,human=False),(False,"HUMAN_AUTHORITY_HOLD"))
  # This does NOT test Telegram reminder delivery or persisted approval state.

 def test_T08_identity_and_hash_controls_on_corrected_release(self):
  self.assertEqual(allowed("B","C","READY_FOR_C",PROD,identity=False),(False,"IDENTITY_HOLD"))
  self.assertEqual(allowed("B","C","READY_FOR_C",PROD,hash_ok=False),(False,"HASH_HOLD"))
  # This does NOT verify v1 retention, v2 recheck, or version lineage.

 def test_T09_aggregate_limit_not_enforced_in_transition_guard(self):
  self.assertNotIn("released_count",allowed.__code__.co_varnames)
  self.assertNotIn("commission_id",allowed.__code__.co_varnames)
  # Coverage gap, not a PASS for W6 T09.

 def test_T10_rule_change_authority_not_enforced_in_transition_guard(self):
  self.assertNotIn("rule_change",allowed.__code__.co_varnames)
  self.assertNotIn("actor",allowed.__code__.co_varnames)
  # Coverage gap, not a PASS for W6 T10.

if __name__=="__main__":unittest.main()
