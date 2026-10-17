import json,tempfile,unittest
from pathlib import Path
from c_stage1_preflight import preflight

class Stage1PreflightTests(unittest.TestCase):
    def run_case(self,count,state="SEMANTIC_GATE_PASS",failures=0):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            for name,obj in (("config.json",{}),("plan.json",{"variants":[{} for _ in range(count)]}),("semantic.json",{"state":state,"failure_count":failures})):
                (root/name).write_text(json.dumps(obj),encoding="utf-8")
            return preflight(root/"config.json",root/"plan.json",root/"semantic.json")
    def test_authorized_50_variants(self):
        self.assertEqual(self.run_case(50)["state"],"C_STAGE1_PREFLIGHT_READY")
    def test_variant_count_mismatch_blocks(self):
        r=self.run_case(7)
        self.assertEqual(r["state"],"C_STAGE1_PREFLIGHT_HOLD")
        self.assertFalse(r["safe_to_run"])
    def test_semantic_hold_blocks(self):
        self.assertFalse(self.run_case(50,"SEMANTIC_GATE_HOLD",1)["safe_to_run"])
if __name__=="__main__":unittest.main()
