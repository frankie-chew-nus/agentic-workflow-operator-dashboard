"""Move local approval configuration into the 5002 project safely.

Copies only (never deletes originals), refuses overwrite, rewrites the manifest
pointer to the copied manifest, and preserves disabled release state.
No PIN is printed; no active dashboard or DB is modified.
"""
import argparse,json,shutil
from pathlib import Path
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--project-root",required=True)
 p.add_argument("--old-dir",default=str(Path.home()/"MSI5002_Local_Approval"))
 a=p.parse_args()
 root=Path(a.project_root).resolve(strict=True)
 old=Path(a.old_dir).resolve(strict=True)
 new=root/"Local_Approval"
 if old==new:
  print("Already inside 5002:",new);return
 src_cfg=old/"local_approval_config.json"
 src_manifest=old/"governance_manifest.json"
 if not src_cfg.is_file() or not src_manifest.is_file():raise SystemExit("SOURCE_CONFIG_OR_MANIFEST_MISSING")
 new.mkdir(parents=True,exist_ok=True)
 dest_cfg=new/src_cfg.name;dest_manifest=new/src_manifest.name
 if dest_cfg.exists() or dest_manifest.exists():raise SystemExit("DESTINATION_EXISTS_REFUSE_OVERWRITE")
 cfg=json.loads(src_cfg.read_text(encoding="utf-8"))
 manifest=json.loads(src_manifest.read_text(encoding="utf-8"))
 if not isinstance(cfg.get("pin_record"),dict):raise SystemExit("PIN_RECORD_MISSING")
 if cfg.get("enabled") is True:raise SystemExit("ACTIVE_APPROVAL_CONFIG_REQUIRES_MANUAL_REVIEW")
 # The original manifest remains unchanged. New copy remains HOLD.
 manifest["operator_approved"]=False
 for record in manifest.get("controls",{}).values():
  if isinstance(record,dict):record["status"]="HOLD"
 dest_manifest.write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
 cfg["enabled"]=False
 cfg["evidence_manifest"]=str(dest_manifest)
 dest_cfg.write_text(json.dumps(cfg,indent=2)+"\n",encoding="utf-8")
 print("New config:",dest_cfg)
 print("New manifest:",dest_manifest)
 print("Originals preserved:",old)
 print("Release remains DISABLED. Do not commit PIN configuration to GitHub.")
if __name__=="__main__":main()
