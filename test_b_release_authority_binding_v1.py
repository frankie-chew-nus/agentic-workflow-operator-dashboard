"""Positive and negative test-only authority binding; no live credentials."""
import unittest
from b_release_authority_binding_v1 import evaluate_release
class BindingTests(unittest.TestCase):
 def context(self):
  return {"authority_source":"INDEPENDENT_OPERATOR_REGISTER",
   "candidate_id":"CAND-B-002","research_id":"RES-XAUUSD","production_authority":False,
   "controls":{k:{"status":"VERIFIED","evidence_sha256":"a"*64} for k in ("T04","T05","T09","T10")}}
 def check(self,context=None,verifier=None,disposable=True):
  return evaluate_release("CAND-B-002","RES-XAUUSD",
   self.context() if context is None else context,verifier=verifier,disposable=disposable)
 def test_no_verifier_holds(self):
  self.assertFalse(self.check()["release_authorized"])
 def test_untrusted_verifier_denial_holds(self):
  self.assertIn("INDEPENDENT_VERIFICATION_FAILED",self.check(verifier=lambda *args:False)["failures"])
 def test_missing_t09_holds_even_if_verifier_claims_yes(self):
  c=self.context();del c["controls"]["T09"]
  self.assertIn("T09_NOT_VERIFIED",self.check(c,verifier=lambda *args:True)["failures"])
 def test_disposable_positive_requires_explicit_verifier(self):
  r=self.check(verifier=lambda *args:True)
  self.assertEqual(r["state"],"DISPOSABLE_RELEASE_ELIGIBLE")
  self.assertFalse(r["production_authority"])
 def test_live_never_authorized(self):
  self.assertFalse(self.check(verifier=lambda *args:True,disposable=False)["release_authorized"])
 def test_verifier_exception_holds(self):
  def broken(*args):raise RuntimeError("bad")
  self.assertFalse(self.check(verifier=broken)["release_authorized"])
if __name__=="__main__":unittest.main()
