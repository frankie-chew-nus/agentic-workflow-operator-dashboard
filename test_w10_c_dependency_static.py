"""Week 10 C-stage dependency static-gate tests (T05).
Loads only the static() function AST from the original local orchestrator file.
Does NOT execute the orchestrator, its top-level code, model calls, or strategy.
"""
import ast,unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parent.parent
SOURCE=ROOT/"Gate2_Evidence"/"Journal10_Dependency_Policy_FINAL"/"J10-E4_Revised_Policy"/"c_orchestrator_v3.py"
def load_static():
 if not SOURCE.is_file():raise unittest.SkipTest("Week 10 original checker absent")
 tree=ast.parse(SOURCE.read_text(encoding="utf-8"))
 functions=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="static"]
 assignments=[n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ("ALLOW","BLOCK") for t in n.targets)]
 if len(functions)!=1 or len(assignments)!=1:raise AssertionError("Unexpected checker layout")
 env={"ast":ast}
 exec(compile(ast.Module(body=assignments+functions,type_ignores=[]),str(SOURCE),"exec"),env)
 return env["static"]
BASE="def metadata(): pass\ndef parameter_schema(): pass\ndef prepare(): pass\ndef signal(a,b,c): pass\n"
class W10CDependencyStaticTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.check=staticmethod(load_static())
 def test_T05_A_local_numpy_pandas_permitted(self):
  failures=self.check("import numpy\nimport pandas\nimport math\n"+BASE)
  self.assertEqual(failures,[])
 def test_T05_B_remote_dependency_flagged(self):
  failures=self.check("import requests\n"+BASE)
  self.assertIn("OPAQUE_REMOTE:requests",failures)
 def test_T05_C_unknown_dependency_requires_review(self):
  failures=self.check("import unknown_external_package\n"+BASE)
  self.assertIn("DEPENDENCY_REVIEW:unknown_external_package",failures)
if __name__=="__main__":unittest.main()
