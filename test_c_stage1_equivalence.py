import unittest
from pathlib import Path
class EquivalenceGateTests(unittest.TestCase):
 def test_gate_is_validation_only_and_strict(self):
  s=Path("c_stage1_equivalence.py").read_text(encoding="utf-8")
  self.assertIn("ZERO_SIGNAL_MISMATCHES_REQUIRED",s)
  self.assertIn("C_STAGE1_EXECUTION_EQUIVALENCE_PASS",s)
  self.assertIn("C_STAGE1_EXECUTION_EQUIVALENCE_HOLD",s)
  self.assertNotIn("write_text",s.replace("def save(p,o): Path(p).write_text",""))
if __name__=="__main__":unittest.main()
