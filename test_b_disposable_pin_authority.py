"""PIN hash verification regression, disposable only."""
import unittest
from b_disposable_pin_authority import enroll,verify
class PinTests(unittest.TestCase):
 def setUp(self):self.record=enroll("736291")
 def test_correct_pin(self):self.assertTrue(verify("736291",self.record))
 def test_wrong_pin(self):self.assertFalse(verify("736292",self.record))
 def test_no_plaintext_pin_stored(self):self.assertNotIn("736291",str(self.record))
 def test_non_digit_rejected(self):
  with self.assertRaises(ValueError):enroll("abcdef")
 def test_short_pin_rejected(self):
  with self.assertRaises(ValueError):enroll("1234")
 def test_non_ascii_digit_rejected(self):self.assertFalse(verify("１２３４５６",self.record))
 def test_tampered_hash_rejected(self):
  changed=dict(self.record);changed["digest"]="0"*64
  self.assertFalse(verify("736291",changed))
 def test_missing_record_rejected(self):self.assertFalse(verify("736291",{}))
 def test_unique_salts(self):self.assertNotEqual(enroll("736291")["salt"],enroll("736291")["salt"])
if __name__=="__main__":unittest.main()
