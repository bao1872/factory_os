# ADR-002 Odoo `stock.*` Is the Only Inventory Source of Truth

Status: Accepted
Date: 2026-09-07

## Context

PRD 早期模型清单（§35）曾出现 `factory.inventory`、`factory.stock_move` 等建议名，同时 PRD §36 立即声明"优先扩展 Odoo 原生对象"。若建立任何可独立写入数量的库存表，会出现"Odoo 库存"与"工厂OS 库存"两本账，且没有任何同步机制能长期保证它们一致——这是开发计划 §10 明确指出的不必要一致性风险。

既有权威依据：

- system-invariants #3：在手、预留、可用、移动与批次数量只来自 `stock.*`；禁止可独立修改数量的平行库存表；
- 开发计划 §10-12：Material Shortage 用 computed service + report model，不持久化成第二套 MRP；库存原则禁止 `factory.inventory` / `factory.inventory_transaction`；
- PRD §36：优先复用 `stock.move`、`stock.picking`、`stock.lot`。

## Decision

- Odoo `stock.quant` / `stock.move` / `stock.move.line` / `stock.picking` / `stock.lot` / `stock.warehouse.orderpoint` 是**唯一库存事实源**；
- 工厂OS 只开发读取/操作原生库存对象的简化页面与服务，不创建可独立修改数量的平行库存模型；
- 简单库存展示、Dashboard 库存数字、缺料计算均为 **read / derived** 层，从 `stock.*` 实时计算；
- 任何需要"记录但不影响库存"的处置路径都被禁止（质量不合格必须进入受控处置，见 system-invariants #5）。

## Alternatives Considered

- **自建库存台账表**：被否。双写一致性无法保证；库存是正确性敏感数据，任何平行账本都会使"哪个是真相"永久模糊。
- **持久化 Material Requirement 业务单据**：被否（开发计划 §10）。库存/PO/MO 变化时同步义务落在应用侧，形成无归属的一致性风险；用计算服务替代。

## Consequences

- 工厂OS 不拥有独立的"库存引擎"，其库存能力上限 = Odoo 原生库存能力；Phase 0 必须验证这些原生行为（收货、领料、盘点、Lot）符合预期后才冻结映射；
- 派生层（Dashboard、缺料、追溯）永远只读，天然避免第二份业务事实；
- 未来若需库存高级能力，只能通过扩展 Odoo 库存对象实现，不另起炉灶。

## Invariants / Authorities Affected

- 引用：system-invariants #3（库存单一事实源）、#4（真实追溯）；configuration-schema 库存与生产段（`product_tracking` 等走原生 `product.template.tracking`）；开发计划 §10-12。
- 本 ADR 的"不可伪造历史库存"语义与 ADR-004 渐进采用相互支撑。

## Verification

- Phase 3 Supply Gate：真实 BOM 端到端后，任何数量都能从 `stock.*` 复核；
- 代码审查与 governance-audit：不存在可独立写数量的平行库存模型；
- 不合格处置测试（Phase 5）：FAIL 后无 `record_only` 路径，全部进入受控处置。

## Supersedes / Superseded By

- Supersedes：PRD §35 中 `factory.inventory` / `factory.stock_move` / `factory.lot` 等"第一阶段建议模型"表述（以本 ADR + 开发计划为准）。
- Superseded By：None。
