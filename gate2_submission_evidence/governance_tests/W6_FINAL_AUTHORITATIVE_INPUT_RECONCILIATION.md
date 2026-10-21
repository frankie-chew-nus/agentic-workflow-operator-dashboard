# W6 Final Authoritative-Input Reconciliation — Operator Worksheet

**Status: OPEN / NOT APPROVED**  
**Branch:** `fix/w6-b-governance-controls`  
**Baseline:** `w6_live_input_readiness.json` — all four controls HOLD.

This worksheet is for **real evidence reconciliation**, not synthetic approvals. No field below is pre-approved.

## T04 — Resources

| Input | Evidence available | Required closure |
|---|---|---|
| OHLC | 354,130 valid chronological XAUUSD M1 rows, dataset SHA-256 `f3f94246e582f5ca548454f0be324ec38ac4b59f349dfedc6a2fa9b28ac3d1b3` | Confirm authorized dataset and execution location |
| ATR | Python implementation references found | Identify authoritative function, ATR formula/lookback/warmup and verify against controlled examples |
| Previous_Day_OHLC | B-003 implementation references found | Identify session boundary/timezone and verify aggregation against controlled examples |

**Operator approval:** PENDING. Source references are not proof of correct runtime computation.

## T05 — Dependencies

Approved policy definition: `T05_OPERATOR_POLICY_APPROVAL_2026-10-21.md`.  
Recorded Week 10 clarification: `BLACK_BOX_CLARIFICATION_V1`.

**Required:** Inventory actual imports and runtime dependencies of the active B and C implementation; distinguish permitted inspectable local computation from prohibited opaque/remote material strategy computation. Unknown/dynamic dependencies HOLD for review.

**Inventory evidence:** PENDING. **Operator approval:** PENDING.

## T09 — Commission release ledger

Current B corrected-release artifacts (2) are `B_CORRECTED_AWAITING_HUMAN_RELEASE` and **must not be counted as authorized releases**.

| Required field | Status |
|---|---|
| Commission identifier and definition | PENDING |
| Distinct candidate release events | PENDING |
| Human B→C release decision IDs | PENDING |
| Immutable release artifact hashes | PENDING |
| Reconciliation of historical release count | PENDING |

**Do not infer zero releases from absent records.** Unknown history => HOLD.

## T10 — Human governance-rule authority

Approved policy definition: `T09_T10_OPERATOR_POLICY_APPROVAL_2026-10-21.md`.

**Required:** Identify an independent Operator-controlled decision register; record policy versions/hashes, decision ID, date, reviewer and verification method. Conversational approvals to policy definitions do not authenticate future policy-change decisions.

**Trusted decision register:** PENDING. **Authentication method:** PENDING.

## Closure criteria

- [ ] T04 resource contracts verified and inventory approved.
- [ ] T05 actual dependency inventory reviewed and approved.
- [ ] T09 historical commission release count reconciled with real decision evidence.
- [ ] T10 independent Human decision provenance established.
- [ ] Re-run fail-closed readiness audit using verified inputs.
- [ ] Disposable full-path integration and existing regression suite pass.
- [ ] Separate Human approval before any active B adapter change.

**No active B changes, database writes, strategy changes, or D/E authority changes are authorized by this worksheet.**
