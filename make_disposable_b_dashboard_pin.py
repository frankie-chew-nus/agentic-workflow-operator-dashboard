"""Disposable gate2.py copy only. PIN read from HTTP form, never persisted."""
from pathlib import Path
from make_disposable_b_dashboard_guard import ORIGINAL
REPLACEMENT="""elif d=='RELEASE_TO_C':
                from b_disposable_pin_transaction import attempt
                from b_disposable_authority_fixture import context_for, TRUSTED_KEYS, PIN_RECORD, REVOKED
                pin=f.get('pin',[''])[0]
                gate=attempt(c,cid,r['id'],pin,PIN_RECORD,context_for(cid,r['id']),TRUSTED_KEYS,revoked=REVOKED,disposable=True)
                if gate['state']!='DISPOSABLE_RELEASED':
                    c.execute("UPDATE candidates SET detail=? WHERE id=?",('B governance HOLD: '+gate.get('reason','UNKNOWN'),cid))"""
def make_pin_copy(source,destination):
 source=Path(source).resolve();destination=Path(destination).resolve()
 if destination.parent.name!="w6_disposable_dashboard" or source==destination:raise ValueError("DISPOSABLE_PATH_REQUIRED")
 code=source.read_text(encoding="utf-8")
 if code.count(ORIGINAL)!=1:raise ValueError("RELEASE_BRANCH_CHANGED")
 patched=code.replace(ORIGINAL,REPLACEMENT)
 compile(patched,str(destination),"exec")
 destination.parent.mkdir(parents=True,exist_ok=True)
 destination.write_text(patched,encoding="utf-8")
 return destination
