"""Tests signed approval binding; test-only key and fixture."""
import copy,os,time,unittest
from b_disposable_signed_authority import sign,verify
class SignedAuthorityTests(unittest.TestCase):
 def setUp(self):
  self.key=os.urandom(32)
  self.p={"candidate_id":"CAND-B-002","research_id":"RES-XAUUSD","decision":"RELEASE_TO_C","expires_at":int(time.time())+300,"nonce":"disposable-unique-0001"}
  self.ctx={"approval":self.p,"signature":sign(self.p,self.key)}
 def check(self,ctx=None,key=None,now=None):
  return verify("CAND-B-002","RES-XAUUSD",self.ctx if ctx is None else ctx,key=self.key if key is None else key,now=now)
 def test_valid(self):self.assertTrue(self.check())
 def test_wrong_key(self):self.assertFalse(self.check(key=os.urandom(32)))
 def test_expired(self):self.assertFalse(self.check(now=self.p["expires_at"]))
 def test_missing_signature(self):
  c=copy.deepcopy(self.ctx);del c["signature"];self.assertFalse(self.check(c))
 def test_candidate_tamper(self):
  c=copy.deepcopy(self.ctx);c["approval"]["candidate_id"]="OTHER";self.assertFalse(self.check(c))
 def test_commission_tamper(self):
  c=copy.deepcopy(self.ctx);c["approval"]["research_id"]="OTHER";self.assertFalse(self.check(c))
 def test_decision_tamper(self):
  c=copy.deepcopy(self.ctx);c["approval"]["decision"]="REJECT";self.assertFalse(self.check(c))
 def test_nonce_tamper(self):
  c=copy.deepcopy(self.ctx);c["approval"]["nonce"]="disposable-unique-0002";self.assertFalse(self.check(c))
 def test_signature_tamper(self):
  c=copy.deepcopy(self.ctx);c["signature"]="0"*64;self.assertFalse(self.check(c))
 def test_short_key(self):self.assertFalse(self.check(key=b"short"))
if __name__=="__main__":unittest.main()
