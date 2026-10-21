"""Build a usable PIN-protected dashboard COPY for isolated testing only.

Never modifies active gate2.py. The signer key, approval record and PIN hash
must be supplied by a trusted local host fixture; no production authority.
"""
from pathlib import Path
from make_disposable_b_dashboard_guard import ORIGINAL

PIN_FIELD='<label for="release-pin">B to C approval PIN (6-12 digits)</label><input id="release-pin" name="pin" type="password" inputmode="numeric" minlength="6" maxlength="12" autocomplete="off" required>'
RELEASE_BRANCH="""elif d=='RELEASE_TO_C':
                from b_disposable_pin_atomic import attempt
                from b_disposable_authority_fixture import context_for, TRUSTED_KEYS, PIN_RECORD, REVOKED
                result=attempt(c,cid,r['id'],f.get('pin',[''])[0],PIN_RECORD,
                               context_for(cid,r['id']),TRUSTED_KEYS,revoked=REVOKED,disposable=True)
                if result['state']!='DISPOSABLE_RELEASED':
                    c.execute("UPDATE candidates SET detail=? WHERE id=?",
                              ('B governance HOLD: '+result.get('reason','UNKNOWN'),cid))"""
FORM_ORIGINAL="return '<form method=post action=/decide><textarea name=rationale required minlength=12 placeholder="'+html.escape(placeholder)+'"></textarea><input type=hidden name=candidate value=CAND-B-002>'+bs+'</form>'"
FORM_REPLACEMENT="return '<form method=post action=/decide><textarea name=rationale required minlength=12 placeholder="'+html.escape(placeholder)+'"></textarea><input type=hidden name=candidate value=CAND-B-002>'+("+repr(PIN_FIELD)+" if any(v=='RELEASE_TO_C' for v,lbl in buttons) else '')+bs+'</form>'"
def build(source,destination):
 source=Path(source).resolve();destination=Path(destination).resolve()
 if destination.parent.name!="w6_disposable_dashboard" or source==destination:
  raise ValueError("DISPOSABLE_PATH_REQUIRED")
 code=source.read_text(encoding="utf-8")
 if code.count(ORIGINAL)!=1 or code.count(FORM_ORIGINAL)!=1:
  raise ValueError("DASHBOARD_SOURCE_CHANGED_FAIL_CLOSED")
 updated=code.replace(ORIGINAL,RELEASE_BRANCH).replace(FORM_ORIGINAL,FORM_REPLACEMENT)
 compile(updated,str(destination),"exec")
 destination.parent.mkdir(parents=True,exist_ok=True)
 destination.write_text(updated,encoding="utf-8")
 return destination
