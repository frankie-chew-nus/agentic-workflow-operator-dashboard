import unittest
from c_candidate_stage1_runner import max_lookback
class FastRunnerTests(unittest.TestCase):
 def test_window_derived_from_schema_not_dataset(self):
  self.assertEqual(max_lookback({"lookback_period":[5,10],"breakout_buffer":[.05,.2],"trailing_atr_multiplier":[1.5,3]}),40)
 def test_larger_declared_lookback_controls_window(self):
  self.assertEqual(max_lookback({"period":[5,75]}),75)
if __name__=="__main__":unittest.main()
