# W6 Governance Evidence Consolidation — T01–T10

**Project:** MSI5002 Operator Dashboard  
**Evidence cutoff:** 18 October 2026  
**Branch:** `test/w6-governance-scenarios`  
**Purpose:** Gate 2 evidence index, not production authorization.

## Evidence classification

The original W6.3 T01–T10 record reports **10/10 PASS on synthetic paper walkthroughs**. Those outcomes were not executable software tests.

Subsequent local Python tests exercised two limited implementation surfaces: the **historical B v2 checker** (`../gate2_build_v03B2/b_v2.py`) and the repository's **`workflow_matrix.allowed` transition guard**. The two surfaces are not equivalent to the full current B→C workflow. No trading-strategy qualification or production D/E authority is inferred.

## Claim-to-test matrix

| W6 ID | W6 scenario | Executable observation | Evidentiary status |
|---|---|---|---|
| T01 | Ordinary release | Historical B candidate check accepted a valid synthetic specification; transition guard allowed `READY_FOR_C` with authority flag | **PARTIAL PASS** — complete release chain not tested |
| T02 | Ambiguous specification | Historical B checker flagged signed-body ambiguity | **PARTIAL PASS** — specific ambiguity class |
| T03 | Grounding failure | Historical B checker flagged `SRC-X-099`; transition guard also blocked test evidence kind | **PARTIAL PASS** — specific source reference |
| T04 | Missing resource | Historical B checker returned no failures for unavailable test library | **FAIL (historical checker)** — resource-availability enforcement absent in tested function |
| T05 | Prohibited black-box | Historical B checker returned no failures for opaque service dependency | **FAIL (historical checker)** — actual dependency use not blocked by tested function |
| T06 | Missing Human release | Transition guard returned `HUMAN_AUTHORITY_HOLD` with `human=False` | **PARTIAL PASS** — flag-based guard, not complete decision ledger |
| T07 | Human silence | Guard held on repeated `human=False` calls | **PARTIAL PASS** — no real elapsed-time, reminder or persisted-state test |
| T08 | Corrected version | Guard held on identity/hash mismatch | **PARTIAL PASS** — no v1 preservation, v2 recheck or lineage test |
| T09 | Fourth candidate | Guard authorized request despite synthetic prior-release count of three; count not supplied to guard | **COVERAGE GAP** — full commission-limit enforcement not established |
| T10 | Unauthorized rule change | Guard authorized request despite synthetic AI rule-change scenario; actor/change not supplied to guard | **COVERAGE GAP** — full policy-change enforcement not established |

## Preserved executable evidence

| Evidence file | Result | Scope |
|---|---|---|
| `w6_t01_t03_result.json` | 3/3 executable tests PASS | Historical B checker, T01–T03 |
| `w6_t04_t05_findings.json` | 2/2 enforcement failures reproduced | Historical B checker, T04–T05 |
| `w6_t06_t10_result.json` | 5/5 executable checks PASS | Transition guard; T09/T10 are coverage-audit checks, not enforcement PASS |
| `w6_t09_t10_findings.json` | 2/2 negative tests failed as designed | Transition-guard coverage gaps for T09/T10 |

All four records are under `gate2_submission_evidence/governance_tests/`. They include local run metadata, test/checker hashes, and sanitized result summaries. Raw-log hashes in these records refer to the captured local output; sanitized summaries are not byte-identical substitutes for the raw logs.

## Interpretation and unresolved work

1. **What passed:** Several bounded checks for source grounding, known ambiguity, authority flags, identity and hashes.
2. **What failed:** The historical B checker did not detect unavailable resources or opaque external dependencies in the tested synthetic candidates.
3. **What remains unverified:** Full current B→C end-to-end enforcement of T01–T10, including commission-level counting, rule-change provenance, reminders, correction lineage and Human decision persistence.
4. **Action:** Preserve original failures. If remediation is authorized, test the relevant current enforcement functions separately and compare before/after results. Do not rewrite historical evidence or silently change strategy logic.

**Governance rule:** The registry records what the evidence proves; it never upgrades the evidence.  
**Production authority:** None.
