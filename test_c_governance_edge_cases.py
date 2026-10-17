"""Additional fail-closed tests for source authority and dashboard stage ownership."""
import hashlib,json,tempfile,unittest
from pathlib import Path
from c_source_authority import diagnose

class AdditionalGovernanceTests(unittest.TestCase):
    def test_missing_module_is_explicit_hold(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);build=root/"build";build.mkdir()
            (build/"summary.json").write_text(json.dumps({"state":"IMPLEMENTATION_READY","module":"missing.py","module_sha256":"a"*64}))
            (root/"c_run_summary.json").write_text(json.dumps({"hold":{"expected":"a"*64,"actual":"b"*64}}))
            result=diagnose(root)
            self.assertEqual(result["classification"],"REPORTED_MODULE_NOT_FOUND")
            self.assertFalse(result["authorized_to_override_hash"])
    def test_missing_build_evidence_is_hold(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            (root/"c_run_summary.json").write_text(json.dumps({"hold":{"expected":"a"*64,"actual":"b"*64}}))
            result=diagnose(root)
            self.assertEqual(result["classification"],"SOURCE_BUILD_EVIDENCE_NOT_FOUND")
            self.assertFalse(result["authorized_to_modify_source"])
    def test_no_hash_authority_when_expected_missing(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);build=root/"build";build.mkdir()
            module=build/"strategy_module.py";module.write_text("print(1)",encoding="utf-8")
            (build/"summary.json").write_text(json.dumps({"state":"IMPLEMENTATION_READY","module":str(module),"module_sha256":"a"*64}))
            (root/"c_run_summary.json").write_text(json.dumps({"hold":{"actual":hashlib.sha256(module.read_bytes()).hexdigest()}}))
            result=diagnose(root)
            self.assertEqual(result["classification"],"UNRESOLVED_SOURCE_AUTHORITY")
            self.assertFalse(result["authorized_to_override_hash"])

if __name__=="__main__":unittest.main()
