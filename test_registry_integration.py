import json,tempfile,unittest
from pathlib import Path
from evidence_discovery import report
class RegistryIntegrationTests(unittest.TestCase):
 def test_c_execution_discovered_but_not_qualified(self):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t);p=root/"c_runs"/"CAND-B-002"/"v2.1.3"/"stage1_output"/"summary.json"
   p.parent.mkdir(parents=True);p.write_text(json.dumps({"state":"STAGE1_COMPLETE","variant_count":54,"classification":"EXECUTION_EVIDENCE_ONLY_NO_PERFORMANCE_PASS"}))
   x=report(root);c=[a for a in x["claims"] if a["stage"]=="C"]
   self.assertEqual(len(c),1);self.assertEqual(c[0]["n"],54)
   self.assertNotEqual(c[0]["verdict"],"PASS")
   self.assertFalse(x["production_authority"])
if __name__=="__main__":unittest.main()
