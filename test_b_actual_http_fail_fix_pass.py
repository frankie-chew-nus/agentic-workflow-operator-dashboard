"""Actual dashboard HTTP -> SQLite: T04/T05/T09/T10 HOLD and authorized PASS.

All requests run against a copied dashboard in a disposable temporary directory.
No live DB, C engine, strategy or D/E process is invoked.
"""
import copy,hashlib,importlib.util,shutil,sqlite3,sys,tempfile,threading,unittest,urllib.parse,urllib.request
from pathlib import Path
from http.server import ThreadingHTTPServer
ROOT=Path(__file__).resolve().parent
CANDIDATE="CAND-B-002"
RESEARCH="RES-XAUUSD"
VERSION="v2.1.2"

def trusted():
    return {"source":"DISPOSABLE_TEST_HOST","candidate_id":CANDIDATE,
      "research_id":RESEARCH,"version":VERSION,
      "operator_decision":"APPROVE_B_TO_C","decision_id":"SYNTHETIC-HUMAN-001",
      "controls":{k:{"status":"VERIFIED","evidence_sha256":hashlib.sha256(k.encode()).hexdigest()}
                  for k in ("T04","T05","T09","T10")},
      "required_resources_available":True,"dependency_inventory_reviewed":True,
      "prohibited_dependencies":[],"policy_change_requested":False,
      "policy_change_actor":None,"policy_change_approved_by_operator":False}

class ActualHTTPGovernanceTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.base=Path(self.temp.name)/"w6_disposable_dashboard"
        self.base.mkdir()
        for name in ("gate2.py","operator_artifacts.py","operator_paths.json",
                     "b_operational_boundary.py","b_disposable_governed_http_release.py"):
            shutil.copy2(ROOT/name,self.base/name)
        self.saved={k:sys.modules.pop(k,None) for k in
                    ("operator_artifacts","b_operational_boundary","b_disposable_governed_http_release")}
        sys.path.insert(0,str(self.base))
        spec=importlib.util.spec_from_file_location("isolated_governance_gate2",self.base/"gate2.py")
        self.mod=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.mod)
        self.mod.init()
        self.mod.DISPOSABLE_GOVERNANCE_TEST_MODE=True
        self.mod.DISPOSABLE_GOVERNANCE_CONTEXT=trusted()
        self.server=ThreadingHTTPServer(("127.0.0.1",0),self.mod.H)
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True)
        self.thread.start()
    def tearDown(self):
        self.server.shutdown();self.server.server_close();self.thread.join(timeout=5)
        sys.path.remove(str(self.base))
        for k,v in self.saved.items():
            sys.modules.pop(k,None)
            if v is not None:sys.modules[k]=v
        self.temp.cleanup()
    def post(self):
        data=urllib.parse.urlencode({"candidate":CANDIDATE,"decision":"RELEASE_TO_C",
               "rationale":"Synthetic Operator approval for disposable governance test"}).encode()
        url="http://127.0.0.1:%d/decide"%self.server.server_address[1]
        with urllib.request.urlopen(urllib.request.Request(url,data=data),timeout=6) as response:
            self.assertEqual(response.status,200)
    def snapshot(self):
        c=sqlite3.connect(self.mod.DB)
        try:
            state=c.execute("SELECT state FROM candidates WHERE id=?",(CANDIDATE,)).fetchone()[0]
            count=c.execute("SELECT COUNT(*) FROM decisions WHERE candidate_id=? AND decision='RELEASE_TO_C'",(CANDIDATE,)).fetchone()[0]
            detail=c.execute("SELECT detail FROM candidates WHERE id=?",(CANDIDATE,)).fetchone()[0]
            return state,count,detail
        finally:c.close()
    def assert_hold(self,code):
        self.post()
        state,count,detail=self.snapshot()
        self.assertEqual((state,count),("B_REVIEW",0))
        self.assertIn(code,detail)
    def test_T04_missing_resource_hold(self):
        self.mod.DISPOSABLE_GOVERNANCE_CONTEXT["required_resources_available"]=False
        self.assert_hold("T04_MISSING_RESOURCE")
    def test_T05_prohibited_dependency_hold(self):
        self.mod.DISPOSABLE_GOVERNANCE_CONTEXT["prohibited_dependencies"]=["OPAQUE_BLACK_BOX"]
        self.assert_hold("T05_PROHIBITED_OR_UNVERIFIED_DEPENDENCY")
    def test_T09_fourth_candidate_hold(self):
        c=sqlite3.connect(self.mod.DB)
        try:
            for i in range(3):
                c.execute("INSERT INTO decisions VALUES(?,?,?,?,?,?)",
                    ("SYNTH-PRIOR-%d"%i,RESEARCH,"OTHER-%d"%i,"RELEASE_TO_C",
                     "synthetic prior release","2026-10-01"))
            c.commit()
        finally:c.close()
        self.assert_hold("T09_COMMISSION_LIMIT")
    def test_T10_unauthorized_rule_change_hold(self):
        self.mod.DISPOSABLE_GOVERNANCE_CONTEXT["policy_change_requested"]=True
        self.mod.DISPOSABLE_GOVERNANCE_CONTEXT["policy_change_actor"]="AI_AGENT"
        self.assert_hold("T10_AI_RULE_CHANGE")
    def test_valid_authorized_release_once_and_duplicate_hold(self):
        self.post()
        state,count,detail=self.snapshot()
        self.assertEqual((state,count),("READY_FOR_C",1))
        self.assertIn("DISPOSABLE_TEST_RELEASE_ONLY",detail)
        self.post()
        state,count,detail=self.snapshot()
        self.assertEqual((state,count),("READY_FOR_C",1))
        self.assertEqual(list((self.base/"evidence").rglob("c_runs/*")),[])
    def test_untrusted_form_cannot_supply_authority(self):
        self.mod.DISPOSABLE_GOVERNANCE_CONTEXT=None
        self.post()
        self.assertEqual(self.snapshot()[:2],("B_REVIEW",0))

if __name__=="__main__":unittest.main()
