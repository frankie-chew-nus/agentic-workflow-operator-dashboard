# T04 — Resource Availability Policy for Operator Review

**Status: DRAFT — NOT APPROVED**  
**Scope:** B candidate resource admission. No strategy change, live adapter integration, or C/D/E release authority.

## 1. Required resources from frozen candidate register

| Candidate | Declared required inputs |
|---|---|
| CAND-B-001 | Open, High, Low, Close, ATR |
| CAND-B-002 | High, Low, Close, ATR |
| CAND-B-003 | High, Low, Close, Open, Previous_Day_OHLC |

## 2. Existing evidence and limits

- Local historical file: `data/stage1_xauusd_m1.csv`, reported 21,460,427 bytes. Its MT5-style header includes date/time, OHLC, tick volume, volume and spread, separated by tabs despite the `.csv` suffix.
- Header existence **does not** verify complete rows, numeric values, chronology, data lineage, file hash, timeframe coverage, or actual runtime availability.
- ATR and Previous_Day_OHLC are **derived resources**, not columns in the observed header.
- Source-code references to ATR were discovered in C, but calculation correctness and actual execution availability have **not** been verified.
- C token/resource ledgers record model consumption, **not** approval of market-data resources.

## 3. Proposed fail-closed T04 rule

A candidate may advance from B resource preflight only when **every required input** is supported by an Operator-approved, versioned resource inventory. The inventory must record:

1. Resource identifier and candidate(s) requiring it.
2. Authoritative provider or local dataset identity, location and SHA-256.
3. Availability and integrity check result with timestamp.
4. For derived inputs: calculation/aggregation contract, input prerequisites, relevant timeframe and tested implementation reference.
5. Human approval reference and inventory version.

If any required resource is absent, stale, unverified, mismatched or not approved, the preflight returns **GOVERNANCE_HOLD**. A candidate's self-declared resource availability is never authority. The B gate must not silently substitute data or infer ATR/previous-day availability from OHLC headers.

## 4. Verification required before approval

- [ ] Verify tab-delimited OHLC dataset rows, timestamps, timeframe and source SHA-256 without modifying data.
- [ ] Confirm authorized source location and intended B/C execution environment.
- [ ] Verify ATR definition, lookback/warmup and deterministic implementation against the approved contract.
- [ ] Verify Previous_Day_OHLC session/day boundary, timezone and aggregation against the approved contract.
- [ ] Record a versioned inventory and explicit Operator approval.
- [ ] Test missing/corrupt/unavailable resources => HOLD, valid resources => eligible for subsequent checks only.
- [ ] Run disposable B integration and regression; preserve original T04 failure evidence.

## 5. Decision requested

**Approve the proposed T04 resource-admission rule in principle**, while retaining `DRAFT_NOT_APPROVED` for the actual inventory until the checks above are complete.

This approval would cover policy definition only, not claims that resources are already available, active B deployment, or release to C.

**Operator approval:** PENDING  
**Active integration:** NOT AUTHORIZED  
**Production authority:** UNCHANGED
