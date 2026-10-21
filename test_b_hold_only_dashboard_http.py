"""Actual isolated dashboard HTTP denies B->C release even with valid form."""
import importlib.util,sqlite3,sys,tempfile,threading,unittest,urllib.parse,urllib.request,shutil
from pathlib import Path
from http.server import ThreadingHTTPServer
from build_b_hold_only_dashboard import build
ROOT=Path(__file__).resolve().parent
class HoldOnlyHTTP(unittest.TestCase):
 def test_release_denied_and_no_ledger_insert(self):
  with tempfile.TemporaryDirectory() as td:
   base=Path(td)/"w6_disposable_dashboard";base.mkdir()
   for name in ("operator_artifacts.py","operator_paths.json"):
    shutil.copy2(ROOT/name,base/name)
   build(ROOT/"gate2.py",base/"gate2.py")
   saved=sys.modules.pop("operator_artifacts",None)
   sys.path.insert(0,str(base));server=None
   try:
    spec=importlib.util.spec_from_file_location("isolated_hold_gate2",base/"gate2.py")
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    module.init()
    server=ThreadingHTTPServer(("127.0.0.1",0),module.H)
    worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
    data=urllib.parse.urlencode({"candidate":"CAND-B-002","decision":"RELEASE_TO_C",
      "rationale":"Explicit Human release request that must be blocked","pin":"736291"}).encode()
    url=f"http://127.0.0.1:{server.server_address[1]}/"
    with urllib.request.urlopen(urllib.request.Request(url,data=data),timeout=5) as response:
     self.assertEqual(response.status,200)
    conn=sqlite3.connect(module.DB)
    try:
     self.assertEqual(conn.execute("SELECT state FROM candidates WHERE id='CAND-B-002'").fetchone()[0],"B_REVIEW")
     self.assertEqual(conn.execute("SELECT COUNT(*) FROM decisions WHERE candidate_id='CAND-B-002' AND decision='RELEASE_TO_C'").fetchone()[0],0)
    finally:conn.close()
   finally:
    if server:server.shutdown();server.server_close();worker.join(timeout=5)
    sys.path.remove(str(base))
    sys.modules.pop("operator_artifacts",None)
    if saved is not None:sys.modules["operator_artifacts"]=saved
if __name__=="__main__":unittest.main()
