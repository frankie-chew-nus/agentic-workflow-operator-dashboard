"""One-shot independently repeatable Gate 2 B->C FAIL -> FIX -> PASS capture.

Runs only disposable HTTP/SQLite tests and existing A-E boundary regressions.
Outputs raw unittest log and source hashes under 5002/Gate2_Evidence.
No PIN, live release, D/E, market-data or strategy operations.
"""
import argparse,datetime,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SUITES=("test_b_actual_http_fail_fix_pass","test_ae_build_contract",
        "test_b_operational_boundary","test_actual_dashboard_hold_no_pin")
SOURCES=("gate2.py","b_disposable_governed_http_release.py",
         "b_operational_boundary.py","test_b_actual_http_fail_fix_pass.py",
         "test_actual_dashboard_hold_no_pin.py","test_ae_build_contract.py",
         "test_b_operational_boundary.py")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--project-root",required=True)
    args=parser.parse_args()
    project=Path(args.project_root).resolve(strict=True)
    if ROOT.parent!=project:raise SystemExit("PROJECT_ROOT_MISMATCH")
    before={name:sha(ROOT/name) for name in SOURCES}
    proc=subprocess.run([sys.executable,"-m","unittest",*SUITES,"-v"],
                        cwd=ROOT,text=True,capture_output=True,timeout=180)
    after={name:sha(ROOT/name) for name in SOURCES}
    stamp=datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out=project/"Gate2_Evidence"/("B2C_FAIL_FIX_PASS_"+stamp)
    out.mkdir(parents=True,exist_ok=False)
    raw=proc.stdout+"\n"+proc.stderr
    (out/"unittest.txt").write_text(raw,encoding="utf-8")
    passed=(proc.returncode==0 and before==after)
    report={
      "status":"PASS" if passed else "FAIL",
      "execution_class":"IN_VITRO_DISPOSABLE_HTTP_SQLITE",
      "timestamp_utc":stamp,
      "test_exit_code":proc.returncode,
      "test_suites":list(SUITES),
      "source_sha256":after,
      "source_unchanged":before==after,
      "scenarios":{
        "T04_missing_resource":"HOLD_EXPECTED",
        "T05_prohibited_dependency":"HOLD_EXPECTED",
        "T09_fourth_candidate":"HOLD_EXPECTED",
        "T10_unauthorized_rule_change":"HOLD_EXPECTED",
        "authorized_synthetic_candidate":"READY_FOR_C_ONCE_EXPECTED",
        "duplicate_release":"NO_SECOND_RELEASE_EXPECTED",
        "missing_trusted_host_context":"HOLD_EXPECTED",
        "baseline_to_corrected_same_candidate":"HOLD_THEN_READY_FOR_C_EXPECTED"},
      "historical_failures":"Historical T04/T05/T09/T10 boundary failures documented separately; not replayed or relabelled here",
      "production_authority":False,"pin_in_scope":False,
      "active_dashboard_db_modified":False,
      "no_c_d_e_execution":True,
      "limitations":["Trusted approval is synthetic host-injected test evidence",
                     "Production B-to-C stays HOLD-only",
                     "Does not establish operational T04/T05/T09/T10 verification",
                     "Does not qualify C, D or E trading outcomes"]
    }
    (out/"acceptance.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2))
    print("Evidence:",out)
    if not passed:raise SystemExit(1)
if __name__=="__main__":main()
