"""Build review-only dashboard copy with local PIN + file-backed governance.

Does not edit gate2.py or databases. Activation requires a separate explicit step.
"""
from pathlib import Path
from make_disposable_b_dashboard_guard import ORIGINAL
from build_disposable_pin_dashboard_integrated import PIN_FIELD,FORM_MARKER,FORM_TAIL,FORM_PIN
REPLACEMENT="""elif d=='RELEASE_TO_C':
                import os,json
                from pathlib import Path
                from b_local_operator_release import release
                config_path=os.environ.get('GATE2_LOCAL_APPROVAL_CONFIG')
                try:
                    cfg=json.loads(Path(config_path).read_text(encoding='utf-8')) if config_path else {}
                except (OSError,ValueError,TypeError):
                    cfg={}
                result=release(c,cid,r['id'],f.get('pin',[''])[0],
                    cfg.get('pin_record'),cfg.get('evidence_manifest'),
                    enabled=cfg.get('enabled') is True)
                if result['state']!='RELEASED':
                    c.execute("UPDATE candidates SET detail=? WHERE id=?",
                        ('B governance HOLD: '+result.get('reason','UNKNOWN'),cid))"""
def build(source,destination):
 source=Path(source).resolve();destination=Path(destination).resolve()
 if destination.parent.name!="w6_disposable_dashboard" or source==destination:
  raise ValueError("DISPOSABLE_PATH_REQUIRED")
 code=source.read_text(encoding="utf-8")
 if code.count(ORIGINAL)!=1 or code.count(FORM_MARKER)!=1:
  raise ValueError("SOURCE_CHANGED_FAIL_CLOSED")
 updated=code.replace(ORIGINAL,REPLACEMENT)
 head,tail=updated.split(FORM_MARKER,1)
 form,rest=tail.split('\ndef stage_body(',1)
 if form.count(FORM_TAIL)!=1:raise ValueError("FORM_CHANGED_FAIL_CLOSED")
 updated=head+FORM_MARKER+form.replace(FORM_TAIL,FORM_PIN)+'\ndef stage_body('+rest
 compile(updated,str(destination),"exec")
 destination.parent.mkdir(parents=True,exist_ok=True)
 destination.write_text(updated,encoding="utf-8")
 return destination
