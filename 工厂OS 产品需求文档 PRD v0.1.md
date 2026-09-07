# 工厂OS 产品需求文档 PRD

**项目名称：** 工厂OS  
**英文名称：** Factory OS  
**文档版本：** v0.1  
**阶段：** MVP / 业务验证阶段  
**产品类型：** 中小制造工厂轻量经营与生产执行系统  
**底层平台：** Odoo 独立 Workspace / 独立数据库  
**核心定位：** 订单驱动的轻量工厂执行系统  
**目标用户：** 中小型制造工厂老板、业务人员、采购、仓库、生产管理、质检人员

---

# 1. 产品背景

大量中小型制造工厂当前依赖以下工具完成经营与生产管理：

- Excel
- 微信
- 电话
- 纸质生产单
- 独立库存表
- 人工经验
- 财务软件
- 零散 ERP

这些工具通常能够完成单个动作，但缺乏订单到交付全过程的统一状态。

典型问题包括：

- 老板无法快速判断订单做到哪里；
- 销售承诺交期后无法判断生产是否能按时完成；
- 原料缺货通常在生产启动后才被发现；
- 采购、仓库、生产之间信息不同步；
- 产品生产数量依赖人工汇报；
- 质量问题通过微信处理，无法形成闭环；
- 批次、原料、质检和客户订单无法完整追溯；
- 订单延期后无法快速定位真实原因；
- 工厂内部已经有部分软件，但员工仍大量依赖 Excel 和微信。

工厂OS不试图替代大型 ERP、MES、WMS 或财务系统。

工厂OS解决一个更基础的问题：

> **让工厂随时知道：有什么订单、缺什么料、做到哪里、有什么质量问题、什么时候能交付。**

---

# 2. 产品定位

## 2.1 一句话定义

**工厂OS是一套围绕“订单—物料—生产—质量—交付”构建的轻量制造执行系统。**

---

## 2.2 产品核心目标

系统必须持续回答五个问题：

1. 现在有哪些订单？
2. 这些订单需要什么物料，库存是否足够？
3. 每个订单目前生产到什么阶段？
4. 当前是否存在质量问题或异常？
5. 每个订单什么时候能够交付？

任何新增功能，如果不能明显改善上述五个问题之一，默认不进入 MVP。

---

# 3. 产品原则

## 3.1 订单驱动

系统的核心对象不是设备，不是员工，也不是财务凭证。

核心对象是：

**Customer Order。**

订单向下驱动：

```text
Customer Order
      ↓
Material Requirement
      ↓
Purchase / Inventory
      ↓
Production Order
      ↓
Quality
      ↓
Delivery
```

---

## 3.2 状态优先于复杂流程

第一阶段重点回答：

- 当前状态是什么；
- 是否正常；
- 哪里异常；
- 下一步是什么。

不追求构建复杂审批流。

---

## 3.3 手机优先

生产、仓库和质检人员的核心动作必须能够在手机端完成。

原则：

> 高频操作尽量不超过 3 次点击。

---

## 3.4 少输入，多自动生成

系统应优先通过已有数据自动计算，而不是要求员工重复填写。

例如：

订单数量：

```text
5,000 pcs
```

已经生产：

```text
3,200 pcs
```

系统自动计算：

```text
Production Progress = 64%
Remaining = 1,800 pcs
```

---

## 3.5 异常优先

Dashboard 不应该只是统计数字。

系统应主动突出：

- 延迟订单
- 缺料
- QC Hold
- 不良率异常
- 采购延期
- 即将到期订单
- 数量不足

---

## 3.6 可追溯

任何一批产品，应尽可能追溯：

```text
客户订单
→ 生产订单
→ Batch
→ 原料 Lot
→ 生产记录
→ QC
→ Shipment
```

---

## 3.7 数据隔离

每家工厂拥有独立 Workspace 和独立数据库。

工厂自身数据归工厂所有。

默认不向任何第三方同步：

- 其他客户
- 其他客户价格
- BOM 成本
- 财务信息
- 其他订单
- 内部利润
- 员工信息

与外部贸易平台之间只同步明确授权的共享订单数据。

---

# 4. 非目标

以下内容明确不属于工厂OS MVP。

---

## 4.1 不做完整财务 ERP

不开发：

- General Ledger
- Chart of Accounts
- 银行对账
- 税务
- VAT
- 固定资产
- 折旧
- 财务报表
- 工资核算

财务需求未来通过：

- 金蝶
- 用友
- 管家婆
- 第三方财务软件

完成。

工厂OS最多保留经营分析所需的简单金额数据。

---

## 4.2 不做人力资源系统

不开发：

- 招聘
- 考勤
- 工资
- 假期
- 社保
- 绩效
- 员工档案管理

员工信息只服务于任务责任。

---

## 4.3 不做传统重型 MES

MVP 不开发：

- PLC
- OPC-UA
- SCADA
- Machine Integration
- 实时设备监控
- 自动 Cycle Time
- OEE 数据采集
- Andon
- 数字孪生
- 工业 IoT

---

## 4.4 不做高级 APS

不开发：

- 复杂产能优化
- 自动有限产能排程
- Machine-level scheduling
- 数学优化排产
- 自动换线优化

第一阶段只支持人工计划和简单排序。

---

## 4.5 不做完整 PLM

不开发：

- CAD 管理
- 复杂 ECN
- 设计审批
- 图纸生命周期
- Engineering Change Board

---

## 4.6 不做完整 WMS

不开发：

- Wave Picking
- 自动库位优化
- RFID
- AGV
- 自动仓储
- Pick Path Optimization

---

# 5. 用户角色

## 5.1 Factory Owner / Admin

权限最高。

主要需求：

- 查看经营全貌；
- 查看所有订单；
- 查看生产进度；
- 查看延期风险；
- 查看质量异常；
- 查看库存；
- 查看简单经营数据。

---

## 5.2 Sales / Order Manager

主要负责：

- Customer
- Quotation
- Sales Order
- 交期
- 客户 PO
- Shipment 状态

---

## 5.3 Purchasing

主要负责：

- Supplier
- Purchase Request
- Purchase Order
- 原料 ETA
- 收货状态

---

## 5.4 Warehouse

主要负责：

- 收货
- 入库
- 出库
- 调拨
- 盘点
- Lot
- Finished Goods

---

## 5.5 Production Manager

主要负责：

- Production Order
- 生产计划
- 工序
- 生产数量
- 生产异常
- 完工

---

## 5.6 Production Operator

只允许执行简单动作：

- 查看今日任务
- 开始生产
- 更新完成数量
- 更新不良数量
- 完成工序

---

## 5.7 Quality Inspector

主要负责：

- Incoming QC
- In-process QC
- Final QC
- NCR
- 图片
- 整改验证

---

# 6. 信息架构

主导航：

```text
Dashboard

Orders
├ Customers
├ Quotations
└ Sales Orders

Products
├ Products
├ BOM
└ Product Versions

Purchasing
├ Suppliers
├ Purchase Requests
└ Purchase Orders

Inventory
├ Stock
├ Receipts
├ Issues
├ Transfers
├ Lots
└ Stock Count

Production
├ Production Orders
├ Operations
└ Today's Production

Quality
├ Inspections
├ NCR
└ Quality History

Delivery
├ Ready to Ship
├ Shipments
└ Delivery History

Reports

Settings
```

---

# 7. Dashboard

Dashboard 是产品第一优先级页面。

目标：

> 用户进入系统 30 秒内判断工厂当前是否健康。

---

## 7.1 顶部 KPI

显示：

- Open Orders
- Orders Due This Week
- Late Orders
- Orders At Risk
- Production In Progress
- Material Shortages
- QC Holds
- Ready to Ship

---

## 7.2 Order Health

订单分为：

### Green

正常。

### Yellow

存在风险，例如：

- 原料预计晚到；
- 生产进度略落后；
- 距交期较近。

### Red

已经异常：

- 明确延期；
- 缺料；
- QC Hold；
- 生产停止。

---

## 7.3 Today

显示：

### Production

今天：

- 应开工
- 应完成
- 生产中
- 延误

### Purchasing

今天：

- 应到原料
- 逾期 PO

### Quality

- 待检验
- QC Hold
- Open NCR

### Delivery

- 今日计划发货
- 本周待发货

---

## 7.4 Exception Feed

系统集中显示异常：

```text
SO-1025
Material shortage
M-233 short 800 pcs

SO-1031
QC Hold
Final inspection failed

PO-553
Supplier late
Expected Sep 8
Current ETA Sep 11
```

---

# 8. Customer

基础字段：

- Customer Code
- Customer Name
- Contact
- Phone
- Email
- Address
- Country
- Currency
- Payment Terms
- Notes
- Active

MVP 不开发 CRM Pipeline。

---

# 9. Product

字段：

- SKU
- Product Name
- English Name
- Category
- Product Image
- Unit
- Barcode
- Specification
- Product Revision
- Default Lead Time
- Packaging
- Default Supplier
- Active

---

# 10. BOM

BOM 支持：

```text
Finished Product
├ Raw Material
├ Component
├ Packaging
└ Sub-assembly
```

字段：

- Product
- Revision
- Component
- Qty
- Unit
- Scrap %
- Effective Date
- Active

---

# 11. Sales Order

## 11.1 状态

```text
Draft
↓
Confirmed
↓
Material Check
↓
Production
↓
QC
↓
Ready to Ship
↓
Shipped
↓
Completed
```

异常状态：

```text
On Hold
Cancelled
Late
```

---

## 11.2 字段

Header：

- SO Number
- Customer
- Customer PO
- Order Date
- Requested Delivery Date
- Confirmed Delivery Date
- Currency
- Status
- Owner
- Attachment
- Notes

Line：

- Product
- SKU
- Qty
- Unit
- Unit Price
- Amount
- Delivered Qty

---

# 12. Material Requirement

订单确认后系统根据 BOM 自动计算 Material Requirement。

计算：

```text
Demand
− Available Inventory
− Existing Reserved
= Shortage
```

显示：

| Material | Demand | Available | Reserved | Shortage |
|---|---:|---:|---:|---:|

用户可选择：

```text
Create Purchase Request
```

---

# 13. Purchasing

## 13.1 Supplier

字段：

- Supplier Code
- Name
- Contact
- Phone
- Email
- Address
- Material Categories
- Default Lead Time
- Notes
- Active

---

## 13.2 Purchase Request

来源：

- Material shortage
- Manual request
- Low stock

状态：

```text
Draft
Approved
Converted to PO
Cancelled
```

---

## 13.3 Purchase Order

字段：

- PO Number
- Supplier
- Material
- Qty
- Price
- Order Date
- Expected Date
- Current ETA
- Received Qty
- Status
- Related Sales Order
- Attachment

状态：

```text
Draft
Confirmed
Partially Received
Received
Late
Cancelled
```

---

# 14. Inventory

库存类型：

- Raw Material
- Component
- Packaging
- WIP
- Finished Goods

---

## 14.1 基础库存字段

- Item
- Warehouse
- Location
- Lot
- On Hand
- Reserved
- Available

计算：

```text
Available = On Hand − Reserved
```

---

## 14.2 库存动作

支持：

- Receipt
- Issue
- Transfer
- Adjustment
- Count

所有动作必须生成记录。

---

## 14.3 Low Stock

支持：

- Minimum Stock
- Reorder Level

当：

```text
Available < Reorder Level
```

触发提醒。

---

# 15. Lot / Batch

所有需要追溯的：

- 原材料
- WIP
- Finished Goods

支持 Lot Number。

字段：

- Lot Number
- Item
- Supplier
- Received Date
- Quantity
- Remaining Qty
- QC Status
- Related Production
- Notes

---

# 16. Production Order

Production Order 简称 MO。

来源：

- Sales Order
- Manual production

---

## 16.1 字段

- MO Number
- Product
- Revision
- Qty
- Related Sales Order
- Planned Start
- Planned Finish
- Actual Start
- Actual Finish
- Completed Qty
- Reject Qty
- Status
- Production Team
- Notes

---

## 16.2 状态

```text
Draft
↓
Material Ready
↓
Ready
↓
In Production
↓
QC
↓
Completed
```

异常：

```text
Material Hold
Production Hold
QC Hold
Cancelled
```

---

# 17. Production Operations

MVP 支持简单 Routing。

例如：

```text
Assembly
↓
Testing
↓
Packing
```

Operation 字段：

- Operation
- Sequence
- Planned Qty
- Completed Qty
- Reject Qty
- Start
- Finish
- Operator / Team
- Status

---

## 17.1 Operator UI

生产人员手机页面必须极简。

示例：

```text
MO-1027

Product
Portable Blower

Today's Target
1,000

Completed
[ 760 ]

Reject
[ 12 ]

[Update]
```

不允许出现大量 ERP 字段。

---

# 18. Quality

质量分三种：

## Incoming QC

原料进入库存前。

## In-process QC

生产过程中。

## Final QC

产品完成后。

---

## 18.1 Inspection

字段：

- Inspection No.
- Type
- Product / Material
- Lot
- Production Order
- Sample Size
- Pass Qty
- Fail Qty
- Result
- Inspector
- Date
- Photos
- Notes

Result：

```text
PASS
FAIL
HOLD
```

---

# 19. NCR

NCR：

**Non-Conformance Report**

流程：

```text
Open
↓
Containment
↓
Root Cause
↓
Corrective Action
↓
Verification
↓
Closed
```

字段：

- NCR Number
- Source
- Product
- Lot
- MO
- Problem
- Severity
- Photos
- Owner
- Root Cause
- Corrective Action
- Due Date
- Verification
- Status

---

# 20. Delivery

状态：

```text
Preparing
↓
Ready to Ship
↓
Shipped
↓
Delivered
```

字段：

- Shipment Number
- Customer
- Sales Order
- Product
- Quantity
- Cartons
- Gross Weight
- Net Weight
- CBM
- Ship Date
- Carrier
- Tracking
- Attachment
- POD
- Status

---

# 21. Traceability

核心查询：

用户输入：

```text
Batch B26090703
```

系统应显示：

```text
Batch B26090703
        │
        ├ Product
        ├ Production Order
        ├ Customer Order
        ├ Raw Material Lots
        ├ Production Operations
        ├ QC
        ├ NCR
        └ Shipment
```

反向也必须支持。

从 Customer Order 可以一路追溯到 Batch 和 Raw Material。

---

# 22. Reports

MVP 报表保持少而实用。

---

## 22.1 Order Delivery

指标：

- Total Orders
- On-time
- Late
- On-time %

---

## 22.2 Production

指标：

- Planned Qty
- Completed Qty
- Reject Qty
- Completion Rate

---

## 22.3 Quality

指标：

- Inspection Count
- Pass Rate
- Reject Rate
- NCR Count

---

## 22.4 Inventory

显示：

- Inventory Value
- Low Stock
- Slow-moving Items

库存价值允许简单估算，不作为正式财务数据。

---

## 22.5 Supplier

指标：

- PO Count
- On-time Delivery
- Average Lead Time
- QC Fail Rate

---

# 23. 简单经营信息

工厂OS允许记录：

- Sales Amount
- Purchase Amount
- Estimated Material Cost
- Outsourcing Cost
- Estimated Gross Margin

但必须明确：

> 所有成本和毛利数据均为经营估算，不替代正式会计系统。

---

# 24. Permissions

采用 Role-Based Access Control。

---

## Owner / Admin

访问全部功能。

---

## Sales

可以访问：

- Customer
- Sales Order
- Delivery

不能修改：

- QC
- Production
- Purchasing

---

## Purchasing

访问：

- Supplier
- Purchase Request
- Purchase Order

---

## Warehouse

访问：

- Inventory
- Receipt
- Issue
- Transfer
- Lot

---

## Production

访问：

- Production Orders
- Operations

---

## Quality

访问：

- Inspection
- NCR
- Quality History

---

## Operator

仅访问：

```text
Today's Tasks
Update Quantity
Report Issue
```

---

# 25. 外部供应链协同

工厂OS必须预留与外部贸易平台连接能力。

原则：

> 外部平台只能看到双方明确共享的订单对象。

---

## 25.1 Shared Supply Order

例如：

```text
Buyer:
External Trading Company

Supplier:
Factory A
```

共享字段：

- Buyer PO
- Product
- Qty
- Price
- Requested Delivery Date
- Confirmed Delivery Date
- Production Status
- Production Progress
- QC Status
- Ready Date
- Shipment Status

---

## 25.2 Private Data

以下数据不得自动同步：

- 工厂其他客户
- 其他客户订单
- 其他客户价格
- Supplier Prices
- BOM Costs
- Payroll
- Internal Margin
- Financial Records
- Other Inventory Transactions

---

# 26. 外部同步原则

未来 API 建议采用事件方式。

例如：

```text
purchase_order.created
purchase_order.confirmed
production.started
production.progress_updated
production.completed
quality.failed
quality.passed
shipment.ready
shipment.shipped
```

每次同步必须记录：

- Event
- Timestamp
- Source
- Destination
- Result

---

# 27. Mobile UX

以下角色优先使用手机：

- Production Operator
- Warehouse
- Quality

移动端页面必须遵循：

### 原则 1

一个页面解决一个动作。

### 原则 2

尽量使用：

- 数字
- 大按钮
- 图片
- 扫码

而不是复杂表格。

### 原则 3

生产人员不需要理解 ERP 概念。

---

# 28. Attachments

以下对象支持附件：

- Product
- Sales Order
- Purchase Order
- Production Order
- Inspection
- NCR
- Shipment

支持：

- PDF
- Excel
- Image

移动端应优先支持现场拍照上传。

---

# 29. Notification

MVP 只做高价值通知。

通知条件：

- Sales Order approaching due date
- Sales Order late
- Material shortage
- Purchase Order late
- Production late
- QC failure
- NCR overdue
- Shipment due

不做大量低价值提醒。

---

# 30. Search

全局搜索至少支持：

- SO
- Customer PO
- Product SKU
- MO
- PO
- Lot
- NCR
- Shipment

---

# 31. Audit Log

关键动作必须记录：

- Who
- What
- When
- Before
- After

重点对象：

- Order
- Inventory
- Production
- Quality
- Shipment

---

# 32. MVP 成功标准

MVP 不以“功能数量”判断成功。

判断标准为：

## 32.1 使用率

至少一家真实工厂连续使用。

---

## 32.2 订单覆盖率

至少：

> 80% 活跃生产订单进入系统。

---

## 32.3 Excel 替代

系统应至少替代：

- 订单进度 Excel
- 库存 Excel
- 生产进度 Excel

其中两项。

---

## 32.4 查询效率

老板应能够在：

**30 秒以内**

回答：

> 这个订单现在做到哪里了？

---

## 32.5 异常可视化

用户不依赖微信询问即可发现：

- 缺料
- 延期
- QC Hold

---

# 33. MVP 开发范围

## P0

必须完成：

- Login / Roles
- Dashboard
- Customer
- Supplier
- Product
- BOM
- Sales Order
- Purchase Order
- Inventory
- Material Requirement
- Production Order
- Production Progress
- Lot / Batch
- Inspection
- NCR
- Delivery
- Traceability
- Attachments
- Basic Reports
- Mobile-friendly UI

---

## P1

MVP 稳定后：

- Barcode / QR
- Purchase Request
- Supplier Score
- Order Margin
- Better Notifications
- External Supply API
- Mobile Quick Actions

---

## P2

真实业务证明有需求后：

- Capacity Planning
- Simple Scheduling
- Product Revision Improvement
- More Advanced QC
- Customer Portal
- Supplier Portal
- External ERP Integration

---

# 34. 明确禁止进入 MVP 的内容

以下属于 Scope Guardrail：

```text
Accounting
Payroll
HR
Recruiting
Attendance
Tax
CRM Marketing
Email Campaign
PLC
SCADA
IoT
OEE
Machine Monitoring
Advanced APS
Digital Twin
RFID
AGV
Advanced WMS
Complex PLM
Full QMS
```

未经产品负责人明确批准不得进入开发。

---

# 35. 核心数据对象

第一阶段建议主要模型：

```text
factory.customer
factory.supplier

factory.product
factory.bom

factory.sales_order
factory.sales_order_line

factory.purchase_order
factory.purchase_order_line

factory.inventory
factory.stock_move
factory.lot

factory.production_order
factory.production_operation

factory.inspection
factory.ncr

factory.shipment

factory.shared_supply_order

factory.audit_log
```

如优先复用 Odoo 原生模型，应避免重复创建已有成熟对象。

原则：

> **优先扩展 Odoo 原生对象，而不是重新造一套 ERP 数据模型。**

---

# 36. Odoo 实现原则

工厂OS是 Odoo 上层产品，而不是重新实现 Odoo。

优先复用：

```text
res.partner
product.template
product.product
sale.order
purchase.order
stock.move
stock.picking
stock.lot
mrp.production
mrp.bom
quality.*
```

自定义模块主要负责：

- 简化 UI；
- 固化流程；
- 状态聚合；
- Dashboard；
- 异常检测；
- 移动端操作；
- 外部供应链接口；
- 数据隔离；
- 工厂OS特有业务逻辑。

---

# 37. 推荐模块结构

```text
factory_os_core

factory_os_dashboard

factory_os_orders

factory_os_inventory

factory_os_purchase

factory_os_production

factory_os_quality

factory_os_delivery

factory_os_traceability

factory_os_reports

factory_os_connector
```

不要创建过多细碎模块。

---

# 38. UX 产品原则

工厂OS不能看起来像传统 Odoo Backend 的简单换皮。

首页应该是：

```text
What needs attention today?
```

而不是：

```text
Select application
```

---

# 39. 首页优先顺序

页面从上至下：

```text
Exceptions

Orders at Risk

Today's Production

Material Shortages

QC Holds

Ready to Ship

KPIs
```

异常优先于统计。

---

# 40. 产品治理规则

未来任何功能进入工厂OS前必须回答三个问题。

---

## Rule 1

**是否直接改善订单、库存、生产、质量或交付？**

如果不是：

默认不做。

---

## Rule 2

**普通工厂员工是否需要学习 ERP 才能使用？**

如果是：

重新设计。

---

## Rule 3

**这个数据是否必须离开工厂自己的数据库？**

如果不是：

默认保持本地。

---

# 41. 第一阶段验证对象

建议仅选择：

**1–2 家关系较好、愿意真实使用的朋友工厂。**

不建议第一阶段同时服务大量工厂。

验证重点不是：

> 系统有没有 Bug。

而是：

> 他们是否真的愿意每天打开工厂OS。

---

# 42. MVP 试点流程

推荐：

## Week 1

录入：

- Customers
- Products
- BOM
- Inventory

---

## Week 2

开始使用：

- Sales Order
- Purchasing

---

## Week 3

加入：

- Production Order
- Production Progress

---

## Week 4

加入：

- QC
- Shipment

然后观察：

- 哪些字段没人填；
- 哪些页面没人打开；
- 哪些动作仍然回到微信；
- 哪些 Excel 仍然必须存在。

这些数据比继续开发更多功能更重要。

---

# 43. 产品长期方向

如果 MVP 被真实工厂持续采用，工厂OS可以逐步发展为：

```text
Factory OS
     │
     ├ Daily Operation
     │
     ├ Management Intelligence
     │
     └ Supply Network
```

---

## Layer 1 — Daily Operation

```text
Orders
Purchase
Inventory
Production
Quality
Delivery
```

---

## Layer 2 — Management Intelligence

```text
Lead Time
On-time Delivery
Defect Rate
Inventory
Supplier Performance
Order Margin
```

---

## Layer 3 — Supply Network

```text
RFQ
Supplier Matching
Shared PO
Production Visibility
Quality Visibility
Shipment
Supplier Score
```

---

# 44. 长期战略边界

工厂OS长期可以成为：

> **连接中小制造工厂和全球买家的供应链执行基础设施。**

但第一阶段不以此作为开发理由。

第一阶段唯一目标仍然是：

> **让一家真实工厂明显比以前更容易管理订单、库存、生产、质量和交付。**

如果这一点没有得到证明，不继续扩展平台能力。

---

# 45. 最终产品定义

工厂OS不是：

- 又一个 ERP；
- 又一个 MES；
- 大型数字化转型平台；
- 工业互联网平台。

工厂OS是：

> **一套为中小制造工厂设计的、订单驱动、异常优先、手机友好、可追溯的轻量生产经营执行系统。**

最终判断标准不是功能多不多。

而是工厂老板打开首页后，能不能马上回答：

> **哪些订单有问题，我今天应该先管什么。**