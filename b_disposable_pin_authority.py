"""Disposable-only local PIN verifier. No production activation.

Store only salted scrypt verifier; never store or log the PIN. A PIN authenticates
knowledge of a secret, not a specific person's identity. Host must rate-limit.
"""
import hashlib,hmac,os
def enroll(pin,*,salt=None):
 if not isinstance(pin,str) or not pin.isascii() or not pin.isdecimal() or len(pin)<6 or len(pin)>12:
  raise ValueError("PIN_MUST_BE_6_TO_12_DIGITS")
 salt=os.urandom(16) if salt is None else salt
 if not isinstance(salt,bytes) or len(salt)!=16:raise ValueError("INVALID_SALT")
 digest=hashlib.scrypt(pin.encode(),salt=salt,n=2**14,r=8,p=1,dklen=32)
 return {"salt":salt.hex(),"digest":digest.hex(),"algorithm":"scrypt-n16384-r8-p1"}
def verify(pin,record):
 try:
  if not isinstance(pin,str) or not pin.isascii() or not pin.isdecimal() or len(pin)<6 or len(pin)>12:return False
  if not isinstance(record,dict) or record.get("algorithm")!="scrypt-n16384-r8-p1":return False
  salt=bytes.fromhex(record["salt"]);expected=bytes.fromhex(record["digest"])
  if len(salt)!=16 or len(expected)!=32:return False
  actual=hashlib.scrypt(pin.encode(),salt=salt,n=2**14,r=8,p=1,dklen=32)
  return hmac.compare_digest(actual,expected)
 except (ValueError,KeyError,TypeError):return False
