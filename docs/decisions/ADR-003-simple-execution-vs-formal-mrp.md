# ADR-003 Simple Order Execution Is Separate from Formal MRP

Status: Accepted
Date: 2026-09-07

## Context

小工厂可能长期不需要 BOM/库存/MO，只需要"订单做到哪一步"的人工执行记录。若简单执行依赖正式 MRP 能力，则 Safe Minimal 起步（PRD §0.2、progressive-adoption）不成立；若把人工执行进度与 MO 生产混为同一业务对象，则开启 MRP 后无法区分"人工记录"与"真实生产事务"。

既有权威依据：

- system-invariants #2：`sale.order` 原生状态只表达交易生命周期，执行/健康度/Gate 用独立字段；#14 渐进采用；
- 开发计划 §6：Odoo Transaction State 与 Factory Execution State 是两套状态；§13：`factory_os_production` 才是正式 MRP/MO；
- configuration-schema "基础订单执行字段"段：`factory_execution_state` / `factory_manual_progress` / `factory_estimated_completion_date` 始终可用，不依赖 `mrp_production_enabled`；MRP 关闭时不生成 MO/stock.move/BOM 消耗；
- progressive-adoption 永久原则：简单订单执行属 `factory_os_orders`，正式 MO/BOM 属 `factory_os_production`，两者不得混为同一业务对象。

## Decision

- **简单订单执行**（`sale.order.factory_execution_state`、人工进度、预计完成、备注/附件）属 `factory_os_orders`，是**始终可用的基础能力**，不依赖 BOM、库存或 MO；
- **正式 MRP/MO**（`mrp.production` / `mrp.workorder` / `mrp.bom` 消耗）属 `factory_os_production`，是独立的高级能力；
- 两者不得混为同一业务对象，不得创建平行生产订单模型；
- MRP 开启后，只对**适用的新动作**增加约束；历史订单不迁移、不重写（与 ADR-004 一致）；
- MRP 关闭时人工进度绝不生成 MO、物料需求或库存事务。

## Alternatives Considered

- **人工执行进度即"简化版 MO"**：被否。会使"有没有真实生产事务"失去语义；开启 MRP 后历史数据无法干净地区分。
- **用 `sale.order.state` 表达执行阶段**：被否（开发计划 §6）。会破坏 Odoo 原生交易工作流语义，违反不变量 #2。

## Consequences

- Safe Minimal 下可完成"客户+产品+数量+承诺交期+人工执行进度"的订单看板闭环（Phase 2 Gate）；
- UI 必须同时显示交易状态与执行状态且不混淆（UI authority 已锁定此规则）；
- 缺料/追溯/质量等能力在 MRP 关闭时自然不可用，避免出现"人工进度假装生产事实"。

## Invariants / Authorities Affected

- 引用：system-invariants #2、#14；configuration-schema 基础订单执行字段段；progressive-adoption 永久原则；开发计划 §6、§13、§40 模型映射。
- 该分离是配置依赖图"简单执行字段不受 `mrp_production_enabled` 控制"的依据。

## Verification

- Phase 2 Gate：无库存/MO/QC 的订单执行闭环 PASS；
- 测试：MRP 关闭时人工报进度不产生任何 `mrp.production` / `stock.move` 记录；
- 测试：MRP 开启后历史订单不被改写（Phase 4 回归）。

## Supersedes / Superseded By

- Supersedes：任何把订单级执行与正式 MRP 绑定的隐含假设（如早期"生产单=订单进度"的表述，现以本 ADR 为准）。
- Superseded By：None。
