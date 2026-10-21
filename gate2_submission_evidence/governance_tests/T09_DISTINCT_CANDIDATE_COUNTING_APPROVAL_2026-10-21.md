# T09 Counting Interpretation — Human Decision Record

**Decision:** APPROVED — COUNTING INTERPRETATION ONLY  
**Recorded date:** 2026-10-21  
**Reference:** `T09_DISTINCT_CANDIDATE_COUNTING_APPROVAL_2026-10-21`

The Human Operator replied **"Approved"** to the explicit question:

> Should the three-candidate limit apply to each research commission's distinct candidates authorized to enter C, counting each candidate only once even if it undergoes multiple corrections or retries?

## Approved interpretation

1. Apply the ceiling **per research commission**.
2. Count **distinct candidates with verified Human authorization to enter C**.
3. Count each such candidate **once**, regardless of corrections, retries or repeat authorization records for the same candidate.
4. Do not count `B_CORRECTED_AWAITING_HUMAN_RELEASE` artifacts as Human-authorized releases.
5. When commission linkage, release authorization or historical completeness is unverified, **HOLD** rather than assume zero.
6. No more than three distinct candidates may be authorized to enter C under the same commission.

## Scope limitations

This approval clarifies counting semantics; it **does not** establish a verified release ledger, authorize historical releases, change production authority, approve active B integration or modify the existing SQLite database. It is a conversational decision record, not independent identity authentication.

**Status:** COUNTING_RULE_APPROVED; LEDGER_RECONCILIATION_PENDING; ACTIVE_INTEGRATION_NOT_AUTHORIZED.
