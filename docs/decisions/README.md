# Architecture Decision Records — docs/decisions/

本目录记录 Factory OS 的架构决策（ADR = Architecture Decision Record）。

## 用途

- 架构决策**一旦 Accepted，即成为架构权威**，层级高于 PRD 与开发计划（见 [governance-model](../governance/governance-model.md) 权威层级）；
- ADR 让"为什么这样设计"可检索、可复核，防止后来者凭印象推翻既有决策；
- ADR 只记录决策与依据，**引用**既有权威文档而非复制其内容。

## 状态

| 状态 | 含义 |
|---|---|
| Proposed | 已提议，未生效，无权威 |
| Accepted | 已被接受，是架构权威 |
| Superseded | 已被其他 ADR 取代，不再生效（保留供追溯） |
| Rejected | 被拒绝，不生效（保留供追溯） |

**只有 Accepted 状态是架构权威。**

## 创建新 ADR 的流程

1. 触发条件：见 [change-control.md](../governance/change-control.md#3-architectural架构变更) 的 ARCHITECTURAL 类；
2. 先 STOP → 按 [ADR-TEMPLATE.md](ADR-TEMPLATE.md) 起草，编号为下一个可用序号；
3. 用户明确授权后置为 Accepted；
4. 在相关权威文档中登记受影响条目；
5. 编号永不复用；被替代的 ADR 标记 Superseded 并链接新 ADR。

## 当前 ADR 索引

| ADR | 标题 | 状态 | 一句话决策 |
|---|---|---|---|
| [ADR-001](ADR-001-one-database-per-factory.md) | One independent Odoo database per factory | Accepted | 每工厂一个独立 Odoo 数据库；同一 codebase；差异只经配置/能力开关/主数据表达 |
| [ADR-002](ADR-002-odoo-stock-source-of-truth.md) | Odoo `stock.*` 是唯一库存真相源 | Accepted | 库存数量只来自 `stock.*`；禁止平行库存台账；派生层只读 |
| [ADR-003](ADR-003-simple-execution-vs-formal-mrp.md) | 简单订单执行与正式 MRP 分离 | Accepted | `sale.order.factory_*` 表达简单执行；正式 MO/BOM 属 `factory_os_production`；两者不混同 |
| [ADR-004](ADR-004-progressive-adoption.md) | 渐进采用：不伪造历史、不建平行模型 | Accepted | 高级能力只约束新动作；历史记录不重写、不伪造 |
| [ADR-005](ADR-005-no-offline-transactions-v0.1.md) | v0.1 无离线业务事务 | Accepted | 网络失败仅保留当前页输入、显示失败、手动 Retry；无离线队列/自动重放 |
| [ADR-006](ADR-006-capability-engine-and-addon-installation.md) | Capability 引擎 vs 原生 addon 安装 | **Accepted** | 能力等级 ↔ 原生 addon 安装 profile 绑定、单调升级（引擎型 capability 不允许 ON→OFF）；保持 8-addon（orders 去 sale_stock）；v0.1 purchasing→inventory；由 Phase 0 STOP A/B 裁决触发，2026-09-07 Accepted |

## 维护约定

- 不修改历史 Accepted ADR 的决策本身；变更以"新 ADR supersede 旧 ADR"表达；
- 每个 ADR 必须有 Verification 与受影响不变量/权威登记，否则不完整；
- 本 README 的索引表在新增/变更 ADR 时必须同步。
