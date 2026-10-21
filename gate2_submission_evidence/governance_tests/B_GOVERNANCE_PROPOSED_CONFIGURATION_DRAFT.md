# Proposed B Governance Configuration — Operator Review Only

**Status: DRAFT_NOT_APPROVED**  
**Scope:** T04, T05, T09, T10. **No active integration or production authority.**

## T04 — Resource inventory

**Proposed required data:** Open, High, Low, Close, ATR, Previous_Day_OHLC (from the frozen B candidate register).

**Evidence:** Local `data/stage1_xauusd_m1.csv` is an MT5-style tab-separated file with date/time/OHLC columns; ATR and previous-day OHLC are derived, not present as columns. Runtime computation and availability remain unverified.

**Operator action:** Verify source file provenance/hash, row integrity and date coverage, actual ATR calculation, previous-day aggregation and each candidate's requirements. Approve an inventory only after these checks. Until then, HOLD.

## T05 — Dependency policy

**Existing Human clarification:** `BLACK_BOX_CLARIFICATION_V1`: locally inspectable, traceable and reproducible computation permitted; opaque/remote material strategy computation prohibited. Examples: standard library, NumPy, pandas. Frozen register separately prohibits Martingale, Grid, Averaging-down and Machine Learning.

**Proposed B rule:** Require explicit dependency declarations and review against an Operator-approved inventory; block opaque remote computation and unapproved dependencies. Do not silently reinterpret the frozen strategy prohibitions. The Week 10 C-stage static gate passed targeted tests but does not establish active B enforcement or detect every dynamic dependency.

**Operator action:** Approve the exact B allowlist, prohibited classes and exception handling. Until then, HOLD.

## T09 — Commission release ledger

**Evidence:** Two `B_CORRECTED_RELEASE` artifacts are in `B_CORRECTED_AWAITING_HUMAN_RELEASE` state; neither contains an explicit Human B→C release decision or commission ID. They cannot be counted as actual releases.

**Proposed ledger fields:** commission_id, candidate_id, candidate_version, Human release decision ID, decision timestamp, immutable release artifact hash, source record reference, verification status.

**Proposed rule:** Maximum three distinct Human-authorized B→C candidate releases per commission; no candidate-supplied counts. Fail closed when historical release history cannot be reconciled. Never backfill approvals by assumption.

**Operator action:** Reconcile historical releases from authoritative records, identify the commission, verify decisions and approve the ledger. Until then, HOLD.

## T10 — Governance-rule changes

**Proposed rule:** Human-only approval, with previous/new policy hashes, decision ID, timestamp, verified Operator identity, and independent trusted decision registry. Reject candidate/agent-declared authority. No expansion of the three-candidate limit or D/E production authority through this B policy.

**Operator action:** Identify a trusted Human decision-recording and authentication mechanism. Hash equality alone does not authenticate a Human. Until then, HOLD.

## Activation and evidence boundaries

- The original four active B boundary failures remain preserved.
- Experimental consolidated controls and disposable integration passed their recorded tests; final experimental regression: 74/74 PASS.
- No verified authoritative live inputs yet; no active B adapter change; no merge to `main`.
- Any integration must first use disposable databases and copied adapters, run positive/negative and regression tests, and confirm rollback.
- A separate explicit Human approval is required for any active integration or activation.

## Operator review decisions (not yet made)

- [ ] T04 inventory verified and approved.
- [ ] T05 dependency policy approved.
- [ ] T09 release history reconciled and ledger approved.
- [ ] T10 Human decision authority independently verified.
- [ ] Disposable integration approved.
- [ ] Active integration separately approved.

**This document records proposals, not Human approvals or deployed controls.**
