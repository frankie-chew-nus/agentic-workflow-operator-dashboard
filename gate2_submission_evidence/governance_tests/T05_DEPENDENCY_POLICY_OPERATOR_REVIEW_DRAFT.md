# T05 — B Dependency Policy for Operator Review

**Status: DRAFT — NOT APPROVED**  
**Scope:** B candidate dependency admission only. This document is not an active policy, release authorization, or strategy change.

## 1. Existing Human clarification

Decision reference: `BLACK_BOX_CLARIFICATION_V1` (Week 10). Recorded rule:

> Locally inspectable, traceable and reproducible computation is permitted; opaque/remote material strategy computation is prohibited.

The source record identifies standard library, NumPy, and pandas as allowed examples, and records `performance_evidence_seen: false`. The original decision record does not itself establish active B-stage enforcement or independently authenticated approval provenance.

## 2. Proposed admission rules

| Category | Proposed B decision |
|---|---|
| Python standard library, NumPy, pandas | Eligible for approval when locally inspectable, traceable and reproducible |
| Opaque or remote material strategy computation | HOLD / prohibited |
| Unlisted libraries, dynamic imports or unclear external services | HOLD for explicit Operator review |
| Martingale, Grid, Averaging-down, Machine Learning | Preserve frozen candidate-register prohibitions; do not silently grant exceptions |
| No dependency declaration or unverified provenance | HOLD until reviewed |

**Clarification:** An allowlisted library name alone is insufficient if the actual computation is opaque or remote. A static AST import scan is only one layer of evidence and does not prove absence of dynamic imports or network access.

## 3. Acceptance criteria before integration

1. Human Operator approves the precise dependency inventory and policy version.
2. B candidate dependencies are explicitly declared and compared against the approved policy.
3. T05 negative test: prohibited opaque/remote computation yields HOLD before B advancement.
4. T05 positive test: inspectable approved local computation proceeds only to the existing subsequent checks.
5. Missing/ambiguous dependencies fail closed.
6. Existing candidate-register restrictions, strategy logic, SQLite evidence, and D/E authority remain unchanged.
7. All changes are tested in a disposable environment before a separate active-integration approval.

## 4. Existing evidence (not proof of B deployment)

- Week 10 `operator_dependency_clarification.json` — Human clarification record.
- Week 10 `c_orchestrator_v3.py` — C-stage AST dependency checker and routing logic.
- `w10_c_dependency_static_result.json` — 3/3 static dependency checks passed.
- `w10_c_dependency_hold_routing_result.json` — 3/3 routing inspection checks passed.
- `w6_active_b_t04_t05_t09_t10_findings.json` — original active B boundary gaps.
- `w6_final_experimental_regression.json` — 74/74 experimental tests passed, not production certification.

## 5. Human decision record — pending

- Decision: **NOT YET RECORDED**
- Operator approval ID: **PENDING**
- Approval timestamp: **PENDING**
- Policy file SHA-256: **To be recorded at approval**
- Active B deployment: **NOT AUTHORIZED**

**Requested decision:** Approve this T05 policy definition only, subject to trusted dependency inventory and later integration tests. This does not authorize active deployment or release to C.
