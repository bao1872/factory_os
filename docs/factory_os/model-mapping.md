# Factory OS — Phase 0 Model Mapping（Odoo 19 Community）

Date: 2026-09-07（Phase 0 r2 复核）
Authorities: 开发计划 §39/§40 · PRD §35/§36 · ADR-001 ~ ADR-005 · system-invariants.md
Scope: 验证与技术映射，**不含业务实现**。本文件冻结"PRD 业务对象 → Odoo 原生模型 → 动作分类"的映射，供 Phase 1+ 作为建模与 ACL 验收依据。

## 1. 验证环境（Evidence）

- 代码库：`odoo-19/`（Odoo 19.0 FINAL，`odoo/release.py:15` `version_info = (19, 0, 0, FINAL, 0, '')`；638 个 addons，无 enterprise 目录）。
- 运行实例：PostgreSQL 17（/tmp:5432，socket+TCP），全新数据库 `factory_phase0_r2`，安装模块 72 个（实测 `ir.module.module state=installed`；含 sale、sale_management、stock、purchase、mrp 及桥接模块 sale_stock/purchase_stock/purchase_mrp/sale_mrp/sale_purchase/stock_account/mrp_account/delivery/stock_delivery/sales_team）。
- Community 关键缺口（实测）：`quality*`（quality/quality_control/quality_mrp）**不存在**；`procurement.group` 模型已移除；`mrp_workorder` 已并入 `mrp`（workorder 模型仍为 `mrp.workorder`）；无持久化 `stock.inventory`/`stock.count`（盘点改为基于 `stock.quant` 的向导流，见 addon-dependency-map / native-behavior-audit）。
- 未做任何自定义：本映射只引用原生模型与官方数据文件，未修改任何 addon。

## 2. 动作分类词汇

| 分类 | 含义 | 判定标准 |
|---|---|---|
| REUSE | 直接用原生模型/字段，不写模型代码 | 原生已覆盖业务对象语义 |
| EXTEND | 继承原生模型加字段/方法/菜单（`_inherit`） | 需要工厂OS业务字段或流程钩子 |
| THIN CUSTOM | 新建轻量模型（每对象 ≤2 个模型） | 原生无等价物且不复制整套原生域 |
| DERIVED | 只读计算/报表/服务，不落业务事实 | 数据必须实时来自原生事实源 |
| DEFERRED | 冻结到后续 Phase（明确阶段） | 依赖未就绪的 addon/连接器 |
| REJECTED | 禁止实现为独立事实源 | 被不变量/ADR 排除（平行库存/平行生产等） |

## 3. PRD §35 核心对象逐条映射

| # | PRD Object（§35） | Native / Factory OS 目标 | Action | 依据与证据 |
|---|---|---|---|---|
| 1 | factory.customer | `res.partner`（+factory_os_core 轻分类字段） | REUSE（thin ext） | 开发计划 L203-210：不建立 factory.customer；客户仍是 res.partner。customer_code 等字段属 Phase1 core 扩展 |
| 2 | factory.supplier | `res.partner`（同上） | REUSE（thin ext） | 同上；采购角色经 `seller_ids`/company_type |
| 3 | factory.product | `product.template` / `product.product` | EXTEND | 开发计划 L214-238（factory_revision/factory_active 等）；先 field-mapping audit 防同义字段 |
| 4 | factory.bom | `mrp.bom` / `mrp.bom.line` | REUSE | 开发计划 L96-97、§14 直接使用；正式 MRP 能力属 factory_os_production（ADR-003） |
| 5 | factory.sales_order | `sale.order` | EXTEND | 开发计划 §5、L340+ 增加工厂OS字段 |
| 6 | factory.sales_order_line | `sale.order.line` | EXTEND | 同上 |
| 7 | factory.purchase_order | `purchase.order` | EXTEND | 开发计划 §8/§9 |
| 8 | factory.purchase_order_line | `purchase.order.line` | EXTEND | 同上 |
| 9 | factory.inventory | **禁止平行表**；事实= `stock.quant`/`stock.move(.line)`/`stock.picking` | REJECTED as table + REUSE 原生 | ADR-002；system-invariants #3；开发计划 §12。19 盘点经 quant 向导（stock.request_count 等），无 stock.inventory 持久模型 |
| 10 | factory.stock_move | `stock.move` / `stock.move.line` | REJECTED as table + REUSE | ADR-002；19 中 stock.move 无 `name`、有 `origin`/`sale_line_id`/`purchase_line_id`/`production_id`/`raw_material_production_id`（实测 `_fields`） |
| 11 | factory.lot | `stock.lot` + `product.template.tracking`(serial/lot/none) | REJECTED as table + REUSE | ADR-002；tracking selection 实测 product_template.py L846-852 |
| 12 | factory.production_order | 正式：`mrp.production`（REUSE/EXTEND）；简单执行：`sale.order` 执行字段（见 #附加） | REJECTED as parallel 生产单；REUSE native MO | 开发计划 L111、ADR-003（两套状态，禁平行生产订单模型） |
| 13 | factory.production_operation | `mrp.workorder` | EXTEND | 开发计划 §2 L98、§14 L690；operations_enabled 属 quality? 见 configuration-schema L71（需 formal MRP） |
| 14 | factory.inspection | Community 无 `quality.*` → 自建薄模型 `factory.quality.inspection` | THIN CUSTOM | 开发计划 §19-§20 实测无 quality addon → 走"当前没有 Quality"路径 L875-884 |
| 15 | factory.ncr | 薄模型 `factory.quality.ncr`（NCR workflow 字段） | THIN CUSTOM（新建） | 开发计划 L923+；system-invariants #5/#6 语义由其消费 |
| 16 | factory.shipment | `stock.picking` + factory_os_delivery 字段 | REUSE + EXTEND | 开发计划 L983-1008（第一版不建 factory.shipment；扩展 stock.picking） |
| 17 | factory.shared_supply_order | 中央交易平台域（connector 外发/接收） | DEFERRED | 开发计划 §8 之外/PRD §34 guardrail；factory_os_connector Phase 8 定义，非 Phase 1-7 |
| 18 | factory.audit_log | `mail.message` tracking + `ir.logging` + factory_os_core 审计服务 | THIN CUSTOM（core） | system-invariants #10（Who/What/When/Before/After 强制审计），Phase 1 落地 |

## 4. 附加业务概念映射（PRD/开发计划/不变量出现，§35 未列或需扩展解释）

| 业务概念 | 目标 | Action | 依据/证据 |
|---|---|---|---|
| 客户/供应商角色与分类 | res.partner + factory_partner_type/customer_code/supplier_code | EXTEND | 开发计划 L192-210 |
| 报价单→销售订单 | sale.order.state draft/sent/sale | REUSE | SEL 实测：draft/sent/sale/cancel |
| 承诺交期 committed date | sale.order 扩展字段（factory_committed_date 等） | EXTEND | system-invariants #12；configuration-schema"基础订单执行字段"段 |
| 简单订单执行状态/进度 | sale.order 扩展（execution_state/manual_progress/estimated_completion_date） | EXTEND | ADR-003；configuration-schema 基础订单执行段；不依赖 BOM/MO/库存 |
| 执行健康度 | 独立 computed/service（正常/预警/风险） | DERIVED | system-invariants #2/#7；不写原生 state |
| 发货交付业务层状态 | stock.picking 扩展字段（PREPARING/READY_TO_SHIP/SHIPPED/DELIVERED） | EXTEND | 开发计划 L1012-1023；不替代原生 picking state |
| 收货 | stock.picking（incoming）+ button_validate | REUSE | 测试 B（见 native-behavior-audit） |
| 补货/再订购 | stock.warehouse.orderpoint + stock.rule | REUSE | 模型实测存在；缺料引擎不得持久化第二套（开发计划 §10） |
| Material Shortage | computed service over stock.quant/orderpoint/move 需求 | DERIVED | 开发计划 §10-§12；ADR-002 Consequences |
| 追溯/族谱 | stock.move.line→stock.lot→production 链 + `stock.traceability.report` | DERIVED + REUSE | 开发计划 L1027-1047；19 Community 自带 stock.traceability.report（stock/report/stock_traceability.py:22） |
| 报废 | `stock.scrap` | REUSE | 开发计划 §14 L692；stock_scrap.py:11 |
| 工作中心 | `mrp.workcenter` | REUSE | 开发计划 L99 |
| 班组/岗位 | mrp.workcenter 或 partner/team 扩展（待 Phase1 细化） | EXTEND（thin） | 无原生"班组"业务对象；禁止造平行 ERP 实体 |
| 设备/PLC/SCADA/OEE | — | REJECTED（MVP 外） | PRD §34 Scope Guardrail；system-invariants 无要求 |
| Dashboard 数字 | 服务层只读聚合 | DERIVED | 开发计划 §29（Dashboard 不存业务数据） |
| Connector 同步/共享供应 | factory_os_connector（outbox/idempotency） | THIN CUSTOM/DEFERRED | 开发计划 §33-§37、Phase 8 |
| 离线事务 | — | REJECTED | ADR-005；不变量 #13 |
| 一人多角色/权限 | res.users + res.groups 映射 | REUSE | 开发计划 §4 权限角色（L241+） |
| 批次/序列 | product.template.tracking + stock.lot | REUSE | tracking serial/lot/none 实测 |

## 5. PRD §35 建议模型名决议汇总（冻结）

1. `factory.inventory` / `factory.stock_move` / `factory.lot`：**不得实现为可独立写数量的平行库存表**（system-invariants #3 + ADR-002；Phase 0 不重开此裁决）。库存事实一律 `stock.*`。
2. `factory.customer` / `factory.supplier`：不建，复用 `res.partner`（开发计划 L203-210）。
3. `factory.product` / `factory.bom`：不建，复用并扩展 `product.template(.product)` / `mrp.bom(.line)`。
4. `factory.sales_order(_line)` / `factory.purchase_order(_line)`：不建，扩展 `sale.order(.line)` / `purchase.order(.line)`。
5. `factory.production_order` / `factory.production_operation`：不建平行生产单；正式 MO 走 `mrp.production`/`mrp.workorder`（ADR-003；开发计划 L111）。
6. `factory.inspection` / `factory.ncr`：Community 无原生 quality → **允许新建** `factory.quality.inspection` / `factory.quality.ncr`（thin，仅两模型，开发计划 §20 无 Quality 路径）。
7. `factory.shipment`：不建，扩展 `stock.picking`。
8. `factory.shared_supply_order`：DEFERRED（connector/中央域，Phase 8）。
9. `factory.audit_log`：不建平行日志域；以原生 mail/ir.logging + core 审计服务实现不变量 #10。

## 6. 边界与后续

- 本文件不修改任何 PRD/开发计划/配置权威；被 §39 冻结的 5 份配置文档（configuration-matrix/schema/dependency-graph/system-invariants/progressive-adoption）保持原文。
- "QC 原生映射"随本文件冻结为 THIN CUSTOM（Community 无 quality addon 证据见 addon-dependency-map.md §3）。
- 未完成"每项不变量 → 模型约束/服务校验/ACL/测试用例"的逐条映射前，不进入 Phase 1（开发计划 §39 L1422）。
