# Factory OS — State Map（Odoo 19 原生状态 vs Factory OS 执行状态）

Date: 2026-09-07（Phase 0 r2）
Authorities: 开发计划 §6/§7/§25 · system-invariants #2/#7/#12 · configuration-schema（基础订单执行/健康度字段）
原则：**不修改、不替代 Odoo 原生 state**；Factory OS 的执行/健康度/Gate/风险使用独立字段与枚举（不变量 #2）。本文件是两套状态的权威对照表。

## 1. 原生状态枚举（实测 `ir.model.fields.selection`，DB factory_phase0_r2）

| 模型 | 字段 | 取值（value = label） |
|---|---|---|
| sale.order | state | draft=Quotation · sent=Quotation Sent · sale=Sales Order · cancel=Cancelled |
| purchase.order | state | draft=RFQ · sent=RFQ Sent · to approve=To Approve · purchase=Purchase Order · cancel=Cancelled |
| stock.picking | state | draft=Draft · waiting=Waiting Another Operation · confirmed=Waiting · assigned=Ready · done=Done · cancel=Cancelled |
| stock.move | state | draft=New · waiting=Waiting Another Move · confirmed=Waiting · partially_available=Partially Available · assigned=Available · done=Done · cancel=Cancelled |
| mrp.production | state | draft=Draft · confirmed=Confirmed · progress=In Progress · to_close=To Close · done=Done · cancel=Cancelled |
| mrp.workorder | state | blocked=Blocked · ready=To Do · progress=In Progress · done=Finished · cancel=Cancelled |
| product.template | type | consu=Goods · service=Service · combo=Combo |
| product.template | tracking | serial · lot · none |
| sale.order.line | qty_delivered_method | manual · analytic · stock_move |

行为锚点（native-behavior-audit.md）：SO/PO 确认 → picking 的初始状态与产品类型/路线有关（storable/plain→delivery/incoming picking confirmed/assigned；service→无）；MO 手工确认 → confirmed，其 move raw/finished=assigned。

## 2. 双轨状态设计（开发计划 §6 权威化）

禁止用 `sale.order.state` 表达 Material Check / Production / QC / Ready to Ship（开发计划 L384-397）。两套状态：

```text
Odoo Transaction State（原生，只表达交易生命周期）
+
Factory Execution State（factory_os_orders 独立字段，sale.order 扩展）
```

| 文档状态 | 例 |
|---|---|
| sale.order.state | sale |
| Factory Execution（factory_execution_state） | production |
| Health（factory_health） | yellow |

字段承载（configuration-schema「基础订单执行字段」段，**始终可用、不依赖 MRP**）：`factory_execution_state`、`factory_manual_progress`、`factory_estimated_completion_date`、`factory_committed_date`（承诺交期 Gate，不变量 #12）、备注/附件。

## 3. 各域状态映射建议（冻结方向，Phase 1-6 细化）

| 域 | 原生状态（reuse） | Factory OS 扩展（extend / derived） | 说明 |
|---|---|---|---|
| 销售 | sale.order.state（draft/sent/sale/cancel） | factory_execution_state、健康度、committed/requested date | ADR-003 分离；execution 值域按 dev plan §6 需求设计（Phase 2 Gate 定稿） |
| 采购 | purchase.order.state | factory 采购执行视图（读原生 state + 关联 picking/MO） | 不新增平行状态 |
| 库存收货/发货 | stock.picking.state / stock.move.state | 发货业务层状态（见下） | picking state 只读展示 |
| 发货 | stock.picking.state | **业务层枚举（新增字段）**：PREPARING / READY_TO_SHIP / SHIPPED / DELIVERED（开发计划 L1012-1023） | 不替代原生；READY_TO_SHIP 触发条件 = 成品质检 Gate PASS（不变量 #6，启用质量时） |
| 制造 | mrp.production.state（draft/confirmed/progress/to_close/done/cancel） | factory 生产视图聚合；进度量 = qty_produced 等原生量 | 直接使用原生；"生产进度"服务层派生 |
| 工序 | mrp.workorder.state（blocked/ready/progress/done/cancel） | operations UI 透传 | operations_enabled 时才显示 |
| 健康度 | — | **全系统统一枚举**：正常 / 预警 / 风险（不变量 #7 唯一语义+固定颜色） | 派生引擎输入：承诺交期、料况、采购 ETA、生产进度、QC、发货（开发计划 §7） |
| Risk Code | — | 枚举化（非自由文本）：MATERIAL_SHORTAGE / PURCHASE_LATE / PRODUCTION_NOT_STARTED / PRODUCTION_LATE / QC_HOLD / QC_FAILED / SHIPMENT_LATE / DELIVERY_LATE（开发计划 L479-490） | 初始集 |
| 质量 | —（Community 无 quality） | factory.quality.inspection.state + factory.quality.ncr.state（thin，Phase 5 定稿） | 不变量 #5/#6 Gate 用 |

## 4. 禁止项（回归护栏）

- 任何按钮/导入/RPC 不得写原生 `state` 表达工厂OS业务阶段（改原生 state 属架构级变更，须先改不变量/ADR）。
- Health 不等于业务阶段：严重质检失败不可映射为正常/预警（不变量 #7）。
- 执行字段只在具体动作时必填（Just-in-Time Validation，不变量 #15），如 Confirmed/Active 前必须有 committed date。
