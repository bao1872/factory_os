# Factory OS — Security Baseline（Odoo 19 Community 原生 ACL 快照）

Date: 2026-09-07（Phase 0 r2）
方法：全新 DB `factory_phase0_r2`（72 模块，sale_management/stock/purchase/mrp 及其桥接），以 `odoo shell` 读取 `ir.model.access`（ACL）与 `ir.rule`（record rules），关联 res.groups 全名；1 用户（admin），无自定义用户/角色。本快照回答"装完即用"的原生默认权限，供不变量 #8（安全底线）与 Phase 1 角色设计做基线差。

## 1. 关键组（实测存在）

| 技术名 | 显示名 | 域 |
|---|---|---|
| base.group_user | Role / User | 全员内部用户 |
| base.group_system | Role / Administrator | 超管 |
| base.group_portal / group_public | Role / Portal · Role / Public | 门户/公开 |
| sales_team.group_sale_salesman | Sales / User: Own Documents Only | 销售（含变体 …All Documents=All Leads 组） |
| purchase.group_purchase_user / _manager | Purchase / User · Administrator | 采购 |
| stock.group_stock_user / _manager | Inventory / User · Administrator | 库存 |
| mrp.group_mrp_user / _manager | Manufacturing / User · Administrator | 生产 |
| base.group_partner_manager | Contact / Creation | 联系人 |
| product 管理组 | Products / Create（product.template.manager） | 产品 |

## 2. 核心模型 ACL 摘要（读/写/建/删，按组）

- `sale.order`：Sales/User Own(1,1,1,0) · Sales/Admin(1,1,1,1) · Manufacturing/User(1,1,0,0) · Accounting/Invoicing(1,1,0,0) · Inventory/User(1,1,0,0) · Portal(1,0,0,0)。line 同构（user 可 create/unlink）。
- `purchase.order`：Purchase/User(1,1,1,1) · Purchase/Admin(1,1,1,1) · Inventory/User(1,0,0,0) · Accounting Invoicing(1,1,0,0) · Portal(1,0,0,0)。line 同构。
- `stock.move`：Inventory/User(1,1,1,0) · Inventory/Admin(1,1,1,1) · 另有 Sales/User(1,1,1,0)、Sales/Admin(1,1,1,1)、MRP/User(1,1,1,1)、Purchase/User(1,0,0,0)…（多域可读写）。
- `stock.move.line`：Inventory/User(1,1,1,1) · Inventory/Admin(1,1,1,1) · Role/User(1,1,1,1)。
- `stock.quant`：Inventory/User(1,1,1,0)；Role/User(1,0,0,0)。
- `stock.picking`：Inventory/User(1,1,1,1) · Inventory/Admin(1,1,1,1) · Sales/User(1,1,1,0) · Sales/Admin(1,1,1,1) · Purchase/User(1,1,1,1) · Portal(1,0,0,0)…
- `stock.lot`：Inventory/User(1,1,1,1)。
- `stock.warehouse.orderpoint`：Inventory/User(1,0,0,0) · Inventory/Admin(1,1,1,1) · Sales/User(1,0,0,0) · Purchase/User(1,0,0,0)。
- `mrp.production`：Manufacturing/User(1,1,1,1) · Manufacturing/Admin(1,0,0,0) · Sales/User(1,1,1,0) · Inventory/User(1,0,0,0)。
- `mrp.bom`：Manufacturing/User(1,0,0,0) · Manufacturing/Admin(1,1,1,1) · 其余域只读。
- `mrp.workorder`：Manufacturing/User(1,1,1,1) · Manufacturing/Admin(1,1,1,1) · Sales/User(1,0,1,0)。
- `product.template`：Products/Create(1,1,1,1) · Role/User(1,0,0,0) · 各业务域只读（Purchase/Inventory/Manufacturing User 均 r1）。
- `product.product`：同上模式。
- `res.partner`：Contact/Creation(1,1,1,1) · Sales/Purchase/Inventory/MRP 各域读或读写 · Portal/Public(1,0,0,0)。

## 3. Record rules 摘要（实测 ir.rule，按模型）

- `sale.order`(4)：multi-company（无组）；Portal 本人单据；Sales/User Own Documents Only→Personal Orders；…All Documents→All Orders。`sale.order.line`(5)：同上 + Inventory/User 读。
- `purchase.order`(2)/`purchase.order.line`(2)：multi-company；Portal 本人。**无"个人订单"限制 → 采购员可见全公司 PO**。
- `stock.move`/`stock.move.line`/`stock.quant`/`stock.lot`/`stock.picking.type`/`stock.warehouse.orderpoint`/`mrp.production`/`mrp.bom`/`mrp.workorder`/`product.template`：各 1 条 **multi-company**（无用户范围限制）。
- `product.product`：**0 条 record rule**。
- `res.partner`(2)：multi-company company 规则；portal/public 仅本人商业伙伴。

## 4. Baseline 结论与 Phase 1 要求

1. **跨公司隔离原生已布防**：几乎所有核心模型都有 multi-company rule（结合 company check），符合不变量 #1 的公司隔离方向；但需 Phase 1 实测"跨公司写入/读取被阻"（不变量 #1 退出条件）。
2. **无"运营只看自己的单"的出厂规则**（销售组除外）：采购/库存/生产/产品的 record rule 只按公司，不按用户 → 工厂OS 角色若要"操作员只见自己班组/仓库/订单"须自建 record rule（不变量 #8），不能靠原生默认。
3. **成本/报价/毛利字段**：sales user 对 sale.order.line 有读写（含单价）；purchase 域成员可见 PO 价格；无字段级 group 默认限制 → Factory OS 的"操作员默认不得读报价/供应商价/成本/毛利/系统设置"必须用字段 groups + 菜单外校验落地（不变量 #8 禁止仅隐藏菜单）。
4. **产品主数据**：业务用户（Purch/Inv/Mfg）对 product 只有读；创建/写属 Products/Create 组 —— Factory OS 的产品扩展字段需挂该组或自建 group。
5. **`stock.move.line` 全员可写**（Role/User r/w/c/u）与 `stock.quant` Role/User 只读：移动行宽写是原生设计（供任意用户操作单据），量化数字只读由引擎保证 —— 派生层（Dashboard/缺料）应读 quant/计算字段而非 move.line 汇总，避免与引擎口径不一致。
6. **验收基线**：本快照是"未配置用户"状态；Phase 1「Operator 不得经 URL/RPC 读取 Purchase Price / Customer List / Supplier Data / Admin Settings」（开发计划 §41 特别测试）将以本表为基线做差分测试。
