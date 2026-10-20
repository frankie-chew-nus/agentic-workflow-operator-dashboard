"""Controlled B integration candidate regression using disposable adapter fixtures."""
import unittest
from test_disposable_b_integration import DisposableIntegrationTests
from controlled_b_integration_candidate import run
from b_policy_change_gate_v1 import digest

class ControlledBIntegrationTests(DisposableIntegrationTests):
 def ctx(self,n=0,**kw):
  prior={"revision":1,"production_authority":False,"max_released_candidates":3}
  d={"fixture_only":True,"available_resources":{"OHLC","ATR"},
     "approved_dependencies":{"stdlib","numpy"},
     "release_ledger":{"schema":"COMMISSION_LEDGER_V1","commission_id":"SYN",
      "status":"VERIFIED_BY_OPERATOR","releases":[{"candidate_id":f"OLD-{i}",
       "human_decision_id":f"DEC-{i}","release_artifact_sha256":"a"*64} for i in range(n)]},
     "commission_id":"SYN","verified_decision_ids":{f"DEC-{i}" for i in range(n)},
     "prior_policy":prior,"trusted_prior_policy_digest":digest(prior)}
  d.update(kw);return d
 def execute(self,extra=None,context=None):
  c=dict(self.candidate);c.update({"required_resources":["OHLC"],"dependencies":["numpy"]});c.update(extra or {})
  self.corrected.write_text(__import__("json").dumps(c))
  return run(c,context if context is not None else self.ctx(),fixture_root=self.base,
    adapter=self.adapter,db=self.db,register=self.register,corrected_candidate=self.corrected)
 def test_consolidated_T04_hold(self):
  r=self.execute({"required_resources":["MISSING"]});self.assertFalse(r["adapter_executed"])
 def test_consolidated_T05_hold(self):
  r=self.execute({"dependencies":["REMOTE"]});self.assertFalse(r["adapter_executed"])
 def test_consolidated_T09_hold(self):
  r=self.execute(context=self.ctx(n=3));self.assertFalse(r["adapter_executed"])
 def test_consolidated_T10_hold(self):
  r=self.execute({"governance_rule_change":{"actor":"AI"}});self.assertFalse(r["adapter_executed"])
 def test_consolidated_valid_disposable_path(self):
  r=self.execute();self.assertEqual(r["state"],"B_RESUME_TEST_ONLY")
  self.assertFalse(r["production_authority"])
 def test_consolidated_untrusted_context_holds(self):
  r=self.execute(context={});self.assertEqual(r["state"],"GOVERNANCE_HOLD")
  self.assertFalse(r["adapter_executed"])
if __name__=="__main__":unittest.main()
