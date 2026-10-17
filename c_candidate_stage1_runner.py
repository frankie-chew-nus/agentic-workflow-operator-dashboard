"""Candidate-driven Stage 1 execution with progress evidence.

No strategy-specific parameter names. Preparation is computed once per completed
history prefix and reused across variants; signal evaluation remains candidate-
specific and look-ahead safe.
"""
import argparse,json,hashlib,importlib.util,time,sys
from pathlib import Path

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,o):Path(p).write_text(json.dumps(o,indent=2),encoding="utf-8")
def loadmod(p):
    s=importlib.util.spec_from_file_location("candidate_strategy",p)
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def progress(path,t0,phase,done,total,detail=""):
    obj={"state":"STAGE1_RUNNING","phase":phase,"completed":done,"total":total,
         "percent":round(100*done/total,1) if total else 0,
         "elapsed_seconds":round(time.time()-t0,1),"heartbeat_epoch":time.time(),
         "detail":detail}
    save(path,obj);print(json.dumps(obj),flush=True)

def main():
    p=argparse.ArgumentParser()
    for n in ("config","plan","manifest","release-record","semantic-pass","output-dir"):p.add_argument("--"+n,required=True)
    a=p.parse_args();plan=json.load(open(a.plan));man=json.load(open(a.manifest));rec=json.load(open(a.release_record));sem=json.load(open(a.semantic_pass))
    mp=Path(a.release_record).parent/rec["module"]
    checks={"release_hash":sha(mp)==rec["module_sha256"],
            "semantic_pass":sem.get("state")=="SEMANTIC_GATE_PASS" and sem.get("module_sha256")==rec["module_sha256"],
            "candidate_plan":plan.get("state")=="STAGE1_CANDIDATE_PLAN_FROZEN"}
    if not all(checks.values()):
        print(json.dumps({"state":"HOLD","reason":"PRE_RUN_IDENTITY_FAILURE","checks":checks},indent=2));raise SystemExit(20)
    croot=Path(a.manifest).resolve().parents[2]
    if str(croot) not in sys.path:sys.path.insert(0,str(croot))
    from market_data.policy import create_source
    bars=create_source("C","CSV",path=man["raw_file"]).get_bars()
    bars=[{**b,"Open":b.get("Open",b.get("open")),"High":b.get("High",b.get("high")),
           "Low":b.get("Low",b.get("low")),"Close":b.get("Close",b.get("close"))} for b in bars]
    m=loadmod(mp);out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=True)
    pf=out/"progress.json";t0=time.time();start=40;indices=list(range(start,len(bars)))
    # Expensive prepare(history) depends on history only, not the variant. Compute once.
    prepared=[]
    total=len(indices)
    for n,i in enumerate(indices,1):
        history=bars[:i+1];prepared.append(m.prepare(history))
        if n==1 or n%1000==0 or n==total:progress(pf,t0,"PREPARING_HISTORY",n,total,f"bar {i+1}/{len(bars)}")
    results=[];variants=plan["variants"];vtotal=len(variants)
    for vn,v in enumerate(variants,1):
        params=v["parameters"];signals=[]
        for pos,i in enumerate(indices):
            history=bars[:i+1];sig=m.signal(history,prepared[pos],params)
            if sig in (-1,1):signals.append({"index":i,"signal":sig})
        results.append({"variant_id":v["variant_id"],"parameters":params,"signal_count":len(signals),
                        "state":"STAGE1_EXECUTED","signals_sha256":hashlib.sha256(json.dumps(signals,sort_keys=True).encode()).hexdigest()})
        progress(pf,t0,"EVALUATING_VARIANTS",vn,vtotal,f"variant {vn}/{vtotal}")
    rp=out/"variant_results.json";save(rp,results)
    summary={"state":"STAGE1_COMPLETE","variant_count":len(results),"pass_count":0,"fail_count":0,
             "human_hold_count":len(results),"classification":"EXECUTION_EVIDENCE_ONLY_NO_PERFORMANCE_PASS",
             "elapsed_seconds":round(time.time()-t0,3),"release_sha256":rec["module_sha256"],
             "semantic_gate_sha256":sha(a.semantic_pass),"results_sha256":sha(rp)}
    save(out/"summary.json",summary);progress(pf,t0,"COMPLETE",vtotal,vtotal,"Stage 1 execution evidence complete")
    print(json.dumps(summary,indent=2),flush=True)
if __name__=="__main__":main()
