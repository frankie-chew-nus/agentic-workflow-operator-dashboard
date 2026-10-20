"""Synthetic tests for consolidated B preflight; no active workflow authority."""
import unittest
from b_policy_change_gate_v1 import digest
from consolidated_b_governance_preflight import evaluate
class ConsolidatedTests(unittest.TestCase):
 def ctx(self,n=0,**kw):
  prior={"revision":1,"production_authority":False,"max_released_candidates":3}
  d={"fixture_only":True,"available_resources":{"OHLC","ATR"},
     "approved_dependencies":{"numpy","pandas","stdlib"},
     "release_ledger":{"schema":"COMMISSION_LEDGER_V1","commission_id":"SYN",
       "status":"VERIFIED_BY_OPERATOR","releases":[{"candidate_id":f"OLD-{i}",
        "human_decision_id":f"DEC-{i}","release_artifact_sha256":"a"*64} for i in range(n)]},
     "commission_id":"SYN","verified_decision_ids":{f"DEC-{i}" for i in range(n)},
     "prior_policy":prior,"trusted_prior_policy_digest":digest(prior)}
  d.update(kw);return d
 def candidate(self,**kw):
  c={"candidate_id":"NEW","required_resources":["OHLC"],"dependencies":["numpy"]}
  c.update(kw);return c
 def test_T04_missing_resource(self):
  self.assertIn("RESOURCE_UNAVAILABLE:LIB_Z",evaluate(self.candidate(required_resources=["LIB_Z"]),self.ctx())["failures"])
 def test_T05_opaque_dependency(self):
  self.assertIn("DEPENDENCY_NOT_APPROVED:REMOTE",evaluate(self.candidate(dependencies=["REMOTE"]),self.ctx())["failures"])
 def test_T09_fourth_candidate(self):
  self.assertIn("COMMISSION_LIMIT_REACHED",evaluate(self.candidate(),self.ctx(n=3))["failures"])
 def test_T10_unapproved_policy_change(self):
  self.assertIn("POLICY_CHANGE_RECORD_MISSING",evaluate(self.candidate(governance_rule_change={"revision":2}),self.ctx())["failures"])
 def test_missing_context_holds(self):
  self.assertEqual(evaluate(self.candidate(),{})["state"],"GOVERNANCE_HOLD")
 def test_unverified_decisions_hold(self):
  self.assertIn("HUMAN_DECISION_NOT_VERIFIED",evaluate(self.candidate(),self.ctx(n=1,verified_decision_ids=set()))["failures"])
 def test_valid_fixture_no_release_authority(self):
  r=evaluate(self.candidate(),self.ctx(n=2))
  self.assertEqual(r["state"],"PREFLIGHT_PASS_TEST_ONLY")
  self.assertFalse(r["production_authority"])
if __name__=="__main__":unittest.main()
