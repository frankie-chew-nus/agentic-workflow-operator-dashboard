"""Negative safety tests for candidate release guard; no active dashboard writes."""
import unittest
from b_release_guard_candidate import release_preflight
class ReleaseGuardTests(unittest.TestCase):
 def check(self,context=None):
  return release_preflight(candidate_id="CAND-B-002",research_id="RES-XAUUSD",verified_context=context)
 def test_missing_context_holds(self):
  self.assertIn("TRUSTED_CONTEXT_MISSING",self.check()["failures"])
 def test_candidate_claims_cannot_authorize(self):
  r=self.check({"authority_source":"CANDIDATE","candidate_id":"CAND-B-002","research_id":"RES-XAUUSD",
   "production_authority":False,"controls":{k:{"status":"VERIFIED","evidence_sha256":"a"*64} for k in ("T04","T05","T09","T10")}})
  self.assertIn("AUTHORITY_SOURCE_UNVERIFIED",r["failures"])
  self.assertFalse(r["release_authorized"])
 def test_missing_t09_holds(self):
  r=self.check({"authority_source":"INDEPENDENT_OPERATOR_REGISTER","candidate_id":"CAND-B-002",
   "research_id":"RES-XAUUSD","production_authority":False,
   "controls":{k:{"status":"VERIFIED","evidence_sha256":"a"*64} for k in ("T04","T05","T10")}})
  self.assertIn("T09_NOT_VERIFIED",r["failures"])
 def test_all_claims_still_cannot_activate(self):
  r=self.check({"authority_source":"INDEPENDENT_OPERATOR_REGISTER","candidate_id":"CAND-B-002",
   "research_id":"RES-XAUUSD","production_authority":False,
   "controls":{k:{"status":"VERIFIED","evidence_sha256":"a"*64} for k in ("T04","T05","T09","T10")}})
  self.assertEqual(r["state"],"GOVERNANCE_HOLD")
  self.assertIn("LIVE_AUTHORITY_BINDING_NOT_IMPLEMENTED",r["failures"])
if __name__=="__main__":unittest.main()
