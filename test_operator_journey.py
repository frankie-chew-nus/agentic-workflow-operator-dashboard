import unittest
from operator_test_harness import run
class JourneyTests(unittest.TestCase):
 def test_sandbox_never_becomes_production_authority(self):
  x=run();self.assertEqual(x["state"],"OPERATOR_TEST_HARNESS_PASS")
  self.assertTrue(x["c_test_fixture_blocked_from_d_production"])
  self.assertTrue(x["c_test_fixture_allowed_in_d_sandbox"])
  self.assertTrue(x["d_test_fixture_blocked_from_e_production"])
if __name__=="__main__":unittest.main()
