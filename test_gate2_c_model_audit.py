"""Read-only source and mock-only endpoint tests; no provider, strategy or Stage 1 calls."""
import ast, importlib.util, json, os, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parent
C=ROOT/'gate2_c_controller'
B=ROOT/'gate2_operator_app_v1'

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

class GovernanceAuditTests(unittest.TestCase):
    def test_compile_is_not_import_allowlist(self):
        build=(C/'build_candidate_v2.py').read_text(encoding='utf-8')
        self.assertIn('py_compile.compile',build)
        self.assertNotIn('ast.parse(',build)
        self.assertIsNotNone(compile('import os\nimport urllib.request\ndef signal(*a): return 0\n','<synthetic>','exec'))
    def test_released_module_is_imported_in_process(self):
        for p in (C/'release_semantic_gate.py',C/'stage1_runner_v3.py',ROOT/'c_stage1_interface.py'):
            self.assertIn('exec_module(',p.read_text(encoding='utf-8'),str(p))
    def test_composer_has_no_runner_write_reference(self):
        s=(C/'build_candidate_v2.py').read_text(encoding='utf-8')
        self.assertNotIn('stage1_runner_v3.py',s)
        self.assertIn('ws/f"strategy_module_r{rev}.py"',s)
    def test_semantic_gate_checks_are_bounded(self):
        s=(C/'release_semantic_gate.py').read_text(encoding='utf-8')
        for x in ('DETERMINISTIC','HISTORY_NOT_MUTATED','OUT_OF_RANGE_','IDENTITY','PARAMETER_NAMES'):
            self.assertIn(x,s)
        self.assertNotIn('llm_review(',s)
    def test_gateway_blocks_strategy_terms_but_not_enforced_runtime_sandbox(self):
        core=load('c_audit_core',C/'c_controller.py')
        reg=json.loads((C/'config/agent_registry.json').read_text(encoding='utf-8'))
        self.assertEqual(core.classify({'instruction':'rolling_mean values period'},reg)[0],'GREEN')
        self.assertEqual(core.classify({'instruction':'rolling_mean values period XAUUSD'},reg)[0],'RED')
        self.assertEqual(core.classify({'instruction':'rolling_mean values period https://example.invalid'},reg)[0],'RED')
    def test_endpoint_missing_config_fails_closed(self):
        model=load('b_audit_endpoint',B/'model_endpoint.py')
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'.env';p.write_text('MODEL_BASE_URL=https://example.invalid/v1\nMODEL_NAME=fake\n')
            with self.assertRaises(RuntimeError):model.endpoint_config(p)
    def test_endpoint_openai_switch_mock_no_network(self):
        model=load('b_audit_endpoint2',B/'model_endpoint.py')
        cfg={'base_url':'https://example.invalid/v1','model':'synthetic-model','api_key':'synthetic','protocol':'openai'}
        with patch.object(model,'_request',return_value={'choices':[{'message':{'content':'ok'}}]}) as req:
            output,protocol=model.chat(cfg,[{'role':'user','content':'synthetic'}])
        self.assertEqual((output,protocol),('ok','openai_compatible'))
        self.assertTrue(req.call_args.args[0].endswith('/chat/completions'))
        self.assertEqual(req.call_args.args[2]['model'],'synthetic-model')
    def test_endpoint_unsupported_protocol_fails_closed(self):
        model=load('b_audit_endpoint3',B/'model_endpoint.py')
        cfg={'base_url':'https://example.invalid','model':'fake','api_key':'synthetic','protocol':'auto'}
        with patch.object(model,'_request') as req:
            with self.assertRaises(RuntimeError):model.chat(cfg,[])
            req.assert_not_called()
    def test_c_model_agent_config_without_env_holds(self):
        core=load('c_audit_core2',C/'c_controller.py')
        reg=json.loads((C/'config/agent_registry.json').read_text(encoding='utf-8'))
        with patch.dict(os.environ,{},clear=True):
            with self.assertRaises(SystemExit):core.agent(reg,'orchestrator')
    def test_c_model_chat_openai_compatible_mock(self):
        core=load('c_audit_core3',C/'c_controller.py')
        class Response:
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def read(self):return b'{}'
        with patch.object(core.urllib.request,'urlopen',return_value=Response()) as urlopen:
            core.call('https://example.invalid/v1','fake',[{'role':'user','content':'synthetic'}],None,timeout=1)
        request=urlopen.call_args.args[0]
        self.assertEqual(request.full_url,'https://example.invalid/v1/chat/completions')
        self.assertEqual(json.loads(request.data)['model'],'fake')

if __name__=='__main__':unittest.main()
