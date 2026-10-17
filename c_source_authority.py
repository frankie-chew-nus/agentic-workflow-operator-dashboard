"""Read-only source authority analysis. Never changes build files or expected hashes."""
import hashlib,json
from pathlib import Path

def sha(b): return hashlib.sha256(b).hexdigest()
def read(p):
    try:return json.loads(Path(p).read_text(encoding="utf-8"))
    except (OSError,ValueError):return {}
def diagnose(runroot):
    root=Path(runroot); summary=read(root/"c_run_summary.json"); hold=summary.get("hold") or {}
    expected=hold.get("expected");actual=hold.get("actual")
    findings=[]
    for path in sorted((root/"build").rglob("*.json")) if (root/"build").exists() else []:
        obj=read(path)
        if not isinstance(obj,dict) or obj.get("state")!="IMPLEMENTATION_READY":continue
        module=obj.get("module")
        if not module:continue
        mp=Path(module)
        if not mp.is_absolute():mp=path.parent/mp
        if not mp.is_file():continue
        data=mp.read_bytes()
        try:
            txt=data.decode("utf-8")
            utf8_hash=sha(txt.encode("utf-8"))
            lf_hash=sha(txt.replace("\r\n","\n").encode("utf-8"))
            crlf_hash=sha(txt.replace("\r\n","\n").replace("\n","\r\n").encode("utf-8"))
        except UnicodeDecodeError: utf8_hash=lf_hash=crlf_hash=None
        record={"summary":str(path),"module":str(mp),"reported_sha256":obj.get("module_sha256"),
                "disk_sha256":sha(data),"utf8_sha256":utf8_hash,
                "lf_normalized_sha256":lf_hash,"crlf_normalized_sha256":crlf_hash,
                "disk_matches_expected":sha(data)==expected,
                "lf_matches_expected":lf_hash==expected,
                "crlf_matches_expected":crlf_hash==expected}
        findings.append(record)
    classification="UNRESOLVED_SOURCE_AUTHORITY"
    if any(x["lf_matches_expected"] or x["crlf_matches_expected"] for x in findings):
        classification="POSSIBLE_NEWLINE_SERIALIZATION_MISMATCH"
    elif any(x["disk_matches_expected"] for x in findings):
        classification="DISK_SOURCE_MATCHES_EXPECTED"
    result={"state":"C_SOURCE_AUTHORITY_ANALYSIS","classification":classification,
            "candidate_id":summary.get("candidate_id"),"version":summary.get("version"),
            "expected":expected,"actual":actual,"evidence":findings,
            "authorized_to_modify_source":False,"authorized_to_override_hash":False,
            "next":"Keep existing C authority check enforced. Investigate generated-source serialization in the existing C build before authorizing any repair."}
    out=root/"source_authority_analysis.json"
    out.write_text(json.dumps(result,indent=2),encoding="utf-8")
    return result
if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser();p.add_argument("--run-root",required=True);a=p.parse_args()
    print(json.dumps(diagnose(a.run_root),indent=2))
