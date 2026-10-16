import json,sqlite3,datetime,uuid,subprocess,threading,webbrowser,html,sys,hashlib
from pathlib import Path
from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
from urllib.parse import parse_qs

BASE=Path(__file__).resolve().parent
DB=BASE/'evidence'/'operator.db'
PROJECT=BASE.parent
CROOT=PROJECT/'gate2_c_controller'
LEGACY_OPERATOR=PROJECT/'gate2_operator_app_v1'
PORT=8787

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load_json(p):
    try: return json.load(open(p,encoding='utf-8')) if Path(p).exists() else None
    except Exception: return None

def cx():
    DB.parent.mkdir(parents=True,exist_ok=True)
    c=sqlite3.connect(DB,timeout=30);c.row_factory=sqlite3.Row
    c.executescript("""CREATE TABLE IF NOT EXISTS research(id TEXT PRIMARY KEY,title TEXT,state TEXT,stage TEXT);
CREATE TABLE IF NOT EXISTS candidates(id TEXT PRIMARY KEY,research_id TEXT,state TEXT,stage TEXT,version TEXT,detail TEXT,q INTEGER);
CREATE TABLE IF NOT EXISTS decisions(id TEXT PRIMARY KEY,research_id TEXT,candidate_id TEXT,decision TEXT,rationale TEXT,created_at TEXT);
CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY,research_id TEXT,candidate_id TEXT,kind TEXT,state TEXT,detail TEXT,log_path TEXT,created_at TEXT,started_at TEXT,finished_at TEXT,return_code INTEGER);
CREATE TABLE IF NOT EXISTS artifacts(id TEXT PRIMARY KEY,candidate_id TEXT,kind TEXT,path TEXT,sha256 TEXT,created_at TEXT);""")
    return c

def decision(c,rid,cid,d,rat): c.execute('INSERT INTO decisions VALUES(?,?,?,?,?,?)',('DEC-'+uuid.uuid4().hex[:10].upper(),rid,cid,d,rat,now()))
def init():
    c=cx()
    if not c.execute('SELECT 1 FROM research').fetchone():
        rid='RES-XAUUSD';c.execute('INSERT INTO research VALUES(?,?,?,?)',(rid,'XAUUSD M1 Price Action','ACTIVE','B'))
        for x in [('CAND-B-001','C_FAIL','C','v2.1.1','0/50 PASS',1),('CAND-B-002','B_REVIEW','B','v2.1.2','Corrected B release awaiting Human review',2),('CAND-B-003','C_FAIL','C','v2.1.1','0/7 PASS',3)]: c.execute('INSERT INTO candidates VALUES(?,?,?,?,?,?,?)',(x[0],rid,x[1],x[2],x[3],x[4],x[5]))
        decision(c,rid,'CAND-B-002','RETURN_TO_B','Volatility expansion is not deterministically defined. Return to B for a corrected specification before C implementation.')
    c.commit();c.close()

def active_job(c): return c.execute("SELECT * FROM jobs WHERE state IN ('QUEUED','RUNNING') ORDER BY created_at LIMIT 1").fetchone()
def queue(c,rid,cid,kind,detail):
    if active_job(c): return False
    jid='JOB-'+uuid.uuid4().hex[:10].upper();log=BASE/'evidence'/'logs'/(jid+'.log');log.parent.mkdir(parents=True,exist_ok=True)
    c.execute('INSERT INTO jobs VALUES(?,?,?,?,?,?,?,?,?,?,?)',(jid,rid,cid,kind,'QUEUED',detail,str(log),now(),None,None,None));return True

def b_flow_cmd():
    # Dashboard orchestrates the already-proven B adapter; it does not migrate/reimplement it.
    import os
    configured=os.environ.get('GATE2_B_ADAPTER')
    candidates=[
        Path(configured) if configured else None,
        LEGACY_OPERATOR/'b_resume_model_flow_v1_1.py',
        LEGACY_OPERATOR/'b_resume_model_flow.py'
    ]
    flow=next((p for p in candidates if p and p.exists()),None)
    if not flow:
        raise FileNotFoundError('Existing B adapter not found. Expected gate2_operator_app_v1\\b_resume_model_flow_v1_1.py (or set GATE2_B_ADAPTER).')
    # Keep B adapter state/evidence with the existing workflow location.
    workflow_db=LEGACY_OPERATOR/'evidence'/'operator.db'
    if not workflow_db.exists(): workflow_db=LEGACY_OPERATOR/'evidence'/'state.db'
    return [sys.executable,str(flow),'--db',str(workflow_db),'--register',str(CROOT/'inputs'/'candidate_strategy_register_v2_1_1_frozen.json'),'--candidate','CAND-B-002','--output-dir',str(LEGACY_OPERATOR/'evidence'/'b_resume'/'CAND-B-002'),'--env',str(CROOT/'.env')]

def dispatcher():
    while True:
        try:
            c=cx();j=c.execute("SELECT * FROM jobs WHERE state='QUEUED' ORDER BY created_at LIMIT 1").fetchone()
            if not j: c.close();threading.Event().wait(1);continue
            c.execute("UPDATE jobs SET state='RUNNING',started_at=? WHERE id=?",(now(),j['id']));c.execute("UPDATE candidates SET state='B_RUNNING',stage='B',detail='Governed B correction via configured model endpoint' WHERE id=?",(j['candidate_id'],));c.commit();c.close()
            cmd=b_flow_cmd()
            with open(j['log_path'],'w',encoding='utf-8') as f: q=subprocess.run(cmd,cwd=Path(cmd[1]).parent,stdout=f,stderr=subprocess.STDOUT,text=True)
            c=cx();c.execute("UPDATE jobs SET state='COMPLETE',finished_at=?,return_code=? WHERE id=?",(now(),q.returncode,j['id']))
            rel=BASE/'evidence'/'b_resume'/j['candidate_id']/'b_corrected_release.json'; gx=load_json(BASE/'evidence'/'b_resume'/j['candidate_id']/'b_regression_hold.json') or {}
            if q.returncode==0 and rel.exists():
                x=load_json(rel) or {};ver=x.get('candidate',{}).get('version','');c.execute("UPDATE candidates SET state='B_REVIEW',stage='B',version=?,detail='Corrected B release awaiting Human review' WHERE id=?",(ver,j['candidate_id']))
            elif gx.get('reason')=='CORRECTION_REGRESSION': c.execute("UPDATE candidates SET state='GOVERNANCE_HOLD',stage='B',detail='Correction regression blocked. Review failed B revision contract rules.' WHERE id=?",(j['candidate_id'],))
            else: c.execute("UPDATE candidates SET state='SYSTEM_HOLD',stage='B',detail=? WHERE id=?",('B workflow failed. View '+j['log_path'],j['candidate_id']))
            c.commit();c.close()
        except Exception: threading.Event().wait(1)

def external_evidence_root():
    # Dashboard owns UI state, not workflow evidence. Prefer configured/existing workflow evidence.
    import os
    configured=os.environ.get('GATE2_OPERATOR_EVIDENCE_ROOT')
    candidates=[Path(configured) if configured else None, PROJECT/'gate2_operator_app_v1'/'evidence', BASE/'evidence']
    for p in candidates:
        if p and (p/'b_resume'/'CAND-B-002').exists(): return p
    return BASE/'evidence'

def review_data(): return load_json(external_evidence_root()/'b_resume'/'CAND-B-002'/'b_corrected_release.json')
def attempted_data(): return load_json(external_evidence_root()/'b_resume'/'CAND-B-002'/'corrected_candidate.json')
def regression_hold(): return load_json(external_evidence_root()/'b_resume'/'CAND-B-002'/'b_regression_hold.json')
def contract_data(): return load_json(BASE/'b002_revision_contract.json') or {'rules':[]}
def expandable_log(path,running=False):
    p=Path(path)
    if running and not p.exists():
        return '<details><summary>View execution log</summary><pre>Execution has started. The log file has not been created yet; refresh while B is running.</pre></details>'
    try: text=p.read_text(encoding='utf-8',errors='replace') if p.exists() else 'Log file unavailable: '+str(p)
    except Exception as e: text='Unable to read log: '+str(e)
    return '<details><summary>'+('View execution log' if running else 'View failure log')+'</summary><pre>'+html.escape(text)+'</pre></details>'
def spec_details(label,obj): return '<details><summary>'+html.escape(label)+'</summary><pre>'+html.escape(json.dumps(obj or {},indent=2))+'</pre></details>'

def governance_html():
    hold=regression_hold() or {};contract=contract_data();prev=(review_data() or {}).get('candidate',{});att=attempted_data() or {};att=att.get('candidate',att) if isinstance(att,dict) else {}
    mapping={'VERSION_MUST_BE':'VERSION','STRICT_NR_N_NOT_PRESERVED':'STRICT_NR_N','VOLATILITY_EXPANSION_RULE_MISSING':'VOL_RULE','VOLATILITY_EXPANSION_NOT_IN_ENTRY':'VOL_ENTRY','ATR_DEFAULT_SEARCH_RELATION_NOT_PRESERVED':'ATR_DEFAULT'}
    failed=set(mapping.get(str(f).split(':',1)[0],str(f).split(':',1)[0]) for f in hold.get('failures',[]));protected={'STRICT_NR_N','VOL_RULE','VOL_ENTRY','ATR_DEFAULT','HYPOTHESIS','EVIDENCE','PARAMETERS','DEPENDENCIES'}
    if failed & protected: failed.add('NO_REGRESSION')
    rows=[]
    for r in contract.get('rules',[]):
        bad=r['id'] in failed;diag=''
        if bad: diag={'VERSION':'Expected next immutable patch version; attempted '+str(hold.get('attempted_version','')),'STRICT_NR_N':'Expected strict < semantics throughout.','VOL_RULE':'Expected breakout range > average range of preceding N candles.','VOL_ENTRY':'Expected volatility confirmation in both long and short entry logic.','NO_REGRESSION':'One or more previously accepted protected requirements regressed.'}.get(r['id'],'Contract check failed.')
        rows.append('<tr class="'+('rule-fail' if bad else 'rule-pass')+'"><td>'+('✗' if bad else '✓')+'</td><td>'+html.escape(r['id'])+'</td><td>'+html.escape(r['label'])+'</td><td>'+html.escape(diag)+'</td></tr>')
    return '<div class="governance-panel"><h3>GOVERNANCE HOLD — CORRECTION REGRESSION</h3><p>The attempted B correction was blocked before release.</p><table class="rules"><tr><th></th><th>Rule</th><th>Requirement</th><th>Observed / expected</th></tr>'+''.join(rows)+'</table>'+spec_details('View previous valid specification',prev)+spec_details('View attempted specification',att)+spec_details('View raw failed-rule evidence',hold)+'</div>'

def form_buttons(buttons,placeholder='Human rationale'):
    bs=''.join('<button class="'+('bad' if v=='REJECT' else 'good' if v=='RELEASE_TO_C' else '')+'" name=decision value="'+v+'">'+html.escape(lbl)+'</button>' for v,lbl in buttons)
    return '<form method=post action=/decide><textarea name=rationale required minlength=12 placeholder="'+html.escape(placeholder)+'"></textarea><input type=hidden name=candidate value=CAND-B-002>'+bs+'</form>'

def stage_body(candidate,job):
    if job and job['candidate_id']=='CAND-B-002': return '<div class="stage-work running"><h3>RUNNING — NO ACTION REQUIRED</h3><p>'+html.escape(job['detail'])+'</p>'+expandable_log(job['log_path'],running=True)+'<button onclick="location.reload()">Refresh</button></div>'
    if not candidate:return ''
    st=candidate['state']
    if st=='B_REVIEW':
        cand=(review_data() or {}).get('candidate',{});vol=cand.get('operator_assumptions',{}).get('volatility_expansion_definition') or cand.get('operator_assumptions',{}).get('volatility_expansion_condition','')
        return '<div class="stage-work"><h3>ACTION REQUIRED — HUMAN B→C REVIEW</h3><p><b>Hypothesis:</b> '+html.escape(cand.get('hypothesis',''))+'</p><p><b>Volatility expansion:</b> '+html.escape(vol)+'</p>'+spec_details('View corrected specification',cand)+form_buttons([('RETURN_TO_B','Return to B'),('REJECT','Reject'),('RELEASE_TO_C','Release to C')])+'</div>'
    if st=='GOVERNANCE_HOLD': return '<div class="stage-work hold"><h3>ACTION REQUIRED — GOVERNANCE HOLD</h3>'+governance_html()+form_buttons([('RETURN_FAILED_RULES','Return to B with failed rules'),('REJECT','Reject candidate')])+'</div>'
    if st=='SYSTEM_HOLD':
        path=candidate['detail'].split('View ',1)[1] if 'View ' in candidate['detail'] else ''
        return '<div class="stage-work hold"><h3>ACTION REQUIRED — SYSTEM HOLD</h3><p>'+html.escape(candidate['detail'])+'</p>'+expandable_log(path)+spec_details('View last corrected specification',(review_data() or {}).get('candidate',{}))+form_buttons([('RETRY_B','Retry same B work'),('REJECT','Reject candidate')])+'</div>'
    if st=='WAITING_FOR_B': return '<div class="stage-work"><h3>ACTION REQUIRED — RESUME B</h3>'+form_buttons([('RESUME_B','Resume B'),('REJECT','Reject candidate')])+'</div>'
    if st=='READY_FOR_C': return '<div class="stage-work"><h3>B COMPLETE — READY FOR C</h3><p>Human release recorded. C integration is the next backend milestone.</p></div>'
    return ''

def journey_html(r,cs,job):
    defs={'A':('Research & Source Qualification','Grounded Researcher + Human Operator'),'B':('Evidence Synthesis & Strategy Formulation','Knowledge Archivist + Strategy Optimizer + Human Operator'),'C':('Local Integration & Stage 1 Backtesting','Existing local C CLI / Local Backtest Runner'),'D':('Hidden OOS / Walk-Forward Validation','Local deterministic harness + MT5 + Human OOS boundary'),'E':('Commissioning Audit & Decision','Human Operator + deterministic commissioning checks')}
    order='ABCDE';idx=order.index(r['stage']);candidate=next((x for x in cs if x['id']=='CAND-B-002'),None);cards=[]
    for i,k in enumerate(order):
        title,owner=defs[k]
        if i<idx: state,status,cls='FROZEN','HANDED OVER TO '+order[i+1],'done'
        elif i==idx: state,cls='ACTIVE','active';status='RUNNING — NO ACTION REQUIRED' if job else ('HUMAN ACTION REQUIRED' if candidate and candidate['state'] in ('B_REVIEW','WAITING_FOR_B','SYSTEM_HOLD','GOVERNANCE_HOLD') else 'WORKFLOW ACTIVE')
        else: state,status,cls='NOT STARTED','Awaiting '+order[i-1]+' handoff','future'
        extra=('<p><b>Current candidate:</b> '+html.escape(candidate['id'])+' · '+html.escape(candidate['version'] or '')+' · '+html.escape(candidate['state'])+'</p>'+stage_body(candidate,job)) if k=='B' and candidate else ''
        cards.append('<section class="journey-card '+cls+'"><div class="journey-head"><span class="stage-letter">'+k+'</span><div><b>'+title+'</b><div class="state">'+state+' · '+status+'</div></div></div><p><b>Owner:</b> '+owner+'</p>'+extra+'</section>')
    return '<div class="card"><h2>Full research journey</h2><div class="journey">'+'<div class="arrow">↓</div>'.join(cards)+'</div></div>'

def render():
    c=cx();r=c.execute("SELECT * FROM research WHERE state='ACTIVE'").fetchone();cs=list(c.execute('SELECT * FROM candidates ORDER BY q'));job=active_job(c)
    b='<div class=card><small>ACTIVE RESEARCH</small><h1>'+html.escape(r['title'])+'</h1></div>'+journey_html(r,cs,job)
    b+='<div class=card><h2>Candidate pipeline</h2><table><tr><th>ID</th><th>Version</th><th>Stage</th><th>State</th><th>Detail</th></tr>'
    for x in cs:b+='<tr'+(' class="candidate-active"' if x['id']=='CAND-B-002' else '')+'><td>'+x['id']+'</td><td>'+html.escape(x['version'] or '')+'</td><td>'+x['stage']+'</td><td>'+x['state']+'</td><td>'+html.escape(x['detail'])+'</td></tr>'
    b+='</table></div><div class=card><h2>Human decision ledger</h2><table><tr><th>Candidate</th><th>Decision</th><th>Rationale</th></tr>'
    for d in c.execute('SELECT * FROM decisions ORDER BY created_at DESC'):b+='<tr><td>'+d['candidate_id']+'</td><td>'+d['decision']+'</td><td>'+html.escape(d['rationale'])+'</td></tr>'
    b+='</table></div>';c.close()
    css='body{font-family:Segoe UI,Arial;background:#f3f5f7;margin:0}header{background:#111827;color:white;padding:18px}main{max-width:1120px;margin:auto;padding:22px}.card{background:white;padding:18px;margin:14px 0;border:1px solid #ddd;border-radius:12px}.journey{display:grid;gap:10px}.journey-card{border:1px solid #d1d5db;border-radius:10px;padding:14px}.done{background:#f0fdf4}.active{border:2px solid #2563eb;background:#eff6ff}.future{background:#f3f4f6;color:#6b7280}.journey-head{display:flex;gap:12px;align-items:center}.stage-letter{display:inline-flex;width:42px;height:42px;border-radius:50%;align-items:center;justify-content:center;background:#111827;color:white;font-weight:700}.state{font-size:13px;font-weight:700}.arrow{text-align:center}.stage-work{margin-top:16px;padding-top:16px;border-top:2px solid #93c5fd}.hold{border-top-color:#d97706}.candidate-active{background:#eff6ff}textarea{width:96%;min-height:75px;padding:10px}button{padding:10px 14px;margin:8px 5px 0 0;background:#2563eb;color:white;border:0;border-radius:6px}.good{background:#15803d}.bad{background:#b91c1c}table{width:100%;border-collapse:collapse}td,th{padding:9px;border-bottom:1px solid #ddd;text-align:left}pre{white-space:pre-wrap;background:#f8fafc;padding:12px;max-height:520px;overflow:auto}details{margin:12px 0;border:1px solid #bfdbfe;border-radius:8px;background:white;padding:10px}.rule-pass{background:#f0fdf4}.rule-fail{background:#fef2f2;font-weight:600}'
    return '<html><head><meta charset=utf-8><style>'+css+'</style></head><body><header><h2>Gate 2 Operator App</h2></header><main>'+b+'</main></body></html>'

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        b=render().encode();self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.end_headers();self.wfile.write(b)
    def do_POST(self):
        n=int(self.headers.get('Content-Length',0));f=parse_qs(self.rfile.read(n).decode());c=cx();r=c.execute("SELECT * FROM research WHERE state='ACTIVE'").fetchone();cid=f.get('candidate',[''])[0];d=f.get('decision',[''])[0];rat=f.get('rationale',[''])[0].strip();x=c.execute('SELECT * FROM candidates WHERE id=?',(cid,)).fetchone()
        if x and len(rat)>=12 and not active_job(c):
            if d in ('RETURN_TO_B','RESUME_B','RETRY_B','RETURN_FAILED_RULES'):decision(c,r['id'],cid,d,rat);queue(c,r['id'],cid,'B_RESUME','Governed B correction via configured model endpoint')
            elif d=='REJECT':decision(c,r['id'],cid,d,rat);c.execute("UPDATE candidates SET state='REJECTED',detail='Human rejected candidate' WHERE id=?",(cid,))
            elif d=='RELEASE_TO_C':decision(c,r['id'],cid,d,rat);c.execute("UPDATE candidates SET state='READY_FOR_C',stage='B',detail='Human released corrected B candidate to C queue' WHERE id=?",(cid,))
        c.commit();c.close();self.send_response(303);self.send_header('Location','/');self.end_headers()
    def log_message(self,*a):pass

if __name__=='__main__':
    init();threading.Thread(target=dispatcher,daemon=True).start();u=f'http://127.0.0.1:{PORT}/';print(u);threading.Timer(.5,lambda:webbrowser.open(u)).start();ThreadingHTTPServer(('127.0.0.1',PORT),H).serve_forever()
