# Agentic Workflow Operator Dashboard

Gate 2 operator dashboard.

## Development workflow

- `main` is the reviewed milestone branch.
- Active development happens on feature branches.
- Current feature branch: `fix/stage-owned-journey-renderer`.
- Local `evidence/`, `.env`, and credentials are never committed.

## Current branch milestone

The stage-owned journey renderer makes A→E the authoritative UI structure:

- stage-specific RUNNING / REVIEW / SYSTEM_HOLD / GOVERNANCE_HOLD panels render inside their owning stage;
- Candidate Pipeline and Human Decision Ledger remain below the journey;
- B correction-regression is translated to GOVERNANCE_HOLD;
- B revision contract diagnostics show failed rules and previous/attempted specifications.

The backend still expects the already-tested local B helper files and sibling `gate2_c_controller` environment used by the current workstation.
