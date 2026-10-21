"""Version and signer trust boundary tests. No production identity claims."""
import copy,os,time,unittest
from b_disposable_trusted_approval import sign,verify
class TrustedApprovalTests(unittest.TestCase):
 def setUp(self):
  self.key=os.urandom(32);self.keys={"operator-test-key-1":self.key}
  self.a={"candidate_id":"CAND-B-002","candidate_version":"v2.1.2","research_id":"RES-XAUUSD",
          "decision":"RELEASE_TO_C","expires_at":int(time.time())+300,
          "nonce":"trusted-approval-nonce-0001","signer_id":"operator-test-key-1"}
  self.ctx={"approval":self.a,"signature":sign(self.a,self.key)}
 def check(self,ctx=None,version="v2.1.2",keys=None,revoked=None):
  return verify("CAND-B-002",version,"RES-XAUUSD",self.ctx if ctx is None else ctx,
                trusted_keys=self.keys if keys is None else keys,revoked=revoked)
 def test_valid_version_bound_approval(self):self.assertTrue(self.check())
 def test_different_candidate_version_rejected(self):self.assertFalse(self.check(version="v2.1.3"))
 def test_tampered_version_rejected(self):
  c=copy.deepcopy(self.ctx);c["approval"]["candidate_version"]="v2.1.3";self.assertFalse(self.check(c))
 def test_untrusted_signer_rejected(self):
  c=copy.deepcopy(self.ctx);c["approval"]["signer_id"]="unknown";c["signature"]=sign(c["approval"],self.key)
  self.assertFalse(self.check(c))
 def test_revoked_signer_rejected(self):self.assertFalse(self.check(revoked={"operator-test-key-1"}))
 def test_wrong_trusted_key_rejected(self):self.assertFalse(self.check(keys={"operator-test-key-1":os.urandom(32)}))
 def test_missing_trust_registry_rejected(self):self.assertFalse(self.check(keys={}))
 def test_claimed_operator_name_not_authority(self):
  c=copy.deepcopy(self.ctx);c["operator_name"]="Operator"
  c["approval"]["operator_name"]="Operator"
  c["signature"]=sign(c["approval"],os.urandom(32))
  self.assertFalse(self.check(c))
 def test_expired_approval_rejected(self):
  c=copy.deepcopy(self.ctx);c["approval"]["expires_at"]=int(time.time())-1
  c["signature"]=sign(c["approval"],self.key)
  self.assertFalse(self.check(c))
if __name__=="__main__":unittest.main()
