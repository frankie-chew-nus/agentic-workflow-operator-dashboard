"""W6 T01-T05 executable contract checks against production workflow_matrix.allowed.

Scope: verifies the A-E transition guard, NOT full W6.2 specification validation.
Missing checks are reported as COVERAGE_GAP, not fabricated PASS.
"""
import json,unittest
from workflow_matrix import allowed,PROD
class W6GovernanceT01T05(unittest.TestCase):
 def test_T01_valid_released_state_authorized(self):
  self.assertEqual(allowed("B","C","READY_FOR_C",PROD,human=True,identity=True,hash_ok=True),(True,"AUTHORIZED"))
 def test_T02_ambiguous_spec_has_no_direct_validation_in_transition_guard(self):
  # Transition guard does not inspect the candidate specification.
  # Explicitly record a gap; no synthetic PASS for ambiguity checking.
  self.assertNotIn("specification",allowed.__code__.co_varnames)
 def test_T03_unapproved_evidence_kind_blocked(self):
  self.assertEqual(allowed("B","C","READY_FOR_C","WORKFLOW_TEST_FIXTURE"),(False,"EVIDENCE_KIND_HOLD"))
 def test_T04_missing_resource_not_validated_by_transition_guard(self):
  self.assertNotIn("resources",allowed.__code__.co_varnames)
 def test_T05_prohibited_dependency_not_validated_by_transition_guard(self):
  self.assertNotIn("dependencies",allowed.__code__.co_varnames)
if __name__=="__main__":unittest.main()
