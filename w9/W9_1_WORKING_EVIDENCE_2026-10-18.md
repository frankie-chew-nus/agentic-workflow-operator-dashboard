# W9.1 working evidence — 18 October 2026

Scope: **Week 9 W9.1 working evidence only**, not a complete Gate 2 evidence inventory. Status: evidence index and interpretation only; **not** a replacement for original records or independent verification. Core rule: evidence records what is proved, never upgrades it.

## Architecture and chronology
- A–E governance and CLI workflows preceded the dashboard. Dashboard repository initialized on 2026-10-17 (commit `3647af3`); dashboard is a usability/orchestration enhancement, not the core governance requirement.
- A/B original evidence is in local `Gate2_Evidence/03_WORKSTREAM_A` and `04_WORKSTREAM_B`, with decision collectors in `08_DECISION_RECORDS`. Original artifacts remain local until separately reviewed for safe publication.
- W9.1 eight steps: A research; A→B source approval/release; B formulation; B→C governance; C build/integrity; C Stage 1; D independent OOS; E commissioning. D/E production **not run**, isolated sandbox tests only. CSV M1 OHLC for C versus intended MT5 OOS adapter for D is an architectural separation; adapter implementation/equivalence not independently verified.

## Verified C Stage 1 artifacts (user-supplied)
- Local: `evidence/c_runs/CAND-B-002/v2.1.3/stage1_output/summary.json` and `variant_results.json`.
- Run `S1-AC3049C5FADB`: 54 variants executed, 0 signals in each, 0 performance PASS, 0 explicit FAIL, 54 Human HOLD; `advance_to_d=false` in `c_run_summary.json`.
- Elapsed 2184.235 s (~36.4 min), bounded completed history 72 bars. Full-history equivalence remains unverified; no CPC/drawdown result established.
- Summary references results SHA-256 `169b64a331c74ce127b8dc9836d1e7ded1afe02af7bd77e11ed88222c1b0543e` (source-reported hash; preserve source file).
- Interrupted earlier progress: 8000/354090 (2.3%), elapsed 329.5 s; not a completed equivalence proof.

## C build/rework economics — provisional
- 15 distinct timestamped `atomic_summary.json` records: 2 `HOLD_FOR_HUMAN`, 13 `IMPLEMENTATION_RELEASED`; release does not imply semantic PASS.
- Each of 15 `resource_summary.json` files reports 4 calls, 3585 tokens. A sample ledger shows decomposition 1058, external volatility utility 452, external trailing stop 696, integration 1379, using `gemini-3.1-flash-lite-preview`. No request IDs/timestamps; **do not claim** 15 × 3585 as verified billed consumption.
- 12 distinct semantic `repair_result.json` records report PASS and per-attempt usage. User console output: 24,732 input and 7,344 output = 32,076 total reported tokens. Check deduplication and billing before aggregation.
- API price configuration missing; monetary cost **NOT CALCULATED**.
- Human retrospective estimate given 2026-10-18: approximately 8 h/day project engagement for recent ~7 days, ~4 h/day active (~28 active hours, ~56 total engagement). Covers broad development, CLI work, dashboard, execution and assignment; **not** per-candidate run cost, not measured time tracking.

## A source approval and release — original 2026-10-12 records uploaded
- `20261012T151348531810Z_report.json`: report created, source_count=5, output `operator_review_v1.html`, SHA-256 reported `5b5c5e49b58f83b4393fada61125a7a0af5e16d93125f97ab177467dcc0e089b`.
- `20261012T152241256117Z_approve.json`: approval operation output `research_register_approved_v1.json`, source_count=5, state null; SHA-256 reported `b32bef938a3590406e53f0275669efba01b43ef46d3ac11163cb6e972c9d0cf0`. Do not infer all five approved.
- `20261012T152255553489Z_release.json`: `RELEASE`, source_count=1, output `a_to_b_release_v1.json`, SHA-256 reported `f8339c49428bfd14240a316441d75fb3ccbdae1a13f591da3c6f16c314a8a362`. The exact source identity and Human decision provenance require underlying artifact inspection.
- These JSON events show real A report/approve/release operations, not token/cost accounting or proof of independent source quality.

## D/E and governance
- D sandbox `D_SANDBOX_PASS`, E sandbox `E_COMMISSIONING_BLOCKED_TEST_ARTIFACT`. Sandbox outcomes are not OOS or commissioning authority.
- 117 automated tests passed per Operator report; sanitized Gate 2 archive v4 preserved in branch `feat/evidence-registry-v1`. Four Operator judgement narratives J01–J04 were explicitly approved in chat; approval is not independent artifact verification.
- Strategy logic must not be changed; B-002 must not be advanced past actual C evidence.

## Next evidence steps
1. Inspect actual `research_register_approved_v1.json` and `a_to_b_release_v1.json` before stating exact A admission denominator and reasons.
2. Inspect B formulation/revision artifacts and any token/time records.
3. Separate one-time development investment, per-commission operating cost, waiting, rework, and unmeasured Human time.
4. Publish only sanitized evidence or digests after privacy/proprietary-content review; never upload raw proprietary strategy code, private paths, credentials or restricted data by default.

## A approval detail verified from underlying registers (2026-10-18 review)
- Original `research_register_approved_v1.json` records 5 discovered sources; only `SRC-A-003` has `verification=VERIFIED`, `operator_decision=APPROVE`, and document verification evidence. Four others remain `PENDING`/`NOT_VERIFIED`, **not** explicit REJECT decisions.
- `a_to_b_release_v1.json`: state `RELEASE`, reason `HUMAN_APPROVED_AND_VERIFIED`, exactly one released source `SRC-A-003`; document SHA-256 `2f46c6c053afeb048ba0ed54444bc36cf14e13808604ea9ab6c651e80ae01a3d`; register SHA-256 `b32bef938a3590406e53f0275669efba01b43ef46d3ac11163cb6e972c9d0cf0`.
- Governance denominator: 1/5 admitted into B. This establishes bounded source release, not scientific validity or XAUUSD M1 generalisability. Source assessment token usage is present in approved register but billing/total A costs are not yet reconciled.

## B initial formulation — original register verified
- 2026-10-13 `20261013T023822439518Z_b_formulate.json` records 3 candidates and SHA-256 `47e987ea3599b9ea1d9d0b9d587d2e0da3256d84c937864450ea8785c2d0a65a` for `candidate_strategy_register_v1.json`.
- Register state `FORMULATED`, model `gemini-3.1-flash-lite`; `CAND-B-001` exhaustion-candle mean reversion, `CAND-B-002` NR7 breakout continuation, `CAND-B-003` pin-bar reversal. All cite approved `SRC-A-003`. These are hypotheses, not approved C releases or demonstrated profitable strategies.
- Recorded initial B usage: prompt 436, candidate output 1384, total 1820 tokens; monetary cost uncalculated. Later B revisions/usage remain to inspect.

## B v1 return and v2 executability — reviewed source records
- `b_v1_return_record.json`: `B_RETURN_FOR_CORRECTION`, `RETURN_TO_B`; all three candidates listed with specification corrections. B owns hypothesis/specification; C owns Stage 1 data, fixed 9-pip friction, execution/evaluation configuration, optimization, and performance testing. B withheld from XAUUSD M1 CSV, Stage 1 results, MT5/OOS data, and performance rankings.
- CAND-B-001: clarify absolute body/range mathematics, remove execution cost/latency assumptions, define timezone. CAND-B-002: resolve volume input vs OHLC proxy, clarify market-open language, remove execution assumptions. CAND-B-003: absolute body, pivot tolerance, remove execution assumptions.
- `b_v2_executability_check.json`: state PASS; 3/3 v2 candidate executability checks PASS, zero failures recorded. **Not** C performance PASS or evidence of strategy qualification.
- Cost impact: revision and governance work exists; elapsed Human time, revision token usage and money remain unmeasured until separate logs inspected.
