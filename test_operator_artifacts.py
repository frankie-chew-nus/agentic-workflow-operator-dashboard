import json,tempfile,unittest
from pathlib import Path
from operator_artifacts import resolve_paths,record_artifact,stage1_inventory

class ArtifactRegistryTests(unittest.TestCase):
    def test_resolve_paths(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/"operator_paths.json").write_text(json.dumps({"paths":{"c_engine":"../controller","b_engine":"../operator"}}))
            p=resolve_paths(root)
            self.assertEqual(p["c_engine"],str((root/"../controller").resolve()))
    def test_immutable_artifact_binding(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);artifact=root/"result.json";artifact.write_text('{"state":"PASS"}')
            first=record_artifact(root/"run","semantic",artifact)
            self.assertEqual(first,record_artifact(root/"run","semantic",artifact))
            artifact.write_text('{"state":"HOLD"}')
            with self.assertRaisesRegex(RuntimeError,"conflict"):record_artifact(root/"run","semantic",artifact)
    def test_empty_stage1_directory_is_not_success(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(stage1_inventory(Path(d))["state"],"EMPTY_OUTPUT_DIRECTORY")
if __name__=="__main__":unittest.main()
