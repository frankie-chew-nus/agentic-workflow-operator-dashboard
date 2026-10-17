import hashlib,tempfile,unittest
from pathlib import Path
from repair_c_source_hash import apply

class SourceHashRepairTests(unittest.TestCase):
    def fixture(self):
        return ("import hashlib\n"
                "from pathlib import Path\n"
                "def emit(mp,cp,final,code):\n"
                "    a=hashlib.sha256(final.encode()).hexdigest()\n"
                "    b=hashlib.sha256(final.encode()).hexdigest()\n"
                "    c=hashlib.sha256(final.encode()).hexdigest()\n"
                "    d=hashlib.sha256(code.encode()).hexdigest()\n")
    def test_guarded_repair_and_idempotence(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"build_candidate_v2.py";p.write_text(self.fixture(),encoding="utf-8")
            self.assertEqual(apply(p),"SOURCE_HASH_FILE_BYTES_FIX_APPLIED")
            self.assertEqual(apply(p),"ALREADY_APPLIED")
            self.assertIn("mp.read_bytes()",p.read_text())
            self.assertIn("cp.read_bytes()",p.read_text())
            self.assertTrue(p.with_suffix(".pre_source_hash_fix.py").exists())
    def test_unrecognized_source_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"build_candidate_v2.py";p.write_text("print('unrecognized')\n")
            with self.assertRaisesRegex(RuntimeError,"HOLD"):apply(p)
            self.assertEqual(p.read_text(),"print('unrecognized')\n")
    def test_file_byte_hash_differs_on_crlf(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"strategy_module.py"
            text="def x():\n    return 1\n"
            p.write_bytes(text.replace("\n","\r\n").encode())
            self.assertNotEqual(hashlib.sha256(text.encode()).hexdigest(),hashlib.sha256(p.read_bytes()).hexdigest())
if __name__=="__main__":unittest.main()
