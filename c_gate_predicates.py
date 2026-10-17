"""Fail-closed C stage gate predicates. No external workflow processing."""
def semantic_pass(obj):
    return (
        isinstance(obj,dict)
        and obj.get("state")=="SEMANTIC_V2_PASS"
        and type(obj.get("failure_count")) is int
        and obj["failure_count"]==0
        and isinstance(obj.get("module_sha256"),str)
        and len(obj["module_sha256"])==64
    )

def stage1_completed(obj):
    return isinstance(obj,dict) and obj.get("state")=="STAGE1_COMPLETE"
