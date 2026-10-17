import argparse,copy,datetime,hashlib,json,subprocess,sys
from pathlib import Path

def load(p):
    return json.load(open(p,encoding="utf-8"))
def save(p,obj):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,indent=2),encoding="utf-8")
def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(cmd,cwd,log):
    with open(log,"a",encoding="utf-8") as f:
        f.write("\n$ "+" ".join(map(str,cmd))+"\n")
        q=subprocess.run(cmd,cwd=cwd,stdout=f,stderr=subprocess.STDOUT,text=True)
    if q.returncode!=0: raise RuntimeError("Command failed rc=%s: %s"%(q.returncode,cmd[1]))
def find_candidate(node,cid):
    if isinstance(node,dict):
        if node.get("candidate_id")==cid:return node
        for v in node.values():
            r=find_candidate(v,cid)
            if r is not None:return r
    elif isinstance(node,list):
        for v in node:
            r=find_candidate(v,cid)
            if r is not None:return r
    return None
def newest(root,names):
    hits=[]
    for n in names:hits.extend(Path(root).rglob(n))
    hits=[p for p in hits if p.is_file()]
    return max(hits,key=lambda p:p.stat().st_mtime) if hits else None
def passish(obj):
    txt=json.dumps(obj).upper()
    return ("PASS" in txt) and not any(x in txt for x in ['"FAIL"','"HOLD"','"BLOCKED"'])

ap=argparse.ArgumentParser()
ap.add_argument("--c-root",required=True);ap.add_argument("--legacy-evidence",required=True)
ap.add_argument("--candidate",required=True);ap.add_argument("--version",required=True)
ap.add_argument("--run-root",required=True);ap.add_argument("--log",required=True)
a=ap.parse_args()
croot=Path(a.c_root);runroot=Path(a.run_root);runroot.mkdir(parents=True,exist_ok=True)
log=Path(a.log);summary=runroot/"c_run_summary.json"
try:
    release=load(Path(a.legacy_evidence)/"b_resume"/a.candidate/"b_corrected_release.json")
    candidate=release.get("candidate",{})
    if candidate.get("candidate_id")!=a.candidate or candidate.get("version")!=a.version:
        raise RuntimeError("Frozen B release identity/version mismatch")
    template=croot/"inputs"/"candidate_strategy_register_v2_1_1_frozen.json"
    reg=load(template);target=find_candidate(reg,a.candidate)
    if target is None: raise RuntimeError("Candidate not found in authoritative C spec template")
    target.clear();target.update(copy.deepcopy(candidate))
    spec=runroot/("candidate_strategy_register_"+a.version.replace(".","_")+"_frozen.json");save(spec,reg)
    boundary={"state":"C_BOUNDARY_FROZEN","candidate_id":a.candidate,"version":a.version,"spec":str(spec),"spec_sha256":digest(spec),"b_release_sha256":digest(Path(a.legacy_evidence)/"b_resume"/a.candidate/"b_corrected_release.json"),"created_at":datetime.datetime.now(datetime.timezone.utc).isoformat()}
    save(runroot/"c_boundary.json",boundary)

    buildroot=runroot/"build"
    run([sys.executable,str(croot/"atomic_build_release_clean.py"),"--spec",str(spec),"--candidate",a.candidate,"--run-root",str(buildroot)],croot,log)
    release_record=newest(buildroot,["implementation_release.json","*release*.json"])
    if not release_record: raise RuntimeError("Atomic build completed but no release record was found")

    semantic=runroot/"semantic_pass.json"
    run([sys.executable,str(croot/"release_semantic_gate.py"),"--release-record",str(release_record),"--spec",str(spec),"--output",str(semantic)],croot,log)
    sem=load(semantic)
    if not passish(sem):
        save(summary,{"state":"C_SEMANTIC_HOLD","candidate_id":a.candidate,"version":a.version,"release_record":str(release_record),"semantic":str(semantic)})
        print(json.dumps(load(summary),indent=2));raise SystemExit(20)

    manifest=croot/"evidence"/"market_data"/"stage1_manifest.json"
    if not manifest.exists(): raise RuntimeError("Stage1 manifest not found")
    freeze=runroot/"stage1_config"
    run([sys.executable,str(croot/"freeze_stage1_plan.py"),"--manifest",str(manifest),"--release-record",str(release_record),"--spec",str(spec),"--output-dir",str(freeze)],croot,log)
    config=newest(freeze,["stage1_config.json"]);plan=newest(freeze,["variant_plan.json"])
    if not config or not plan: raise RuntimeError("Stage1 freeze did not produce config and variant plan")

    output=runroot/"stage1_output"
    run([sys.executable,str(croot/"stage1_runner_v3.py"),"--config",str(config),"--plan",str(plan),"--manifest",str(manifest),"--release-record",str(release_record),"--semantic-pass",str(semantic),"--output-dir",str(output)],croot,log)
    result=newest(output,["*summary*.json","*result*.json","*ledger*.json"])
    state="C_COMPLETE_REVIEW"
    if result:
        obj=load(result);txt=json.dumps(obj).upper()
        if "C_PASS" in txt or ('"PASS"' in txt and '"FAIL"' not in txt):state="C_PASS"
        elif "C_FAIL" in txt or '"FAIL"' in txt:state="C_FAIL"
    out={"state":state,"candidate_id":a.candidate,"version":a.version,"boundary":str(runroot/"c_boundary.json"),"release_record":str(release_record),"semantic_pass":str(semantic),"config":str(config),"plan":str(plan),"manifest":str(manifest),"output_dir":str(output),"result":str(result) if result else None}
    save(summary,out);print(json.dumps(out,indent=2))
except SystemExit: raise
except Exception as e:
    save(summary,{"state":"C_SYSTEM_HOLD","candidate_id":a.candidate,"version":a.version,"error":repr(e),"log":str(log)})
    print(json.dumps(load(summary),indent=2));raise SystemExit(2)
