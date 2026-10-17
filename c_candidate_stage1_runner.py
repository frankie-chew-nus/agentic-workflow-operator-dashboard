"""Candidate-driven Stage 1 runner.

Consumes only the released module's public strategy contract:
prepare(history), signal(history, prepared, params). No strategy-specific
parameter names are embedded here.
"""
import argparse,json,hashlib,importlib.util,time
from pathlib import Path

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def loadmod(p):
    s=importlib.util.spec_from_file_location("candidate_strategy",p)
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def main():
    p=argparse.ArgumentParser()
    for name in ("config","plan","manifest","release-record","semantic-pass","output-dir"):p.add_argument("--"+name,required=True)
    a=p.parse_args();cfg=json.load(open(a.config));plan=json.load(open(a.plan));man=json.load(open(a.manifest));rec=json.load(open(a.release_record));sem=json.load(open(a.semantic_pass))
    mp=Path(a.release_record).parent/rec["module"]
    checks={"release_hash":sha(mp)==rec["module_sha256"],
            "semantic_pass":sem.get("state")=="SEMANTIC_GATE_PASS" and sem.get("module_sha256")==rec["module_sha256"],
            "candidate_plan":plan.get("state")=="STAGE1_CANDIDATE_PLAN_FROZEN"}
    if not all(checks.values()):
        print(json.dumps({"state":"HOLD","reason":"PRE_RUN_IDENTITY_FAILURE","checks":checks},indent=2));raise SystemExit(20)
    # Reuse authoritative market-data source policy, not legacy strategy logic.
    import sys
    # The authoritative market-data package lives with the existing C engine.
    # Resolve it from the manifest location rather than relying on cwd/PYTHONPATH.
    croot=Path(a.manifest).resolve().parents[2]
    if str(croot) not in sys.path: sys.path.insert(0,str(croot))
    from market_data.policy import create_source
    bars=create_source("C","CSV",path=man["raw_file"]).get_bars()
    # Released semantic contract documents uppercase OHLC. Normalize only field
    # aliases at the runner boundary; values and ordering are unchanged.
    bars=[{**b,"Open":b.get("Open",b.get("open")),"High":b.get("High",b.get("high")),
           "Low":b.get("Low",b.get("low")),"Close":b.get("Close",b.get("close"))} for b in bars]
    m=loadmod(mp)
    out=Path(a.output_dir);out.mkdir(parents=True,exist_ok=True)
    results=[];t0=time.time()
    for v in plan["variants"]:
        params=v["parameters"];signals=[]
        # Completed-history prefixes prevent look-ahead and use only public contract.
        for i in range(40,len(bars)):
            history=bars[:i+1]
            prepared=m.prepare(history)
            sig=m.signal(history,prepared,params)
            if sig in (-1,1):signals.append({"index":i,"signal":sig})
        results.append({"variant_id":v["variant_id"],"parameters":params,
                        "signal_count":len(signals),"state":"STAGE1_EXECUTED",
                        "signals_sha256":hashlib.sha256(json.dumps(signals,sort_keys=True).encode()).hexdigest()})
    rp=out/"variant_results.json";rp.write_text(json.dumps(results,indent=2),encoding="utf-8")
    summary={"state":"STAGE1_COMPLETE","variant_count":len(results),
             "pass_count":0,"fail_count":0,"human_hold_count":len(results),
             "classification":"EXECUTION_EVIDENCE_ONLY_NO_PERFORMANCE_PASS",
             "elapsed_seconds":round(time.time()-t0,3),"release_sha256":rec["module_sha256"],
             "semantic_gate_sha256":sha(a.semantic_pass),"results_sha256":sha(rp)}
    (out/"summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    print(json.dumps(summary,indent=2))
if __name__=="__main__":main()
