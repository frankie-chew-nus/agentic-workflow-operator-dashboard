"""One-shot read-only Gate 2 C/model audit regression and SHA-256 capture.

Runs no strategy, backtest, network request, model call or production mutation.
Writes sanitized test log and source fingerprints under 5002/Gate2_Evidence.
"""
import argparse,datetime,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument("--project-root",required=True)
    a=p.parse_args();project=Path(a.project_root).resolve(strict=True)
    if ROOT.parent!=project:raise SystemExit("PROJECT_ROOT_MISMATCH")
    c=next((p for p in (ROOT/"gate2_c_controller",project/"gate2_c_controller") if p.is_dir()),None)
    b=next((p for p in (ROOT/"gate2_operator_app_v1",project/"gate2_operator_app_v1") if p.is_dir()),None)
    if c is None or b is None:raise SystemExit("REQUIRED_B_C_ENGINE_MISSING")
    files={
      "working/c_controller.py":ROOT/"c_controller.py",
      "working/c_candidate_stage1_plan.py":ROOT/"c_candidate_stage1_plan.py",
      "working/c_candidate_stage1_runner.py":ROOT/"c_candidate_stage1_runner.py",
      "working/c_stage1_interface.py":ROOT/"c_stage1_interface.py",
      "working/c_gate_predicates.py":ROOT/"c_gate_predicates.py",
      "working/test_gate2_c_model_audit.py":ROOT/"test_gate2_c_model_audit.py",
      "C/build_candidate_v2.py":c/"build_candidate_v2.py",
      "C/file_authoritative_build.py":c/"file_authoritative_build.py",
      "C/atomic_build_release_clean.py":c/"atomic_build_release_clean.py",
      "C/release_semantic_gate.py":c/"release_semantic_gate.py",
      "C/semantic_repair_release.py":c/"semantic_repair_release.py",
      "C/stage1_runner_v3.py":c/"stage1_runner_v3.py",
      "C/c_controller.py":c/"c_controller.py",
      "C/config/agent_registry.json":c/"config"/"agent_registry.json",
      "B/model_endpoint.py":b/"model_endpoint.py",
      "B/b_model_adapter.py":b/"b_model_adapter.py"
    }
    missing=[key for key,path in files.items() if not path.is_file()]
    if missing:raise SystemExit("MISSING_SOURCE_FILES:"+",".join(missing))
    before={k:sha(v) for k,v in files.items()}
    proc=subprocess.run([sys.executable,"-m","unittest","test_gate2_c_model_audit","-v"],
                        cwd=ROOT,text=True,capture_output=True,timeout=60)
    after={k:sha(v) for k,v in files.items()}
    stamp=datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    dest=project/"Gate2_Evidence"/("C_Model_Governance_Audit_"+stamp)
    dest.mkdir(parents=True,exist_ok=False)
    (dest/"unittest.txt").write_text(proc.stdout+"\n"+proc.stderr,encoding="utf-8")
    git=subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,text=True,capture_output=True)
    report={
      "status":"PASS" if proc.returncode==0 and before==after else "FAIL",
      "evidence_class":"IN_VITRO_STATIC_INSPECTION_AND_MOCKED_ENDPOINTS",
      "time_utc":stamp,"test_exit_code":proc.returncode,
      "working_repository_commit":git.stdout.strip() if git.returncode==0 else "UNAVAILABLE",
      "source_sha256":after,"source_unchanged":before==after,
      "live_model_calls":0,"live_network_requests":0,
      "strategy_executed":False,"backtests_executed":False,
      "active_workflow_modified":False,
      "scope":"Source and mocked protocol checks only; no live runtime security isolation proven",
      "limitations":["No real DMR/Gemma provider call in this run",
                     "No real provider interchangeability demonstrated",
                     "No malicious generated strategy code executed",
                     "Historical local C static checker not verified as active integrated control"]
    }
    (dest/"findings.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2))
    print("Evidence:",dest)
    if report["status"]!="PASS":raise SystemExit(1)
if __name__=="__main__":main()
