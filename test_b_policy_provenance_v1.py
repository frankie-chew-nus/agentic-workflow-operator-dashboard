"""Synthetic provenance tests; no claim of authenticated Human approval."""
import copy,hashlib,unittest
from b_policy_provenance_v1 import canonical,verify_bundle
class ProvenanceTests(unittest.TestCase):
 def fixture(self):
  return {"status":"OPERATOR_REVIEWED",
   "operator_decision":{"decision_id":"SYN-1","decision_at":"SYNTHETIC","reviewer":"SYNTHETIC"},
   "resource_inventory":["OHLC"],"dependency_allowlist":["numpy"],
   "release_ledger":{"commission_id":"SYN","released_candidate_ids":["CAND-1"]},
   "rule_change_authority":"HUMAN_ONLY","production_authority":False}
 def digest(self,x):return hashlib.sha256(canonical(x)).hexdigest()
 def test_missing_external_digest_holds(self):
  self.assertIn("TRUSTED_DIGEST_MISSING",verify_bundle(self.fixture()))
 def test_tampered_bundle_holds(self):
  b=self.fixture();d=self.digest(b);b["resource_inventory"].append("OPAQUE_REMOTE")
  self.assertIn("BUNDLE_HASH_MISMATCH",verify_bundle(b,d))
 def test_missing_human_provenance_holds(self):
  b=self.fixture();b["operator_decision"]={}
  self.assertIn("DECISION_PROVENANCE_MISSING",verify_bundle(b,self.digest(b)))
 def test_unverified_release_ledger_holds(self):
  b=self.fixture();b["release_ledger"]={}
  self.assertIn("RELEASE_LEDGER_UNVERIFIED",verify_bundle(b,self.digest(b)))
 def test_rule_change_authority_holds(self):
  b=self.fixture();b["rule_change_authority"]="AI"
  self.assertIn("RULE_CHANGE_AUTHORITY_UNVERIFIED",verify_bundle(b,self.digest(b)))
 def test_synthetic_complete_shape_only(self):
  b=self.fixture();self.assertEqual(verify_bundle(b,self.digest(b)),[])
  self.assertFalse(b["production_authority"])
  # Structural PASS is not Human authentication or production approval.
if __name__=="__main__":unittest.main()
