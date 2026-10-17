import json,tempfile,unittest
from pathlib import Path
from operator_handoff import *
class HandoffTests(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();self.root=Path(self.t.name);self.a=self.root/"evidence.json";self.a.write_text('{"ok":true}')
 def tearDown(self):self.t.cleanup()
 def test_valid_production(self):
  e=envelope("C","X","v1",PRODUCTION,[("c_summary",self.a)],"C_PASS")
  self.assertTrue(validate(e,"C","X","v1")["pass"])
 def test_test_fixture_blocked_from_production(self):
  e=envelope("C","X","v1",TEST,[("c_summary",self.a)],"C_TEST_FIXTURE")
  self.assertFalse(validate(e,"C","X","v1")["pass"])
  self.assertTrue(validate(e,"C","X","v1",allow_test=True)["pass"])
 def test_hash_tamper_blocks(self):
  e=envelope("C","X","v1",PRODUCTION,[("c_summary",self.a)],"C_PASS");self.a.write_text("tampered")
  self.assertFalse(validate(e,"C","X","v1")["pass"])
 def test_wrong_candidate_blocks(self):
  e=envelope("C","X","v1",PRODUCTION,[("c_summary",self.a)],"C_PASS")
  self.assertFalse(validate(e,"C","Y","v1")["pass"])
if __name__=="__main__":unittest.main()
