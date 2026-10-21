# T09 + T10 Governance Policy — Operator Review

**Status: DRAFT — NOT APPROVED**  
**Scope:** B governance policy definitions only. No retrospective release authorization, active integration, or D/E authority.

## T09 — Commission candidate-release ceiling

**Proposed rule:** A research commission may have no more than **three distinct Human-authorized B→C candidate releases**. The limit is enforced from an Operator-controlled, reconciled release ledger, not candidate-provided counts.

A release record must include: research commission ID, candidate ID/version, Human release decision reference, timestamp, immutable artifact reference and SHA-256, and verified provenance. Corrections and repeated attempts must be distinguished from distinct candidate releases. Records in `B_CORRECTED_AWAITING_HUMAN_RELEASE` do **not** count as approved B→C releases.

**Fail-closed:** Missing commission linkage, incomplete release history, unverified Human decisions, duplicates, or an already-reached limit => `GOVERNANCE_HOLD` pending Operator review. No retrospective approvals may be invented.

**Known gap:** The existing two B corrected-release artifacts lack commission IDs and explicit Human B→C release decisions. An authoritative historical release ledger has **not** been established. A synthetic ledger passed its tests, but is not production authority.

## T10 — Human-only governance-policy changes

**Proposed rule:** Governance rules may be changed only by an explicitly authorized Human Operator. Each change must record old/new policy versions and SHA-256, a decision ID, time, actor identity, reason and an independently verifiable decision source.

**Fail-closed:** AI-authored approvals, unregistered decisions, altered hashes, missing prior-policy provenance, or ambiguous authority => `GOVERNANCE_HOLD`. Neither a candidate's declaration nor a matching hash authenticates Human identity.

**Immutable restrictions:** The three-candidate ceiling and D/E production restrictions cannot be silently relaxed through B policy edits. Any proposal to change these boundaries requires a separate higher-level governance decision and is outside this T10 approval.

**Known gap:** The existing B SQLite `decisions` table contains RETURN_TO_B/RETRY_B entries, but no verified policy-change authority. The experimental T10 gate passed synthetic tests only.

## Operator decision requested

- [ ] Approve T09 **policy definition only**, subject to verified release history and a commission-linked ledger.
- [ ] Approve T10 **policy definition only**, subject to independent Human authorization verification.

**Explicit exclusions:** No live ledger is approved, no historic release is retroactively authorized, no active B integration or merge into `main` is authorized, and no strategy or production authority changes are permitted.

**Status:** BOTH POLICY DEFINITIONS AWAIT HUMAN APPROVAL.
