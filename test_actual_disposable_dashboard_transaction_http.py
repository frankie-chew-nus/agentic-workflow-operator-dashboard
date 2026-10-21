"""Test actual disposable gate2.py HTTP route with simulated authority.

No active DB. Fixture uses explicit test-only verifier, never production authority.
"""
import importlib.util,json,shutil,sqlite3,sys,tempfile,threading,unittest,urllib.parse,urllib.request
from pathlib import Path
from http.server import ThreadingHTTPServer
from make_disposable_b_dashboard_transaction import make_transaction_copy
ROOT=Path(__file__).resolve().parent
FIXTURE="""def context_for(cid,rid):
 return {"authority_source":"INDEPENDENT_OPERATOR_REGISTER","candidate_id":cid,
 "research_id":rid,"production_authority":False,
 "controls":{k:{"status":"VERIFIED","evidence_sha256":"a"*64} for k in ("T04","T05","T09","T10")}}
ALLOW=False
def verify(cid,rid,ctx):return ALLOW
"""
class ActualHandlerTests(unittest.TestCase):
 def test_http_denied_then_simulated_release_once(self):
  with tempfile.TemporaryDirectory() as td:
   base=Path(td)/"w6_disposable_dashboard";base.mkdir()
   for name in ("operator_artifacts.py","operator_paths.json","b_release_guard_candidate.py",
                "b_release_authority_binding_v1.py","b_disposable_release_transaction.py"):
    shutil.copy2(ROOT/name,base/name)
   (base/"b_disposable_authority_fixture.py").write_text(FIXTURE,encoding="utf-8")
   make_transaction_copy(ROOT/"gate2.py",base/"gate2.py")
   saved={name:sys.modules.pop(name,None) for name in
          ("operator_artifacts","b_release_guard_candidate","b_release_authority_binding_v1",
           "b_disposable_release_transaction","b_disposable_authority_fixture")}
   sys.path.insert(0,str(base));server=None
   try:
    spec=importlib.util.spec_from_file_location("isolated_transaction_gate2",base/"gate2.py")
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    self.assertEqual(module.DB.resolve(),(base/"evidence"/"operator.db").resolve())
    module.init()
    server=ThreadingHTTPServer(("127.0.0.1",0),module.H)
    worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
    url=f"http://127.0.0.1:{server.server_address[1]}/"
    def post():
     data=urllib.parse.urlencode({"candidate":"CAND-B-002","decision":"RELEASE_TO_C",
      "rationale":"Disposable governance transaction test only"}).encode()
     with urllib.request.urlopen(urllib.request.Request(url,data=data),timeout=5) as response:
      self.assertEqual(response.status,200)
    def state():
     c=sqlite3.connect(module.DB)
     try:return (c.execute("SELECT state FROM candidates WHERE id='CAND-B-002'").fetchone()[0],
       c.execute("SELECT COUNT(*) FROM decisions WHERE candidate_id='CAND-B-002' AND decision='RELEASE_TO_C'").fetchone()[0])
     finally:c.close()
    post();self.assertEqual(state(),("B_REVIEW",0))
    import b_disposable_authority_fixture as fixture
    fixture.ALLOW=True
    post();self.assertEqual(state(),("READY_FOR_C",1))
    post();self.assertEqual(state(),("READY_FOR_C",1))
   finally:
    if server:server.shutdown();server.server_close()
    sys.path.remove(str(base))
    for name,original in saved.items():
     sys.modules.pop(name,None)
     if original is not None:sys.modules[name]=original
if __name__=="__main__":unittest.main()
