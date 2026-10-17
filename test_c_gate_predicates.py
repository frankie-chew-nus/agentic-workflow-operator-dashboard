import unittest
from c_gate_predicates import semantic_pass,stage1_completed

HASH="a"*64
class StageGateTests(unittest.TestCase):
    def test_only_exact_semantic_pass(self):
        self.assertTrue(semantic_pass({"state":"SEMANTIC_V2_PASS","failure_count":0,"module_sha256":HASH}))
        for obj in ({},{"state":"SEMANTIC_V2_HOLD","failure_count":0,"module_sha256":HASH},
                    {"state":"SEMANTIC_V2_PASS","failure_count":1,"module_sha256":HASH},
                    {"state":"SEMANTIC_V2_PASS","failure_count":0},
                    {"state":"SEMANTIC_V2_PASS","failure_count":False,"module_sha256":HASH},
                    {"message":"PASS","state":"HOLD"}):
            with self.subTest(obj=obj):self.assertFalse(semantic_pass(obj))
    def test_stage1_never_infers_pass_from_text(self):
        self.assertFalse(stage1_completed({"state":"HOLD_FOR_HUMAN","message":"PASS"}))
        self.assertTrue(stage1_completed({"state":"STAGE1_COMPLETE","pass_count":0,"fail_count":7}))
if __name__=="__main__":unittest.main()
