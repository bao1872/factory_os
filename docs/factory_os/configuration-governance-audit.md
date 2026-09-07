# Configuration Governance Consistency Audit

Date: 2026-09-07  
Scope: documentation and UI governance only; no business code was implemented.

## Delta

- Added implementation-level `configuration-schema.md` with stable technical keys, Odoo storage, field types/selections, exact defaults, constraints, groups, dependency behavior, audit mechanism and consuming services.
- Added `configuration-dependency-graph.md` with `requires`, `visible_if`, incompatibilities, `BLOCK`, `AUTO_DISABLE`, `HIDE_KEEP` and `ENABLE_REQUIRED` behavior.
- Split rejected inventory disposition from NCR creation policy; removed every `record_only` path.
- Added the v0.1 network-failure invariant and replaced the active mobile design with `24-mobile-confirmation-and-network-failure-v2.png`.
- Separated 70-page design coverage from development authorization and mapped it to exactly 22 MVP work surfaces.
- Added authority-document order to README and linked the Schema/dependency specifications from PRD, development plan and UI review.

## Results

| Check | Result | Evidence |
|---|---|---|
| PRD ↔ configuration matrix/schema | PASS | PRD authority block links directory, technical schema and dependency graph; Schema covers all configurable matrix domains. |
| PRD ↔ system invariants | PASS | PRD explicitly delegates tenant, native state, stock truth, QC Gate, security, Connector privacy, network failure and audit. |
| Development plan ↔ configuration schema | PASS | Phase 0 now requires matrix, Schema, dependency graph and invariants before Phase 1. |
| UI settings ↔ configuration schema | PASS | UI 25 is active; C-class items are read-only protection summaries; product tracking is not a company toggle. |
| UI coverage ↔ MVP scope | PASS | 70/70 is explicitly Design Coverage; development matrix defines priorities and exactly Core surface 01–22. |
| Historical UI 15 inactive | PASS | UI review and coverage matrix label 15 historical; active setting baseline is 25. |
| Historical offline board inactive | PASS | Old 24 is historical; active baseline is network-failure-v2 and matches the manual-Retry invariant. |
| No global batch/lot setting | PASS | Schema uses native `product.template.tracking` only; the sole company-level mention is an explicit prohibition. |
| No disable switch for audit, tenant isolation or stock truth | PASS | These are C-class invariants with no technical setting key or Settings proxy. |
| Connector privacy cannot be disabled | PASS | Field allowlist plus permanent denylist; no “share all” value exists. |
| Reject inventory vs NCR policy | PASS | `reject_inventory_disposition` and `ncr_creation_policy` are separate; all rejects require controlled inventory disposition. |
| Dependency-disabled behavior | PASS | Dependency graph fixes blocking vs automatic UI-only cascade and provides the error contract. |
| Markdown/patch consistency | PASS | `git diff --check` returns no errors. |

## Gate decision

**Configuration Governance Gate: COMPLETE.**

This decision authorizes Phase 0 technical audit only. It does not authorize implementation of all designed pages or Post-MVP/Phase 8 items. If Phase 0 discovers an Odoo 19 Community model incompatibility, update the Schema through a reviewed governance change before implementation.
