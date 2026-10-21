"""Disposable HTTP transaction tests: actual POST -> transaction -> SQLite.

The handler is a test-only subclass. It does NOT modify or prove the original
dashboard RELEASE_TO_C handler is wired to the transaction. Never use in production.
"""
import json,sqlite3,tempfile,threading,unittest,urllib.parse,urllib.request
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from b_disposable_release_transaction import attempt

class HTTPTransactionTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory()
  self.db=Path(self.tmp.name)/"operator.db"
  con=sqlite3.connect(self.db)
  con.executescript("""CREATE TABLE candidates(id TEXT PRIMARY KEY,research_id TEXT,state TEXT,stage TEXT);
CREATE TABLE decisions(id TEXT PRIMARY KEY,research_id TEXT,candidate_id TEXT,decision TEXT,rationale TEXT,created_at TEXT);
INSERT INTO candidates VALUES('CAND-B-002','RES-XAUUSD','B_REVIEW','B');""")
  con.close()
  self.context={"authority_source":"INDEPENDENT_OPERATOR_REGISTER",
   "candidate_id":"CAND-B-002","research_id":"RES-XAUUSD","production_authority":False,
   "controls":{k:{"status":"VERIFIED","evidence_sha256":"a"*64} for k in ("T04","T05","T09","T10")}}
  outer=self
  class Handler(BaseHTTPRequestHandler):
   def log_message(self,*args):pass
   def do_POST(self):
    n=int(self.headers.get("Content-Length","0"))
    if n>8192:
     self.send_error(413);return
    form=urllib.parse.parse_qs(self.rfile.read(n).decode("utf-8"))
    cid=form.get("candidate",[""])[0]
    if form.get("decision",[""])[0]!="RELEASE_TO_C":
     self.send_error(400);return
    con=sqlite3.connect(outer.db)
    try:
     result=attempt(con,cid,"RES-XAUUSD",outer.context,
                    verifier=outer.verifier,disposable=True)
    finally:con.close()
    body=json.dumps(result).encode()
    self.send_response(200)
    self.send_header("Content-Type","application/json")
    self.send_header("Content-Length",str(len(body)))
    self.end_headers();self.wfile.write(body)
  self.verifier=lambda *args:False
  self.server=ThreadingHTTPServer(("127.0.0.1",0),Handler)
  self.thread=threading.Thread(target=self.server.serve_forever,daemon=True)
  self.thread.start()
 def tearDown(self):
  self.server.shutdown();self.server.server_close();self.thread.join(timeout=3)
  self.tmp.cleanup()
 def post(self):
  url="http://127.0.0.1:%d/"%self.server.server_address[1]
  data=urllib.parse.urlencode({"candidate":"CAND-B-002","decision":"RELEASE_TO_C"}).encode()
  with urllib.request.urlopen(urllib.request.Request(url,data=data),timeout=5) as r:
   return json.load(r)
 def state(self):
  c=sqlite3.connect(self.db)
  try:
   return (c.execute("SELECT state FROM candidates").fetchone()[0],
           c.execute("SELECT COUNT(*) FROM decisions").fetchone()[0])
  finally:c.close()
 def test_denied_http_no_write(self):
  self.assertEqual(self.post()["state"],"HOLD")
  self.assertEqual(self.state(),("B_REVIEW",0))
 def test_missing_t09_http_no_write(self):
  self.verifier=lambda *args:True
  del self.context["controls"]["T09"]
  self.assertEqual(self.post()["state"],"HOLD")
  self.assertEqual(self.state(),("B_REVIEW",0))
 def test_positive_http_once_duplicate_denied(self):
  self.verifier=lambda *args:True
  self.assertEqual(self.post()["state"],"DISPOSABLE_RELEASED")
  self.assertEqual(self.state(),("READY_FOR_C",1))
  self.assertEqual(self.post()["state"],"HOLD")
  self.assertEqual(self.state(),("READY_FOR_C",1))
 def test_tampered_context_http_no_write(self):
  self.verifier=lambda *args:True
  self.context["research_id"]="OTHER"
  self.assertEqual(self.post()["state"],"HOLD")
  self.assertEqual(self.state(),("B_REVIEW",0))
if __name__=="__main__":unittest.main()
