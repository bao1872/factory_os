# 工厂OS Odoo 模块设计与开发计划

**项目：** 工厂OS / Factory OS  
**版本：** Development Plan v0.1  
**基础平台：** Odoo 19  
**架构原则：** One Codebase + One Database per Factory Workspace + Central Connector  
**依据：** 《工厂OS PRD v0.1》

---

## 0.1 开发基线补充（2026-09-07 锁定）

开发必须同时遵循：

- [`docs/factory_os/configuration-matrix.md`](docs/factory_os/configuration-matrix.md)：A/B 类有界配置、默认值、作用域、权限、依赖与审计；
- [`docs/factory_os/configuration-schema.md`](docs/factory_os/configuration-schema.md)：技术字段名、模型、类型、selection、约束、审计和消费服务；
- [`docs/factory_os/configuration-dependency-graph.md`](docs/factory_os/configuration-dependency-graph.md)：requires、visible_if、冲突和依赖关闭行为；
- [`docs/factory_os/system-invariants.md`](docs/factory_os/system-invariants.md)：C 类正确性、安全、库存、质量、隐私与审计不变量。

这些文件不是参考材料，而是模型约束、设置页、ACL/record rules、服务层校验和自动化测试的验收依据。

渐进采用基线见 [`docs/factory_os/progressive-adoption.md`](docs/factory_os/progressive-adoption.md)：裸安装只启用销售与订单级简单执行；正式 MRP、库存、质量等能力由向导或后续设置开启。capability flags 只控制 Factory OS 能力/UI/流程，不动态安装或卸载 Odoo addons。

`factory_os_orders` 必须支持不依赖 BOM、库存和 MO 的订单级简单执行状态、人工进度、预计完成日期、备注与附件。`factory_os_production` 才代表正式 MRP/MO 能力；Phase 0 验证 Odoo 19 Community 原生 MO/BOM 行为后再冻结映射。两者不得创建平行生产订单或虚假库存事务。

---

# 1. 总体技术决策

工厂OS不重新开发 ERP。

整体架构：

```text
                    Factory OS Codebase
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   Factory A DB       Factory B DB       Factory C DB
        │                  │                  │
        └──────── Factory OS Connector ───────┘
                           │
                           ↓
                    Central Trade DB
                    / Supply Control Tower
```

核心原则：

```text
一个工厂 Workspace
=
一个独立 Odoo Database
```

每个数据库内部使用相同版本：

```text
Odoo 19
+
Factory OS Addons
```

禁止：

```text
Factory A branch
Factory B branch
Factory C branch
```

所有工厂使用同一个代码仓库。

差异只能通过：

```text
Configuration
Feature Flag
Master Data
```

解决。

---

# 2. 不重新开发的 Odoo 内核

以下能力原则上直接复用 Odoo：

| 业务能力 | Odoo 原生模型 |
|---|---|
| 客户 / 供应商 | `res.partner` |
| 产品 | `product.template` / `product.product` |
| 销售订单 | `sale.order` / `sale.order.line` |
| 采购订单 | `purchase.order` / `purchase.order.line` |
| BOM | `mrp.bom` / `mrp.bom.line` |
| 制造订单 | `mrp.production` |
| 工序 | `mrp.workorder` |
| 工作中心 | `mrp.workcenter` |
| 库存移动 | `stock.move` / `stock.move.line` |
| 收货 / 发货 | `stock.picking` |
| 实际库存 | `stock.quant` |
| Lot / Serial | `stock.lot` |
| 补货规则 | `stock.warehouse.orderpoint` |
| 报废 | `stock.scrap` |
| 用户 | `res.users` |
| 权限组 | `res.groups` |
| 附件 | `ir.attachment` |
| 消息 / Activities | `mail.thread` / `mail.activity` |

Odoo 19 原生 Manufacturing 已经支持制造订单、工序、Work Center、组件消耗以及生产排程，因此工厂OS应扩展这些模型，而不是建立 `factory.production.order` 与 Odoo MRP 平行运行。citeturn809812search0turn809812search4

---

# 3. Factory OS Addon 总体结构

第一阶段只建立 8 个正式 addon：

```text
addons/
│
├── factory_os_core
├── factory_os_orders
├── factory_os_supply
├── factory_os_production
├── factory_os_quality
├── factory_os_delivery
├── factory_os_dashboard
└── factory_os_connector
```

依赖关系：

```text
                         factory_os_core
                               │
             ┌─────────────────┼─────────────────┐
             ↓                 ↓                 ↓
     factory_os_orders   factory_os_supply   factory_os_production
             │                 │                 │
             └─────────────┬───┴─────────┬──────┘
                           ↓             ↓
                  factory_os_quality
                           │
                           ↓
                  factory_os_delivery
                           │
                           ↓
                  factory_os_dashboard
                           │
                           ↓
                  factory_os_connector
```

实际 manifest 依赖不需要机械复制这个图，而要保持最小依赖关系。

---

# 4. Module 01 — factory_os_core

## 定位

这是整个工厂OS的基础模块。

不承担销售、库存、生产业务。

负责：

```text
Factory OS identity
Security
Roles
Common fields
Common mixins
Navigation shell
Configuration
Audit foundation
```

## Odoo dependencies

```python
base
mail
web
contacts
product
```

## 扩展模型

### `res.partner`

增加轻量分类：

```text
factory_partner_type
customer_code
supplier_code
active_for_factory_os
```

不要重新建立：

```text
factory.customer
factory.supplier
```

客户和供应商仍然使用 `res.partner`。

---

### `product.template`

增加工厂OS字段：

```text
factory_revision
factory_specification
default_production_lead_days
packaging_description
factory_product_category
factory_active
```

注意：

已有 Odoo 字段必须优先复用。

开发前先进行 field mapping audit，避免出现：

```text
Odoo已有字段
+
Factory OS又创建一个同义字段
```

---

## 权限角色

建立：

```text
Factory OS / Owner
Factory OS / Sales
Factory OS / Purchasing
Factory OS / Warehouse
Factory OS / Production Manager
Factory OS / Operator
Factory OS / Quality
```

权限必须同时使用：

```text
ir.model.access
+
ir.rule
```

Odoo 的 record rule 是 access right 之后的第二层记录级限制，而且没有匹配限制规则时属于 default-allow，因此不能只靠菜单隐藏做安全控制。citeturn893773search2turn893773search3

---

## Core 配置

新增：

```text
Factory OS Settings
```

包括：

```text
Factory Name
Default Warehouse
Default Manufacturing Route
Module Toggles with Dependencies
Business-policy Thresholds
Bounded Workflow Modes
External Sync Enabled
Dashboard Risk Thresholds
```

禁止设置全局 `Lot Tracking Default`：追踪方式属于产品级字段（不追踪/批次/序列号）。禁止把租户隔离、库存真实性、安全底线、强制审计等系统不变量做成开关。设置项完整定义见配置矩阵。

---

## 明确禁止

`factory_os_core` 不允许：

```text
Sales logic
Purchase logic
MRP logic
QC logic
API integration
Dashboard aggregation
```

---

# 5. Module 02 — factory_os_orders

## 定位

解决：

> 工厂有什么客户订单，现在处于什么执行状态？

## Odoo dependencies

```python
factory_os_core
sale
sale_stock
```

## 核心模型

直接扩展：

```text
sale.order
sale.order.line
```

不创建：

```text
factory.sales_order
```

---

## `sale.order` 增加字段

优先复用 Odoo：

```text
client_order_ref
date_order
partner_id
order_line
amount_total
```

Factory OS 增加：

```text
requested_delivery_date
factory_execution_state
factory_health_state
factory_risk_code
factory_risk_message
production_progress
material_status
quality_status
delivery_status
```

其中：

```text
factory_health_state
```

采用：

```text
green
yellow
red
```

---

# 6. 一个非常重要的状态设计

禁止修改 Odoo 原生：

```text
sale.order.state
```

来表达：

```text
Material Check
Production
QC
Ready to Ship
```

原因是：

Odoo 的 `sale.order.state` 是销售交易生命周期。

工厂OS需要的是：

**Execution Lifecycle。**

因此必须是两套状态：

```text
Odoo Transaction State
+
Factory Execution State
```

例如：

```text
Sale Order state:
sale

Factory Execution:
production

Health:
yellow
```

这样不会破坏 Odoo 原生工作流。

---

# 7. Order Health Engine

这是第一个真正需要工厂OS自己开发的业务引擎。

输入：

```text
Committed Delivery Date
Material Availability
Purchase ETA
Production Progress
QC Status
Shipment Status
```

输出：

```text
Green
Yellow
Red
```

以及：

```text
Risk Code
Risk Message
```

例如：

```text
SO0267

Health:
RED

Risk:
MATERIAL_SHORTAGE

Message:
Material M203 shortage 800 pcs
```

Risk Code 必须枚举化，而不是只存文本。

初始：

```text
MATERIAL_SHORTAGE
PURCHASE_LATE
PRODUCTION_NOT_STARTED
PRODUCTION_LATE
QC_HOLD
QC_FAILED
SHIPMENT_LATE
DELIVERY_LATE
```

---

# 8. Module 03 — factory_os_supply

这个模块把：

```text
Purchasing
+
Inventory
+
Material Requirement
```

放在一起。

不要拆成两个 addon。

原因是三者的数据高度耦合。

---

## Dependencies

```python
factory_os_core
factory_os_orders
purchase
purchase_stock
stock
mrp
```

---

# 9. Purchasing

直接扩展：

```text
purchase.order
purchase.order.line
```

增加：

```text
factory_risk_state
factory_risk_code
current_eta
related_sale_order_ids
related_production_ids
```

但预计到货时间必须先检查 Odoo 原有：

```text
date_planned
```

是否已经满足需求。

避免重复字段。

---

# 10. Material Shortage Engine

这里不要建立：

```text
factory.material.requirement
```

作为第二套 MRP。

第一版应直接根据：

```text
mrp.bom
stock.quant
stock.move
mrp.production
purchase.order.line
```

计算。

核心概念：

```text
Demand
Available
Reserved
Incoming
Shortage
```

展示：

| Material | Demand | Available | Incoming | Shortage |
|---|---:|---:|---:|---:|

---

## Shortage 不一定持久化

第一版建议：

```text
computed service
+
report model
```

而不是存成独立业务单据。

否则会立即遇到：

```text
库存变化了
PO变化了
MO变化了

Material Requirement记录谁负责同步？
```

这是不必要的数据一致性风险。

---

# 11. Inventory

直接使用：

```text
stock.quant
stock.picking
stock.move
stock.move.line
stock.lot
stock.warehouse.orderpoint
```

工厂OS只开发简化页面：

```text
Stock Overview
Receiving
Material Issue
Internal Transfer
Stock Count
Lot Lookup
Low Stock
```

---

# 12. 库存原则

禁止另建：

```text
factory.inventory
factory.inventory_transaction
```

Odoo stock ledger 是唯一库存事实源：

> **Single Source of Truth。**

---

# 13. Module 04 — factory_os_production

## 定位

这是轻量 MES 层。

## Dependencies

```python
factory_os_core
factory_os_orders
factory_os_supply
mrp
stock
```

---

# 14. 核心模型

直接使用：

```text
mrp.bom
mrp.production
mrp.workorder
mrp.workcenter
stock.scrap
```

Odoo 19 的公开 MRP 实现本身包含 `mrp.workorder`、工序依赖、Work Center、生产数量等，因此这里主要做 UI 和业务解释层。citeturn809812search0turn809812search3

---

# 15. Production Order 扩展

`mrp.production` 增加：

```text
factory_health_state
factory_risk_code
related_customer_order
planned_delivery_date
factory_progress
operator_update_at
```

但是：

```text
qty_producing
qty_produced
components availability
date_start
date_finished
```

等已有字段必须继续使用 Odoo 原生数据。

---

# 16. Production Progress

系统计算：

```text
Completed Qty / Planned Qty
```

生成：

```text
0–100%
```

同时显示：

```text
Planned
Completed
Scrap
Remaining
```

Reject 不建议另外维护一个孤立字段。

不良数量应该尽量形成：

```text
stock.scrap
```

或者 Quality record。

这样库存才能正确。

---

# 17. Work Order

使用：

```text
mrp.workorder
```

表示：

```text
Assembly
Testing
Packing
```

但是第一阶段只允许简单 Routing。

不做：

```text
高级 APS
自动换线优化
复杂产能算法
设备级排程
```

---

# 18. Operator Mobile UI

这是 `factory_os_production` 最重要的自定义 UI。

不把普通 Odoo MO 页面直接给工人。

建立：

```text
Today's Production
```

Card：

```text
MO-00235

Portable Blower

Target
1000

Completed
760

Reject
12

[Update Qty]
[Report Problem]
[Complete]
```

目标：

> 一个生产更新操作不超过 3 个主要动作。

---

# 19. Module 05 — factory_os_quality

这里必须先做一个技术决策。

Odoo 19 官方 Quality 已经支持 Quality Control Point、Quality Check、制造/库存操作触发检查以及 Quality Alert。citeturn772433search0turn772433search1

但是不要在不知道当前部署版本和授权模块状态时强耦合。

因此 Phase 0 必须检查当前 Odoo：

```text
Community / Enterprise
Installed quality addons
Available quality models
```

---

# 20. Quality 两条实现路径

## 如果当前 Odoo 有原生 Quality

直接扩展：

```text
quality.check
quality.alert
quality.point
```

工厂OS主要新增：

```text
Inspection UI
NCR workflow
Severity
Root Cause
Corrective Action
Verification
Photos
```

---

## 如果当前没有 Quality

只自行建立两个薄模型：

```text
factory.quality.inspection
factory.quality.ncr
```

不要复制完整 Odoo Quality。

---

# 21. Inspection

关联：

```text
Product
Material
Lot
Stock Picking
Manufacturing Order
Work Order
```

类型：

```text
Incoming
In Process
Final
```

结果：

```text
PASS
FAIL
HOLD
```

支持照片。

Odoo Quality 本身允许检查关联 Manufacturing Order / Inventory operation，并支持 Lot/Serial，因此如果现有部署可用，优先复用。citeturn893773search1

---

# 22. NCR

必须是工厂OS自己的业务闭环：

```text
OPEN
↓
CONTAINMENT
↓
ROOT_CAUSE
↓
CORRECTIVE_ACTION
↓
VERIFICATION
↓
CLOSED
```

字段：

```text
severity
owner
problem
root_cause
corrective_action
due_date
verification
```

---

# 23. Module 06 — factory_os_delivery

这里同时负责：

```text
Delivery
+
Traceability
```

不另外拆 `factory_os_traceability`。

---

## Dependencies

```python
factory_os_orders
factory_os_production
factory_os_quality
stock
delivery
```

如果当前环境没有 `delivery` addon，则以 `stock` 为最低依赖。

---

# 24. Shipment

第一版不创建：

```text
factory.shipment
```

优先扩展：

```text
stock.picking
```

新增：

```text
carton_count
gross_weight
net_weight
cbm
forwarder
tracking_reference
pod_attachment
factory_shipment_state
```

---

# 25. Delivery 状态

不要替代 Odoo picking state。

增加业务层：

```text
PREPARING
READY_TO_SHIP
SHIPPED
DELIVERED
```

---

# 26. Traceability

这是核心能力，但原则上不建立第二份追溯表。

追溯数据已经存在：

```text
sale.order
↓
mrp.production
↓
stock.move
↓
stock.lot
↓
quality
↓
stock.picking
```

Odoo 原生已经支持制造产品的 Lot / Serial tracking。citeturn893773search8

工厂OS应该开发：

```text
Traceability Service
```

而不是：

```text
Traceability Database Copy
```

---

# 27. Traceability 页面

输入：

```text
Lot
SKU
SO
MO
PO
Shipment
```

显示关系图：

```text
Customer PO
    ↓
Sales Order
    ↓
Manufacturing Order
    ↓
Finished Lot
    ↓
Raw Material Lots
    ↓
QC
    ↓
Shipment
```

支持双向查询。

---

# 28. Module 07 — factory_os_dashboard

这是工厂OS产品体验的核心。

## Dependencies

```python
factory_os_orders
factory_os_supply
factory_os_production
factory_os_quality
factory_os_delivery
```

---

# 29. Dashboard 不存业务数据

Dashboard 只负责：

```text
Read
Aggregate
Rank
Highlight
```

不要创建：

```text
factory.dashboard.order
factory.dashboard.production
```

作为数据副本。

---

# 30. Dashboard 服务层

建议建立：

```text
factory.dashboard.service
factory.risk.service
```

或者 AbstractModel / service functions。

使用：

```text
search_read
read_group
aggregated SQL where justified
```

计算：

```text
Open Orders
Late Orders
At Risk Orders
Production In Progress
Material Shortages
QC Holds
Ready to Ship
```

---

# 31. Exception Feed

统一输出：

```text
Object Type
Object ID
Severity
Risk Code
Message
Due Date
Responsible
```

例如：

```text
SO-1034
RED
MATERIAL_SHORTAGE

M203 short by 800 pcs
```

---

# 32. Dashboard 页面结构

严格按照：

```text
Exceptions
↓
Orders at Risk
↓
Today's Production
↓
Material Shortages
↓
QC Holds
↓
Ready to Ship
↓
KPIs
```

不要设计成传统 ERP 首页。

---

# 33. Module 08 — factory_os_connector

这个模块最后开发。

不是 MVP 核心流程的前置条件。

## 定位

负责：

```text
Factory Workspace
↕
Central Trade Platform
```

---

# 34. Connector 数据边界

允许同步：

```text
Shared Buyer PO
Product
Quantity
Agreed Price
Requested Delivery
Confirmed Delivery
Production Status
Production Progress
QC Status
Ready Date
Shipment Status
```

禁止同步：

```text
Other Customers
Other Orders
Other Prices
Supplier Cost
Other Inventory
Payroll
Accounting
Internal Margin
```

---

# 35. Connector 技术模型

建议新增：

```text
factory.sync.binding
factory.sync.event
factory.sync.log
```

必要时：

```text
factory.shared.order
```

但 `factory.shared.order` 只代表跨系统协同对象，不替代：

```text
sale.order
purchase.order
```

---

# 36. Outbox Pattern

不要业务动作发生时直接：

```text
HTTP POST → central server
```

然后失败就阻塞业务。

应该：

```text
Odoo Transaction
      ↓
Create Sync Event
      ↓
Commit
      ↓
Background Worker
      ↓
Central API
```

事件：

```text
ORDER_CONFIRMED
PRODUCTION_STARTED
PRODUCTION_PROGRESS
PRODUCTION_COMPLETED
QC_FAILED
QC_PASSED
READY_TO_SHIP
SHIPPED
```

---

# 37. Connector 必须支持 Idempotency

每个 Event：

```text
event_uuid
source_workspace
object_type
object_id
event_type
version
created_at
```

中央系统重复收到相同：

```text
event_uuid
```

不得重复执行。

---

# 38. 开发顺序

不要八个模块同时开发。

按照下面的 Gate 顺序进行。

| Phase | 目标 | 模块 |
|---|---|---|
| 0 | 现有 Odoo 审计 | 无开发 |
| 1 | 建立系统骨架 | Core |
| 2 | 跑通订单 | Orders |
| 3 | 跑通物料与库存 | Supply |
| 4 | 跑通制造 | Production |
| 5 | 加入质量闭环 | Quality |
| 6 | 完成交付与追溯 | Delivery |
| 7 | 建立管理工作台 | Dashboard |
| 8 | 接入中央外贸平台 | Connector |

---

# 39. Phase 0 — Technical Audit

这是第一项任务。

IDE 必须先输出：

```text
Odoo exact version
Community / Enterprise
Installed addons
Custom addons
Current database schema
Current external trade modules
Current product models
Current supplier/customer models
Current Sale workflow
Current Purchase workflow
Current Stock workflow
Current MRP usage
Current security structure
```

尤其检查有没有已经自定义：

```text
product
sale
purchase
stock
mrp
```

禁止未审计就创建新模型。

Phase 0 还必须确认并冻结：

```text
docs/factory_os/configuration-matrix.md
docs/factory_os/configuration-schema.md
docs/factory_os/configuration-dependency-graph.md
docs/factory_os/system-invariants.md
docs/factory_os/progressive-adoption.md
```

并输出每项不变量对应的模型约束、服务校验、ACL/record rule 与测试用例映射。未完成该映射，不进入 Phase 1。

Phase 0 还必须验证：Odoo 19 Community 原生 MO/BOM/组件消耗的真实行为；单仓库/少量内部库位时是否可自动推断简单库存展示；所有 PRD 主数据字段是否遵循 Just-in-Time Validation。库存展示优先自动推断，只有证明确有必要时才提议纯展示性质的 simple/advanced 设置。

---

# 40. Phase 0 输出 Model Mapping

必须生成：

```text
docs/factory_os/model-mapping.md
```

格式：

| PRD Object | Existing Odoo Model | Action |
|---|---|---|
| Customer | res.partner | Reuse |
| Supplier | res.partner | Reuse |
| Product | product.template | Extend |
| Sales Order | sale.order | Extend |
| Purchase Order | purchase.order | Extend |
| Inventory | stock.* | Reuse |
| BOM | mrp.bom | Extend |
| Production | mrp.production | Extend |
| Operation | mrp.workorder | Extend |
| Lot | stock.lot | Reuse |
| Shipment | stock.picking | Extend |
| QC | TBD after edition audit | Extend / Thin custom |
| NCR | Custom | Create |

没有这个文档，不进入 Phase 1。

---

# 41. Phase 1 — Core 验收 Gate

必须完成：

| 验收项 | 要求 |
|---|---|
| 模块安装 | PASS |
| 模块卸载 | PASS |
| Factory OS 菜单 | PASS |
| 角色权限 | PASS |
| 普通用户越权测试 | PASS |
| 产品扩展 | PASS |
| Customer/Supplier 分类 | PASS |
| 配置页 | PASS |
| 初始化向导六步流程 | PASS |
| 配置依赖与隐藏逻辑 | PASS |
| 配置变更审计 | PASS |
| 系统不变量绕过测试 | PASS |
| Safe Minimal 裸配置 | PASS |
| 无 BOM/库存/QC 的订单看板流程 | PASS |
| Committed Date 状态转换 Gate | PASS |
| 一人多角色向导映射 | PASS |
| 主数据 Just-in-Time Validation | PASS |

特别测试：

```text
Operator
```

不得通过 URL 或 RPC 读取：

```text
Purchase Price
Customer List
Supplier Data
Admin Settings
```

---

# 42. Phase 2 — Order Gate

验证真实流程：

```text
Customer
↓
Quotation
↓
Sales Order
↓
Execution Status
```

必须通过：

```text
Customer PO
Requested Date
Confirmed Date
Order Health
Attachments
Search
Role access
```

---

# 43. Phase 3 — Supply Gate

选择一个真实产品 BOM。

验证：

```text
SO = 1000 pcs
↓
BOM Explosion
↓
Material Demand
↓
Available Inventory
↓
Shortage
↓
Purchase Order
↓
Receipt
↓
Available Material
```

这是整个系统第一个真正 End-to-End 场景。

---

# 44. Phase 4 — Production Gate

继续同一个订单：

```text
Material Ready
↓
Create MO
↓
Work Orders
↓
Operator Update
↓
Finished Qty
↓
Finished Lot
```

必须保证：

```text
库存变化正确
组件消耗正确
成品库存正确
Lot正确
```

不能为了 UI 简单破坏 Odoo stock/mrp transaction。

---

# 45. Phase 5 — Quality Gate

验证：

```text
Incoming QC
In-process QC
Final QC
```

故意制造一次：

```text
FAIL
```

必须产生：

```text
QC Hold
↓
NCR
↓
Corrective Action
↓
Verification
↓
Closed
```

同时订单：

```text
Health = RED
```

---

# 46. Phase 6 — Delivery Gate

完整测试：

```text
SO
↓
MO
↓
Lot
↓
QC Pass
↓
Ready to Ship
↓
Delivery Picking
↓
Shipped
↓
Delivered
```

然后：

```text
Search Batch
```

必须完整追出：

```text
SO
MO
Raw Material Lot
QC
Shipment
```

---

# 47. Phase 7 — Dashboard Gate

Dashboard 所有数字必须能从底层记录人工复算。

例如：

```text
Late Orders = 3
```

必须可以点击进入：

```text
exactly those 3 orders
```

禁止：

```text
Dashboard number = 3
List result = 4
```

---

# 48. Phase 8 — Connector Gate

先只连接：

```text
1 Factory Workspace
+
Central Trade DB
```

验证：

```text
Central PO
↓
Factory receives shared order
↓
Factory production update
↓
Central receives progress
↓
QC update
↓
Shipment update
```

再验证隐私：

Central API 无法查询：

```text
Factory unrelated customer
Unrelated SO
Unrelated inventory
Internal cost
```

---

# 49. 测试体系

每一个 Factory OS addon 必须有自动测试。

目录标准：

```text
factory_os_xxx/
├── __manifest__.py
├── models/
├── views/
├── security/
├── data/
├── static/
└── tests/
```

Odoo 官方模块机制本身就是通过 models、views、security、data 等组成 addon，并通过 access rights 和 record rules实施权限控制。citeturn893773search2turn893773search9

---

# 50. 必须覆盖的测试类型

| Test | 必须 |
|---|---|
| Module install | ✓ |
| Model constraints | ✓ |
| Permissions | ✓ |
| Record rules | ✓ |
| State transitions | ✓ |
| Inventory integrity | ✓ |
| MRP integrity | ✓ |
| QC workflow | ✓ |
| Lot traceability | ✓ |
| Risk engine | ✓ |
| Connector idempotency | ✓ |
| Cross-workspace privacy | ✓ |

---

# 51. 禁止的技术实现

以下直接写入治理规则：

```text
禁止修改 Odoo core source

禁止复制 sale.order 重新实现销售订单

禁止复制 stock.quant 建第二套库存

禁止复制 mrp.production 建第二套生产订单

禁止修改 Odoo native state 语义

禁止以 UI 隐藏代替 security rule

禁止大量使用 sudo() 绕过权限

禁止 Dashboard 保存第二份业务事实

禁止中央平台默认读取工厂私有数据

禁止为单个朋友工厂 fork 一套代码

禁止未有真实需求就开发 PLC / IoT / APS / OEE
```

---

# 52. Git 建议目录

建议当前贸易项目如果仍然采用同一个 Git：

```text
repo/
│
├── addons/
│   ├── trade_xxx/
│   ├── factory_os_core/
│   ├── factory_os_orders/
│   ├── factory_os_supply/
│   ├── factory_os_production/
│   ├── factory_os_quality/
│   ├── factory_os_delivery/
│   ├── factory_os_dashboard/
│   └── factory_os_connector/
│
├── docs/
│   └── factory_os/
│       ├── PRD.md
│       ├── architecture.md
│       ├── model-mapping.md
│       ├── permissions.md
│       ├── state-machines.md
│       ├── api-contract.md
│       └── test-plan.md
│
└── tests/
```

---

# 53. 第一版真正的 E2E Definition of Done

工厂OS v0.1 不是：

> 8 个模块安装成功。

真正 Definition of Done 是一个真实订单能够完整经过：

```text
Customer Order
      ↓
Material Check
      ↓
Shortage Detection
      ↓
Purchase
      ↓
Receipt
      ↓
Production
      ↓
Work Order
      ↓
Finished Lot
      ↓
QC
      ↓
NCR if needed
      ↓
Ready to Ship
      ↓
Shipment
      ↓
Delivered
      ↓
Traceability
```

并且老板打开首页可以直接看到：

```text
哪些订单正常
哪些订单有风险
缺什么料
哪些生产延期
哪些 QC Hold
哪些货可以发
```

做到这里，Factory OS v0.1 才算完成。

---

# 54. 开发优先级最终排序

| Priority | Module | 原因 |
|---|---|---|
| P0 | `factory_os_core` | 系统骨架、安全边界 |
| P0 | `factory_os_orders` | 一切业务起点 |
| P0 | `factory_os_supply` | 库存和缺料决定能否生产 |
| P0 | `factory_os_production` | Factory OS核心价值 |
| P0 | `factory_os_quality` | 外贸供应链核心能力 |
| P0 | `factory_os_delivery` | 完成业务闭环 |
| P1 | `factory_os_dashboard` | 管理层真正日常使用界面 |
| P1 | `factory_os_connector` | 建立供应网络后才需要 |

这里 Dashboard 虽然开发顺序较晚，但**产品重要性是 P0**。

原因只是：

> 没有稳定的底层业务数据，先开发 Dashboard 只能制造假数据和返工。

---

# 55. 最终架构原则

工厂OS最终必须坚持四层：

```text
Odoo Transaction Layer
Sale / Purchase / Stock / MRP

        ↓

Factory OS Execution Layer
Status / Risk / QC / Traceability

        ↓

Factory OS Experience Layer
Dashboard / Mobile / Exceptions

        ↓

Supply Network Layer
Connector / Shared Orders
```

四层不能倒置。

尤其禁止：

```text
先做漂亮 Dashboard
↓
再想底层数据从哪里来
```

正确顺序永远是：

```text
Transaction truth
↓
Execution logic
↓
Management visibility
↓
Network integration
```
