"""W10 C orchestrator HOLD routing tests using its actual AST-extracted static gate.

No orchestrator main(), AI API, strategy execution, or production evidence access.
Checks real routing condition from source: functional gate only when not cf and not sf,
and release only when combined failures are empty. Does not claim end-to-end orchestration.
"""
import ast,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
SOURCE=ROOT/"Gate2_Evidence"/"Journal10_Dependency_Policy_FINAL"/"J10-E4_Revised_Policy"/"c_orchestrator_v3.py"
BASE="def metadata(): pass\ndef parameter_schema(): pass\ndef prepare(): pass\ndef signal(a,b,c): pass\n"
def inspect():
 if not SOURCE.is_file():raise unittest.SkipTest("W10 orchestrator source absent")
 t=ast.parse(SOURCE.read_text(encoding="utf-8"))
 static=[n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=="static"]
 main=[n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=="main"]
 assignments=[n for n in t.body if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id in ("ALLOW","BLOCK") for x in n.targets)]
 if len(static)!=1 or len(main)!=1 or len(assignments)!=2:raise AssertionError("Unexpected W10 orchestrator layout")
 env={"ast":ast}
 exec(compile(ast.Module(body=assignments+static,type_ignores=[]),str(SOURCE),"exec"),env)
 tree=main[0]
 source=ast.unparse(tree)
 # Inspect the actual control-flow syntax, not a mock of the expected result.
 if "functional(mp, c, ct) if not cf and (not sf) else" not in source:
  raise AssertionError("Functional gate ordering changed; review required")
 if "if not fail:" not in source or "IMPLEMENTATION_READY" not in source:
  raise AssertionError("Release condition changed; review required")
 if '"HOLD_FOR_HUMAN"' not in source:raise AssertionError("HOLD path missing")
 return env["static"]
class W10DependencyHoldTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.static=staticmethod(inspect())
 def test_T05_D_prohibited_import_prevents_functional_gate(self):
  sf=self.static("import requests\n"+BASE)
  self.assertIn("OPAQUE_REMOTE:requests",sf)
  self.assertFalse(not [] and not sf)
  self.assertTrue(bool(sf))
 def test_T05_E_unknown_import_requires_review(self):
  sf=self.static("import unknown_external_package\n"+BASE)
  self.assertIn("DEPENDENCY_REVIEW:unknown_external_package",sf)
  self.assertTrue(bool(sf))
 def test_T05_F_permitted_import_continues_only_to_functional_checks(self):
  sf=self.static("import numpy\nimport pandas\n"+BASE)
  self.assertEqual(sf,[])
  # A clean static gate alone does not imply IMPLEMENTATION_READY.
if __name__=="__main__":unittest.main()
