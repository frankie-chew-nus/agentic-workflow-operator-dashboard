# B Governance Activation — Operator Decision Checklist (DRAFT)

**Status: NOT APPROVED. No activation authorized.**

This is the final trusted-input and activation gate for T04/T05/T09/T10. Experimental tests passed 74/74, but no live B integration has occurred. Do not use synthetic fixtures as live authority.

## Operator decisions required

| Control | Proposed source / decision | Current status | Acceptance evidence |
|---|---|---|---|
| T04 resource availability | Operator-approved inventory of resources actually available to B/C, including data source identity, ATR calculation and previous-day OHLC if required | UNVERIFIED | Dated approval, resource verification evidence, SHA-256 |
| T05 dependencies | Apply Human clarification `BLACK_BOX_CLARIFICATION_V1`: inspectable local computation may be permitted; opaque/remote material strategy computation prohibited | CLARIFICATION RECORDED; B ENFORCEMENT UNVERIFIED | Human-approved allowlist and negative/positive integration tests |
| T09 commission limit | Verified commission ID and actual Human-authorized B→C release events, distinct from `B_CORRECTED_AWAITING_HUMAN_RELEASE` | NO AUTHORITATIVE LEDGER | Reconciled event ledger with Human decision IDs and immutable release artifacts |
| T10 rule changes | Human-only approval bound to old/new policy hashes; independent verification of decision origin | AUTHENTICATION NOT ESTABLISHED | Operator decision record, policy hashes, trusted decision registry |

## Stop conditions

- Any missing or unverifiable source above => HOLD; do not auto-approve.
- No use of candidate-provided release counts or self-declared Human approvals.
- No modification of active `b_resume.py`, active SQLite, strategy code, or D/E authority without a separate, explicit Operator decision.
- Do not merge into `main` before real-input verification, disposable full-path regression, and rollback validation.
- Preserve original T04/T05/T09/T10 FAIL evidence and the 74/74 experimental PASS record separately.

## Decision to be recorded by Human Operator

- [ ] Approve specific T04 inventory and source evidence.
- [ ] Approve T05 dependency policy and allowed components.
- [ ] Reconcile T09 historical releases and approve the commission ledger.
- [ ] Establish T10 independent Human decision verification.
- [ ] Authorize **disposable integration only** after all above are verified.
- [ ] Separately authorize any later activation or merge.

**No boxes are prechecked.** Approval must be explicitly recorded by the Operator; creating this document does not constitute approval.
