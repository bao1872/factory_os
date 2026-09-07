# Progressive Adoption Gate Audit

Date: 2026-09-07  
Scope: authority documents, configuration specification and UI design only. No business code was started.

## Modified authority documents

- PRD: added Progressive Adoption and Just-in-Time Validation; replaced dual mandatory dates with optional Requested + state-gated Committed date.
- Development Plan: separated simple order execution from formal MRP and added Phase 0 verification/Gates.
- Configuration Matrix/Schema: changed raw defaults to Safe Minimal, renamed formal capability to `mrp_production_enabled`, added base order execution fields.
- Dependency Graph: formal MRP dependencies no longer govern order-level manual execution.
- System Invariants: added progressive adoption, Committed Date and JIT validation boundaries.
- Progressive Adoption: added six-question wizard mapping, four presets and the no-data-migration upgrade path.
- UI Review/Coverage: activated 25-v3 and demoted the technical onboarding portion of 25-v2.

## Schema delta

| Area | Before | After |
|---|---|---|
| Raw modules | Most capabilities on | Sales only; purchasing/inventory/MRP/quality/delivery/reports/connector off |
| Production flag | `production_enabled` ambiguous | `mrp_production_enabled` means formal MO/BOM only |
| Base execution | Implicitly tied to production | `factory_execution_state`, manual progress, estimated completion, notes/attachments always available |
| Dates | Requested + Confirmed required | Committed required only at active transition; Requested optional |
| Quality | Three inspections and final Gate on | Quality, inspections and Gates off; wizard adds final-only/full/traceable presets |
| Mobile | Three workbenches on | All off until relevant workflow selected |
| Packaging | All fields on | Empty raw selection; validate at export action when needed |

## Invariant delta

- Advanced capabilities add constraints only to applicable actions and new transactions.
- Historic orders are never rewritten into MO, stock, QC or traceability records.
- Draft delivery date may be TBD; active execution always has Committed Delivery Date.
- Optional master data is validated just in time, not on first record creation.
- Odoo `stock.*` remains the only inventory truth; simple inventory is presentation only.

## Wizard and preset evidence

The full six-step answer-to-atomic-setting mapping and four preset table are authoritative in [`progressive-adoption.md`](progressive-adoption.md). No `management_level`, `maturity_level`, preset field or numeric level exists in the runtime Schema. One user maps to any allowed combination of built-in groups.

## Upgrade path

`订单看板 → 订单+进销存 → 标准生产 → 质量追溯` operates on the same `res.partner`, `product.template` and `sale.order` history. New stock actions use `stock.*`; new formal production uses `mrp.production`; tracking is set per product. Old records remain truthful and are not backfilled automatically.

## Consistency results

| Check | Result |
|---|---|
| Small factory can start with customer + product + quantity + committed date | PASS |
| Order execution works with MRP, inventory and quality off | PASS |
| Formal MRP still requires inventory and BOM capability | PASS |
| Requested date optional; Committed date gated at active transition | PASS |
| Raw defaults match Safe Minimal | PASS |
| Quality final-only and full mappings are explicit | PASS |
| Presets expand only to atomic settings | PASS |
| One person can receive multiple roles | PASS |
| Nonessential master data is not globally required | PASS |
| Simple inventory never creates a parallel stock engine | PASS |
| Existing privacy, audit, reject/NCR, product tracking and dependency rules preserved | PASS |
| Active onboarding UI uses real-world language | PASS |

## Gate decision

**Progressive Adoption Gate: COMPLETE.**

This permits Phase 0 technical audit. It does not permit assumptions about Odoo 19 Community MO/BOM implementation before that audit and does not expand the 22-surface MVP scope.
