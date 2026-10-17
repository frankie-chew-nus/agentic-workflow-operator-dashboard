import unittest
from c_gate_predicates import semantic_repair_authorized
H="a"*64
class RepairAuthorizationTests(unittest.TestCase):
    def test_matching_semantic_hold(self):
        self.assertTrue(semantic_repair_authorized({"state":"SEMANTIC_GATE_HOLD","failure_count":1,"module_sha256":H},{"module_sha256":H}))
    def test_no_repair_without_exact_release_authority(self):
        bad=[
            ({"state":"SEMANTIC_V2_PASS","failure_count":1,"module_sha256":H},{"module_sha256":H}),
            ({"state":"SEMANTIC_GATE_HOLD","failure_count":0,"module_sha256":H},{"module_sha256":H}),
            ({"state":"SEMANTIC_GATE_HOLD","failure_count":1,"module_sha256":"b"*64},{"module_sha256":H}),
            ({"state":"SEMANTIC_GATE_HOLD","failure_count":1,"module_sha256":H},{}),
            ({"state":"SEMANTIC_GATE_HOLD","failure_count":True,"module_sha256":H},{"module_sha256":H}),
        ]
        for sem,release in bad:
            with self.subTest(sem=sem):self.assertFalse(semantic_repair_authorized(sem,release))
if __name__=="__main__":unittest.main()
