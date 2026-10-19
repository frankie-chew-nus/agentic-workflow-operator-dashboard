"""Draft policy schema tests. Synthetic records are never production approvals."""
import copy,unittest
from b_governance_policy_schema import load_draft,validate_policy
class BPolicySchemaTests(unittest.TestCase):
 def test_draft_fails_closed(self):
  errors=validate_policy(load_draft())
  for required in ("POLICY_NOT_APPROVED","HUMAN_APPROVAL_MISSING",
   "RESOURCE_INVENTORY_MISSING","DEPENDENCY_ALLOWLIST_MISSING",
   "RELEASE_LEDGER_UNVERIFIED","RULE_CHANGE_AUTHORITY_MISSING"):
   self.assertIn(required,errors)
 def test_missing_fields_block(self):
  p=load_draft();del p["approved_resources"]
  self.assertIn("MISSING_FIELD:approved_resources",validate_policy(p))
 def test_production_authority_cannot_be_granted(self):
  p=load_draft();p["production_authority"]=True
  self.assertIn("PRODUCTION_AUTHORITY_FORBIDDEN",validate_policy(p))
 def test_candidate_limit_cannot_silently_expand(self):
  p=load_draft();p["max_released_candidates"]=4
  self.assertIn("COMMISSION_LIMIT_INVALID",validate_policy(p))
 def test_synthetic_approved_shape_does_not_grant_authority(self):
  p=load_draft()
  p.update(status="APPROVED",research_commission_id="SYNTHETIC",
   approved_resources=["OHLC"],approved_dependencies=["stdlib"],
   release_ledger={"verified_source":"SYNTHETIC_FIXTURE"},
   rule_change_approval={"actor":"HUMAN"},
   operator_approval={"decision_id":"SYNTHETIC","approved_at":"SYNTHETIC","policy_sha256":"SYNTHETIC"})
  self.assertEqual(validate_policy(p),[])
  self.assertFalse(p["production_authority"])
  # Schema completeness alone does not authenticate approval or ledger provenance.
if __name__=="__main__":unittest.main()
