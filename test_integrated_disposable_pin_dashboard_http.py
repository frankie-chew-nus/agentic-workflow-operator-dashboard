"""Disposable actual dashboard HTTP PIN and version-bound signature test."""
import importlib.util,os,shutil,sqlite3,sys,tempfile,threading,time,unittest,urllib.parse,urllib.request
from pathlib import Path
from http.server import ThreadingHTTPServer
from build_disposable_pin_dashboard_integrated import build
from b_disposable_pin_authority import enroll
from b_disposable_trusted_approval import sign
ROOT=Path(__file__).resolve().parent
FIXTURE='''TRUSTED_KEYS={}
REVOKED=set()
PIN_RECORD=None
CONTEXT=None
def context_for(cid,rid):return CONTEXT
'''
class IntegratedPINHTTPTests(unittest.TestCase):
 def test_integrated_pin_http_denial_and_release(self):
  with tempfile.TemporaryDirectory() as td:
   base=Path(td)/"w6_disposable_dashboard";base.mkdir()
   for name in ("operator_artifacts.py","operator_paths.json","b_release_guard_candidate.py",
                "b_release_authority_binding_v1.py","b_disposable_trusted_approval.py",
                "b_disposable_versioned_transaction.py","b_disposable_pin_authority.py",
                "b_disposable_pin_atomic.py"):
    shutil.copy2(ROOT/name,base/name)
   (base/"b_disposable_authority_fixture.py").write_text(FIXTURE,encoding="utf-8")
   build(ROOT/"gate2.py",base/"gate2.py")
   names=("operator_artifacts","b_release_guard_candidate","b_release_authority_binding_v1",
          "b_disposable_trusted_approval","b_disposable_versioned_transaction",
          "b_disposable_pin_authority","b_disposable_pin_atomic","b_disposable_authority_fixture")
   saved={name:sys.modules.pop(name,None) for name in names}
   sys.path.insert(0,str(base));server=None
   try:
    spec=importlib.util.spec_from_file_location("pin_disposable_gate2",base/"gate2.py")
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    module.init()
    rendered=module.render()
    self.assertIn('name="pin"',rendered)
    self.assertIn('type="password"',rendered)
    c=sqlite3.connect(module.DB)
    try:
     c.execute("CREATE TABLE disposable_authority_nonces(nonce TEXT PRIMARY KEY,candidate_id TEXT,research_id TEXT,used_at TEXT)")
     c.commit()
    finally:c.close()
    server=ThreadingHTTPServer(("127.0.0.1",0),module.H)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    url=f"http://127.0.0.1:{server.server_address[1]}/"
    def post(pin):
     data=urllib.parse.urlencode({"candidate":"CAND-B-002","decision":"RELEASE_TO_C",
       "rationale":"Disposable local PIN HTTP approval","pin":pin}).encode()
     with urllib.request.urlopen(urllib.request.Request(url,data=data),timeout=5) as response:
      self.assertEqual(response.status,200)
    def snapshot():
     c=sqlite3.connect(module.DB)
     try:return (c.execute("SELECT state FROM candidates WHERE id='CAND-B-002'").fetchone()[0],
       c.execute("SELECT COUNT(*) FROM decisions WHERE candidate_id='CAND-B-002' AND decision='RELEASE_TO_C'").fetchone()[0])
     finally:c.close()
    import b_disposable_authority_fixture as fixture
    key=os.urandom(32);fixture.TRUSTED_KEYS={"test-operator":key};fixture.PIN_RECORD=enroll("736291")
    approval={"candidate_id":"CAND-B-002","candidate_version":"v2.1.2","research_id":"RES-XAUUSD",
      "decision":"RELEASE_TO_C","expires_at":int(time.time())+300,
      "nonce":"pin-http-test-nonce-0001","signer_id":"test-operator"}
    ctx={"authority_source":"INDEPENDENT_OPERATOR_REGISTER","candidate_id":"CAND-B-002",
      "research_id":"RES-XAUUSD","production_authority":False,
      "controls":{k:{"status":"VERIFIED","evidence_sha256":"a"*64} for k in ("T04","T05","T09","T10")},
      "approval":approval,"signature":sign(approval,key)}
    fixture.CONTEXT=ctx
    post("000000");self.assertEqual(snapshot(),("B_REVIEW",0))
    approval["candidate_version"]="v2.1.3";ctx["signature"]=sign(approval,key)
    post("736291");self.assertEqual(snapshot(),("B_REVIEW",0))
    approval["candidate_version"]="v2.1.2";ctx["signature"]=sign(approval,key)
    post("736291");self.assertEqual(snapshot(),("READY_FOR_C",1))
    post("736291");self.assertEqual(snapshot(),("READY_FOR_C",1))
   finally:
    if server:server.shutdown();server.server_close()
    sys.path.remove(str(base))
    for name,original in saved.items():
     sys.modules.pop(name,None)
     if original is not None:sys.modules[name]=original
if __name__=="__main__":unittest.main()
