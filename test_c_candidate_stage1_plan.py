import json,tempfile,unittest
from pathlib import Path
from c_candidate_stage1_plan import build

class CandidatePlanTests(unittest.TestCase):
    def test_plan_uses_only_frozen_b_parameters(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);spec=root/"spec.json";cfg=root/"config.json";cfg.write_text("{}")
            spec.write_text(json.dumps({"candidates":[{"candidate_id":"CAND-B-002","parameter_ranges":{"lookback_period":[5,10],"breakout_buffer":[0.05,0.2],"trailing_atr_multiplier":[1.5,3.0]}}]}))
            path,plan=build(spec,"CAND-B-002",cfg,root/"out")
            self.assertTrue(path.exists())
            self.assertEqual(set(plan["parameter_names"]),{"lookback_period","breakout_buffer","trailing_atr_multiplier"})
            self.assertNotIn("atr_period",json.dumps(plan))
            self.assertNotIn("risk_reward_ratio",json.dumps(plan))
            self.assertEqual(plan["variant_count"],54)
    def test_invalid_range_fails(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);spec=root/"spec.json";cfg=root/"config.json";cfg.write_text("{}")
            spec.write_text(json.dumps({"candidates":[{"candidate_id":"X","parameter_ranges":{"n":[10,5]}}]}))
            with self.assertRaises(ValueError):build(spec,"X",cfg,root/"out")
if __name__=="__main__":unittest.main()
