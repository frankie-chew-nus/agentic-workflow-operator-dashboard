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
FORM_MARKER="def form_buttons(buttons,placeholder='Human rationale'):"
FORM_TAIL="bs+'</form>'"
FORM_PIN="("+repr(PIN_FIELD)+" if any(v=='RELEASE_TO_C' for v,lbl in buttons) else '')+bs+'</form>'"

def build(source,destination):
 source=Path(source).resolve();destination=Path(destination).resolve()
 if destination.parent.name!="w6_disposable_dashboard" or source==destination:
  raise ValueError("DISPOSABLE_PATH_REQUIRED")
 code=source.read_text(encoding="utf-8")
 if code.count(ORIGINAL)!=1 or code.count(FORM_MARKER)!=1:
  raise ValueError("DASHBOARD_SOURCE_CHANGED_FAIL_CLOSED")
 updated=code.replace(ORIGINAL,RELEASE_BRANCH)
 head,tail=updated.split(FORM_MARKER,1)
 form,rest=tail.split('\ndef stage_body(',1)
 if form.count(FORM_TAIL)!=1:raise ValueError('FORM_CHANGED_FAIL_CLOSED')
 form=form.replace(FORM_TAIL,FORM_PIN)
 updated=head+FORM_MARKER+form+'\ndef stage_body('+rest)
 compile(updated,str(destination),"exec")
 destination.parent.mkdir(parents=True,exist_ok=True)
 destination.write_text(updated,encoding="utf-8")
 return destination
