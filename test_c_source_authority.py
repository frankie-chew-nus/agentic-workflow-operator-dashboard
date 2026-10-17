"""Regression checks for read-only C hash analysis and B/C UI ownership."""
import hashlib,json,tempfile,unittest
from pathlib import Path
from c_source_authority import diagnose

class SourceAuthorityTests(unittest.TestCase):
    def test_newline_mismatch_is_diagnostic_only(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);build=root/"build";build.mkdir()
            source="def example():\n    return 1\n"
            disk=source.replace("\n","\r\n").encode()
            module=build/"strategy_module.py";module.write_bytes(disk)
            expected=hashlib.sha256(source.encode()).hexdigest()
            (build/"summary.json").write_text(json.dumps({"state":"IMPLEMENTATION_READY","module":str(module),"module_sha256":expected}))
            (root/"c_run_summary.json").write_text(json.dumps({"candidate_id":"CAND-B-002","version":"v2.1.3","hold":{"expected":expected,"actual":hashlib.sha256(disk).hexdigest()}}))
            result=diagnose(root)
            self.assertEqual(result["classification"],"POSSIBLE_NEWLINE_SERIALIZATION_MISMATCH")
            self.assertFalse(result["authorized_to_override_hash"])
            self.assertEqual(module.read_bytes(),disk)
    def test_unknown_mismatch_stays_unresolved(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);build=root/"build";build.mkdir()
            module=build/"strategy_module.py";module.write_text("print('unrelated')",encoding="utf-8")
            (build/"summary.json").write_text(json.dumps({"state":"IMPLEMENTATION_READY","module":str(module),"module_sha256":"a"*64}))
            (root/"c_run_summary.json").write_text(json.dumps({"hold":{"expected":"b"*64,"actual":"c"*64}}))
            result=diagnose(root)
            self.assertEqual(result["classification"],"UNRESOLVED_SOURCE_AUTHORITY")
            self.assertFalse(result["authorized_to_modify_source"])

if __name__=="__main__":unittest.main()
