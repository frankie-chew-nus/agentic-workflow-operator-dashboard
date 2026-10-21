"""Local PIN enrollment and evidence checklist scaffold, outside repository.

Does not mark controls VERIFIED or enable release. No PIN printed or committed.
"""
import argparse,getpass,json
from pathlib import Path
from b_disposable_pin_authority import enroll
def main():
 p=argparse.ArgumentParser();p.add_argument("--directory",required=True);p.add_argument("--candidate",default="CAND-B-002");p.add_argument("--version",default="v2.1.2");p.add_argument("--research",default="RES-XAUUSD")
 a=p.parse_args();root=Path(a.directory).resolve();root.mkdir(parents=True,exist_ok=True)
 config=root/"local_approval_config.json";manifest=root/"governance_manifest.json"
 if config.exists() or manifest.exists():raise SystemExit("Existing configuration detected; refusing overwrite")
 pin=getpass.getpass("Choose local approval PIN (6-12 digits): ")
 confirm=getpass.getpass("Confirm PIN: ")
 if pin!=confirm:raise SystemExit("PIN confirmation mismatch")
 record=enroll(pin);del pin,confirm
 evidence={"candidate_id":a.candidate,"candidate_version":a.version,"research_id":a.research,
  "operator_approved":False,"controls":{x:{"status":"HOLD","file":"","sha256":""} for x in ("T04","T05","T09","T10")}}
 manifest.write_text(json.dumps(evidence,indent=2)+"\n",encoding="utf-8")
 config.write_text(json.dumps({"enabled":False,"pin_record":record,"evidence_manifest":str(manifest)},indent=2)+"\n",encoding="utf-8")
 print("Local config:",config)
 print("Evidence manifest:",manifest)
 print("Release disabled until all evidence is verified and explicitly approved.")
if __name__=="__main__":main()
