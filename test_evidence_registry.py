import hashlib,tempfile,unittest
from pathlib import Path
from evidence_registry import inspect_claim,inspect_registry
class EvidenceRegistryTests(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();self.root=Path(self.t.name)
  self.p=self.root/"evidence.json";self.p.write_text('{"state":"D_SANDBOX_PASS"}')
  self.c={"claim_id":"P01","claim":"Sandbox D evidence exists","proof_type":"SANDBOX",
          "method":"deterministic fixture","n":1,"denominator":1,"expected":"D_SANDBOX_PASS",
          "observed":"D_SANDBOX_PASS","verdict":"PASS","stage":"D","human_decision":None,
          "artifacts":[{"path":"evidence.json","sha256":hashlib.sha256(self.p.read_bytes()).hexdigest()}]}
 def tearDown(self):self.t.cleanup()
 def test_hash_verification_does_not_grant_authority(self):
  x=inspect_claim(self.c,self.root)
  self.assertEqual(x["verification"],"VERIFIED_ARTIFACTS")
  self.assertFalse(x["production_authority"])
 def test_tampering_is_visible(self):
  self.p.write_text("changed")
  self.assertEqual(inspect_claim(self.c,self.root)["verification"],"UNVERIFIED_ARTIFACTS")
 def test_missing_artifact_is_not_verified(self):
  self.p.unlink()
  self.assertEqual(inspect_claim(self.c,self.root)["verification"],"UNVERIFIED_ARTIFACTS")
 def test_missing_fields_are_incomplete(self):
  self.assertEqual(inspect_claim({"claim_id":"P02"},self.root)["verification"],"INCOMPLETE")
 def test_no_path_escape(self):
  self.c["artifacts"]=[{"path":"../outside.json","sha256":"a"*64}]
  self.assertEqual(inspect_claim(self.c,self.root)["verification"],"UNVERIFIED_ARTIFACTS")
 def test_duplicate_claims_rejected(self):
  with self.assertRaises(ValueError):inspect_registry([self.c,self.c],self.root)
 def test_incomplete_equivalence_never_upgraded(self):
  self.c["proof_type"]="INCOMPLETE";self.c["verdict"]="INCOMPLETE"
  x=inspect_claim(self.c,self.root)
  self.assertEqual(x["recorded_verdict"],"INCOMPLETE")
  self.assertFalse(x["production_authority"])
if __name__=="__main__":unittest.main()
