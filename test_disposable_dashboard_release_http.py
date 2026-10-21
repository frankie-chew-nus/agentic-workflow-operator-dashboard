"""HTTP-level fail-closed RELEASE_TO_C test using a disposable dashboard and SQLite.

Runs only the HTTP handler in-process on loopback; no dispatcher thread, strategy,
model endpoint or C jobs. No writes to the active dashboard or active database.
"""
import importlib.util,json,shutil,sqlite3,sys,tempfile,threading,unittest,urllib.parse,urllib.request
from pathlib import Path
from http.server import ThreadingHTTPServer
from make_disposable_b_dashboard_guard import make_disposable_copy

ROOT=Path(__file__).resolve().parent

class DisposableDashboardHTTPTests(unittest.TestCase):
 def test_release_to_c_http_is_blocked_without_live_authority(self):
  with tempfile.TemporaryDirectory() as td:
   base=Path(td)/"w6_disposable_dashboard"
   base.mkdir()
   for name in ("operator_artifacts.py","operator_paths.json","b_release_guard_candidate.py"):
    shutil.copy2(ROOT/name,base/name)
   make_disposable_copy(ROOT/"gate2.py",base/"gate2.py")
   sys.path.insert(0,str(base))
   saved={name:sys.modules.pop(name,None) for name in ("operator_artifacts","b_release_guard_candidate")}
   server=None
   try:
    spec=importlib.util.spec_from_file_location("disposable_gate2_http",base/"gate2.py")
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    self.assertEqual(module.BASE.resolve(),base.resolve())
    self.assertEqual(module.DB.resolve(),(base/"evidence"/"operator.db").resolve())
    module.init()
    server=ThreadingHTTPServer(("127.0.0.1",0),module.H)
    thread=threading.Thread(target=server.serve_forever,daemon=True)
    thread.start()
    payload=urllib.parse.urlencode({
     "candidate":"CAND-B-002",
     "decision":"RELEASE_TO_C",
     "rationale":"Synthetic release attempt for isolated HTTP governance verification."
    }).encode("utf-8")
    url=f"http://127.0.0.1:{server.server_address[1]}/"
    # urllib follows the expected 303 redirect to GET.
    with urllib.request.urlopen(urllib.request.Request(url,data=payload,method="POST"),timeout=5) as response:
     self.assertEqual(response.status,200)
    conn=sqlite3.connect(module.DB)
    try:
     state,detail=conn.execute("SELECT state,detail FROM candidates WHERE id='CAND-B-002'").fetchone()
     releases=conn.execute("SELECT COUNT(*) FROM decisions WHERE candidate_id='CAND-B-002' AND decision='RELEASE_TO_C'").fetchone()[0]
     self.assertEqual(state,"B_REVIEW")
     self.assertEqual(releases,0)
     self.assertIn("TRUSTED_CONTEXT_MISSING",detail)
     self.assertNotEqual(state,"READY_FOR_C")
    finally:conn.close()
   finally:
    if server:
     server.shutdown()
     server.server_close()
    sys.path.remove(str(base))
    for name,original in saved.items():
     sys.modules.pop(name,None)
     if original is not None:sys.modules[name]=original

if __name__=="__main__":unittest.main()
