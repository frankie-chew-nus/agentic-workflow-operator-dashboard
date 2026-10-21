"""Disposable actual dashboard HTTP path with signed test-only authority.

This copies gate2.py to a temporary directory; no active DB or dashboard edits.
"""
import importlib.util,os,shutil,sqlite3,sys,tempfile,threading,time,unittest,urllib.parse,urllib.request
from pathlib import Path
from http.server import ThreadingHTTPServer
from make_disposable_b_dashboard_transaction import make_transaction_copy
from b_disposable_signed_authority import sign
ROOT=Path(__file__).resolve().parent
FIXTURE='''from b_disposable_signed_authority import verify as check
KEY=None
CONTEXT=None
def context_for(cid,rid):
 return CONTEXT
def verify(cid,rid,ctx):
 return check(cid,rid,ctx,key=KEY)
'''
class SignedHTTPTests(unittest.TestCase):
 def test_signed_http_denial_tamper_expiry_release_and_duplicate(self):
  with tempfile.TemporaryDirectory() as td:
   base=Path(td)/"w6_disposable_dashboard";base.mkdir()
   for name in ("operator_artifacts.py","operator_paths.json","b_release_guard_candidate.py",
                "b_release_authority_binding_v1.py","b_disposable_release_transaction.py",
                "b_disposable_signed_authority.py"):
    shutil.copy2(ROOT/name,base/name)
   (base/"b_disposable_authority_fixture.py").write_text(FIXTURE,encoding="utf-8")
   make_transaction_copy(ROOT/"gate2.py",base/"gate2.py")
   names=("operator_artifacts","b_release_guard_candidate","b_release_authority_binding_v1",
          "b_disposable_release_transaction","b_disposable_signed_authority","b_disposable_authority_fixture")
   saved={name:sys.modules.pop(name,None) for name in names}
   sys.path.insert(0,str(base));server=None
   try:
    spec=importlib.util.spec_from_file_location("signed_disposable_gate2",base/"gate2.py")
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    self.assertEqual(module.DB.resolve(),(base/"evidence"/"operator.db").resolve())
    module.init()
    server=ThreadingHTTPServer(("127.0.0.1",0),module.H)
    worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
    url=f"http://127.0.0.1:{server.server_address[1]}/"
    def post():
     data=urllib.parse.urlencode({"candidate":"CAND-B-002","decision":"RELEASE_TO_C",
      "rationale":"Disposable signed authority HTTP test"}).encode()
     with urllib.request.urlopen(urllib.request.Request(url,data=data),timeout=5) as response:
      self.assertEqual(response.status,200)
    def state():
     c=sqlite3.connect(module.DB)
     try:
      return (c.execute("SELECT state FROM candidates WHERE id='CAND-B-002'").fetchone()[0],
       c.execute("SELECT COUNT(*) FROM decisions WHERE candidate_id='CAND-B-002' AND decision='RELEASE_TO_C'").fetchone()[0])
     finally:c.close()
    import b_disposable_authority_fixture as fixture
    fixture.KEY=os.urandom(32)
    p={"candidate_id":"CAND-B-002","research_id":"RES-XAUUSD","decision":"RELEASE_TO_C",
       "expires_at":int(time.time())+300,"nonce":"signed-http-test-nonce-0001"}
    controls={k:{"status":"VERIFIED","evidence_sha256":"a"*64} for k in ("T04","T05","T09","T10")}
    fixture.CONTEXT={"authority_source":"INDEPENDENT_OPERATOR_REGISTER","candidate_id":"CAND-B-002",
     "research_id":"RES-XAUUSD","production_authority":False,"controls":controls,"approval":p}
    fixture.CONTEXT["signature"]=sign(p,fixture.KEY)
    # Wrong key: deny without release.
    good_key=fixture.KEY;fixture.KEY=os.urandom(32)
    post();self.assertEqual(state(),("B_REVIEW",0))
    fixture.KEY=good_key
    # Tamper signed approval: deny.
    p["candidate_id"]="OTHER"
    post();self.assertEqual(state(),("B_REVIEW",0))
    p["candidate_id"]="CAND-B-002"
    # Expired signed approval: deny.
    p["expires_at"]=int(time.time())-1
    fixture.CONTEXT["signature"]=sign(p,fixture.KEY)
    post();self.assertEqual(state(),("B_REVIEW",0))
    # Valid signed approval: exactly one release.
    p["expires_at"]=int(time.time())+300
    fixture.CONTEXT["signature"]=sign(p,fixture.KEY)
    post();self.assertEqual(state(),("READY_FOR_C",1))
    post();self.assertEqual(state(),("READY_FOR_C",1))
   finally:
    if server:server.shutdown();server.server_close()
    sys.path.remove(str(base))
    for name,original in saved.items():
     sys.modules.pop(name,None)
     if original is not None:sys.modules[name]=original
if __name__=="__main__":unittest.main()
