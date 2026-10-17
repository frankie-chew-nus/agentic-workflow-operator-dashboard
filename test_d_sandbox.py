import json,tempfile,unittest
from pathlib import Path
from operator_handoff import TEST,PRODUCTION,envelope,validate
from d_sandbox import run
class DSandboxTests(unittest.TestCase):
 def fixture(self):
  t=tempfile.TemporaryDirectory();r=Path(t.name);a=r/"c.json";a.write_text('{"fixture":true}')
  return t,r,envelope("C","FIX-001","v0",TEST,[("c_summary",a)],"C_TEST_FIXTURE")
 def test_pass_still_has_no_production_authority(self):
  t,r,c=self.fixture()
  try:
   x=run(c,[{"outcome":1},{"outcome":-1},{"outcome":1}],r/"d")
   self.assertEqual(x["state"],"D_SANDBOX_PASS");self.assertFalse(x["production_authority"]);self.assertFalse(x["advance_to_e_production"])
   dh=json.loads((r/"d"/"d_handoff.json").read_text())
   self.assertFalse(validate(dh,"D","FIX-001","v0")["pass"])
  finally:t.cleanup()
 def test_fail_is_deterministic(self):
  t,r,c=self.fixture()
  try:self.assertEqual(run(c,[{"outcome":-1}],r/"d")["state"],"D_SANDBOX_FAIL")
  finally:t.cleanup()
 def test_production_c_evidence_rejected_by_sandbox(self):
  t,r,c=self.fixture()
  try:
   c["evidence_kind"]=PRODUCTION
   self.assertEqual(run(c,[{"outcome":1}],r/"d")["state"],"D_SANDBOX_HOLD")
  finally:t.cleanup()
 def test_missing_hidden_data_holds(self):
  t,r,c=self.fixture()
  try:self.assertEqual(run(c,[],r/"d")["state"],"D_SANDBOX_HOLD")
  finally:t.cleanup()
if __name__=="__main__":unittest.main()
