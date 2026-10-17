import json,tempfile,unittest
from pathlib import Path
from c_stage1_resolver import resolve_stage1

class Stage1ResolverTests(unittest.TestCase):
    def test_missing_and_empty(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            self.assertEqual(resolve_stage1(root/"missing")["reason"],"OUTPUT_DIRECTORY_MISSING")
            self.assertEqual(resolve_stage1(root)["reason"],"NO_AUTHORITATIVE_SUMMARY")
    def test_summary_by_content_not_filename(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);p=root/"arbitrary_name.json"
            p.write_text(json.dumps({"state":"STAGE1_COMPLETE","variant_count":7,"pass_count":0,"fail_count":7,"human_hold_count":0}))
            result=resolve_stage1(root)
            self.assertEqual(result["state"],"C_STAGE1_REVIEW_REQUIRED")
            self.assertEqual(result["metrics"]["fail_count"],7)
            self.assertFalse(result["advance_to_d"])
    def test_ambiguous_and_invalid(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            obj={"state":"STAGE1_COMPLETE","variant_count":7,"pass_count":0,"fail_count":7,"human_hold_count":0}
            for n in ("a.json","b.json"):(root/n).write_text(json.dumps(obj))
            self.assertEqual(resolve_stage1(root)["reason"],"AMBIGUOUS_AUTHORITATIVE_SUMMARIES")
            (root/"b.json").unlink()
            obj["pass_count"]=8
            (root/"a.json").write_text(json.dumps(obj))
            self.assertEqual(resolve_stage1(root)["reason"],"NO_AUTHORITATIVE_SUMMARY")
if __name__=="__main__":unittest.main()
