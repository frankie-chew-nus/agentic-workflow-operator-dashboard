import json,tempfile,unittest
from pathlib import Path
from c_stage1_interface import validate

MODULE='''def parameter_schema(): return {"lookback_period":[5,10],"breakout_buffer":[.05,.2],"trailing_atr_multiplier":[1.5,3.0]}
def prepare(history): return {}
def signal(history,prepared,params): return 0
'''
class InterfaceTests(unittest.TestCase):
    def fixture(self,runner,params=None):
        d=tempfile.TemporaryDirectory();root=Path(d.name);rel=root/"release";rel.mkdir()
        (rel/"strategy_module.py").write_text(MODULE)
        (rel/"implementation_release.json").write_text(json.dumps({"module":"strategy_module.py","module_sha256":"a"*64}))
        params=params or {"lookback_period":5,"breakout_buffer":.05,"trailing_atr_multiplier":1.5}
        (root/"plan.json").write_text(json.dumps({"variants":[{"parameters":params}]}))
        (root/"runner.py").write_text(runner)
        return d,rel/"implementation_release.json",root/"plan.json",root/"runner.py"
    def test_old_signal_interface_blocks(self):
        d,r,p,x=self.fixture('sig=m.signal_at(i,prepared,par)\npar["lookback_period"]')
        try:self.assertFalse(validate(r,p,x)["safe_to_run"])
        finally:d.cleanup()
    def test_runner_extra_parameter_blocks(self):
        d,r,p,x=self.fixture('prefix=bars[:i+1];prepared_i=m.prepare(prefix);sig=m.signal(prefix,prepared_i,par)\npar["atr_period"]')
        try:
            out=validate(r,p,x);self.assertFalse(out["safe_to_run"]);self.assertFalse(out["checks"]["runner_parameter_keys_available"])
        finally:d.cleanup()
    def test_matching_contract_ready(self):
        d,r,p,x=self.fixture('prefix=bars[:i+1];prepared_i=m.prepare(prefix);sig=m.signal(prefix,prepared_i,par)\npar["lookback_period"]')
        try:self.assertTrue(validate(r,p,x)["safe_to_run"])
        finally:d.cleanup()
if __name__=="__main__":unittest.main()
