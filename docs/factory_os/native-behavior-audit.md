# Factory OS — Native Behavior Audit（Odoo 19 Community 实测）

Date: 2026-09-07（Phase 0 r2 复核；全新数据库复跑）
Authorities: ADR-002 / ADR-003 / ADR-004 · system-invariants #2/#3/#14 · 开发计划 §0.1/§6/§10/§19-§20/§24-§26/§39
方法：在全新 DB `factory_phase0_r2`（初始安装 sale_management,stock,purchase,mrp → 72 模块实测）上用 `odoo shell` 脚本做 create→action→全局 counts 差量 + 记录级断言；每次脚本独立 commit。脚本存 `/tmp/phase0_audit/*.py`（临时，不入库）；结果文件 `r2_*.txt` 同目录。

## 1. 产品类型与库存语义（Odoo 19 与旧记忆的关键差异）

- `product.template.type` 枚举仅 `consu`(Goods)/`service`/`combo`，**无 `product`/stockable**（源码 `addons/product/models/product_template.py:54-65`；DB `ir.model.fields` SEL 实测一致）。
- 是否管理库存 = `consu` + `is_storable`（stock 模块在 product.template 上新增独立 Boolean，`addons/stock/models/product.py:829-831`，label "Track Inventory"）；`product.product`、`sale.order.line`(:27)、`purchase.order.line`(:34)、`stock.move`(:177) 都有 related 副本（实测）。
- `tracking` selection：serial/lot/none（product_template.py:846-852）。
- Service 产品 `type='service'`；`combo` 仅 POS/销售组合用（本审计不展开）。
- 影响：所有配置/导入/测试脚本/未来 UI 一律使用 `is_storable` 表达"可存储物"。

## 2. 强制原生行为测试矩阵

| 测试 | 目的（对应合同） | 结果（r2 实测） |
|---|---|---|
| A 简单 SO 确认 | SO 确认到底生成什么（Goods storable / Goods plain / Service） | storable→outgoing picking+move(make_to_stock)；**plain(consu,非storable)→同样生成 delivery picking+move**；service→什么都不生成。**均不生成 MO** |
| B PO 确认 | 同上（采购侧） | storable→incoming picking；**plain 同样生成 incoming picking**；service→不生成 |
| C MRP 触发路径 | SO 确认/线路带 Manufacture 是否自动出 MO；MO 组件消耗与产出 | 产品带 Manufacture 路线、SO 行 route=Manufacture、is_mto=False → SO 确认**不创建 MO**（只出 delivery picking）；orderpoint.action_replenish 返回向导动作、**不直接生成 MO/PO**。手工建 MO 确认后组件消耗链与产出成立（见 C4R） |
| D 渐进采用 | 后期开启能力是否伪造/重写历史 | 产品改为 storable+Manufacture/Buy 路线后，**旧 SO 不回溯生成任何 MO/picking**（delta=0）；新 SO 仅多 1 个 delivery picking，仍无自动 MO → **原生不伪造历史** |

### A 证据（r2_test_A_simple_so_r2.txt）
```
A3R_RESULT S00009 storable   | picks 7->8 | moves 7->8 | MO 0->0   （WH/OUT/00008 confirmed, WH/Stock->Customers, move make_to_stock 10)
A3R_RESULT S00010 plain      | picks 8->9 | moves 8->9 | MO 0->0   （WH/OUT/00009 assigned, move make_to_stock 10)
A3R_RESULT S00011 service    | picks 9->9 | moves 9->9 | MO 0->0   （无 picking/move）
A4_RESULT S00003 service     | picks 0->0 | moves 0->0 | MO 0->0
A4_RESULT S00004 storable    | picks 0->1 | moves 0->1 | MO 0->0
```
注：plain goods 的 picking 在确认时即 `assigned` 且带 move_line（初版脚本用已移除的 `stock.move.line.product_uom_qty` 崩溃；r2 改用 `ml.quantity` 后完整输出）。

### B 证据（r2_test_B_purchase.txt）
```
B_CONFIRMED P00001 storable | picks 1->2 | moves 1->2 | MO 0->0   （WH/IN/00001 incoming assigned Vendors->WH/Stock, move 8.0 make_to_stock)
B_CONFIRMED P00002 plain    | picks 2->3 | moves 2->3 | MO 0->0   （同样 incoming assigned）
B_CONFIRMED P00003 service  | picks 3->3 | moves 3->3 | MO 0->0   （无 picking）
```

### C 证据（r2_test_C_mrp.txt / r2_test_C3_mo_trigger.txt / r2_test_C4_r2.txt）
```
C1_CONFIRM S00005 (产品 route=Manufacture) | MO 0->0 | picks 3->4 | MOs= []        （无自动 MO）
C2_SO_line routes=['Manufacture'] is_mto=False；C2_CONFIRM S00006 | MO 0->0 | MOs= [] （无自动 MO）
C3_TRIGGER action_replenish ok | mo 0->0 | po 3->3                                  （向导动作，不直产）
C4R_MO WH/MO/00003 confirmed | raw=[Comp 10.0 assigned WH/Stock->Production] | fin=[FG 5.0 assigned] | workorders=[]
C4R_MO_DONE state=done qty_produced=5.0  （lot_producing_ids=[LOT-C4R-0001] + qty_producing + raw picked → button_mark_done）
C4R_FG_QUANTS [( -5, LOT-C4R-0001, Production), (5, LOT-C4R-0001, WH/Stock)]
C4R_FIN_LINE_LINKS [(LOT-C4R-0001, 5.0, WH/MO/00003)]   ← move_line.move_id.production_id 可回溯到 MO
C4R_RAW_LINE Comp 10.0 | raw_mo= WH/MO/00003            ← move_line.move_id.raw_material_production_id 可回溯组件消耗
```
完成 API 事实修正：`mrp.production.button_mark_done` 存在于 `mrp/models/mrp_production.py:2219`（此前会话早期检索误记为缺失）；产出批次字段为复数 `lot_producing_ids`（M2M，:120），无单数 `lot_producing_id`；无工序时 `workorder_ids` 为空，完成逻辑仍在生产单本体（不用 workorder 模块兜底）。

### D 证据（r2_test_D_later_enable.txt）
```
D_DAY1_SO S00007 (plain, 无 route) 确认 | counts mo0 pick6 move6 po3
D_LATER_CAPABILITY_ON routes=['Manufacture','Buy']（产品 is_storable=True + 双路线）
D_AFTER_FLIP_NO_ACTION counts 不变 | delta_mo=0 delta_pick=0
D_OLD_SO_STILL S00007 state=sale | 原有 move 仍 1 条（未被改写）
D_NEW_SO S00008 | delta_mo=0 delta_pick=1（新订单只多 delivery picking，无自动 MO）
```

## 3. 关键结论（影响 Factory OS 设计）

1. **SO/PO 确认 ≠ 自动 MO**：即使产品/行带 Manufacture 路线（含 MTO 规则行）也不创建 MO；MO 只由补货引擎/调度器路径产生。与 ADR-003 的"简单执行与正式 MRP 分离"兼容：Factory OS 需要显式调用原生补货/调度（而非依赖 SO 确认）来触发 MO —— Phase 3 Supply/Production Gate 测试必须覆盖该触发入口（C3 暴露：orderpoint.action_replenish 是 UI 向导动作，不直接产出）。
2. **原生 picking 生成只认"装没装 stock + 产品类型/路线"**：storable 与 plain goods 的 SO/PO 确认都产生 picking/move（warehouse 默认 Deliver/Receive 路线），service 不产生。Safe Minimal（不装 stock 只装 sale）下 SO 确认不会产生任何 picking/move——**能力分层在原生侧 = addon 安装分层**，而不是配置开关。
3. **原生不伪造历史**：能力后开只影响新单据（D：旧 SO 零回溯；新 SO 多 delivery picking），与 ADR-004、不变量 #14 一致。
4. **Lot 追溯闭环可用**：成品 Lot→quant 双行（-Production/+WH/Stock）、move_line.move_id.production_id 与 raw_material_production_id 可支撑 DERIVED 追溯（不变量 #4）；`stock.traceability.report` 存在于 Community（stock/report/stock_traceability.py:22）。
5. **MO 完成**：Community 下生产单可直接 button_mark_done（19.0）；tracked 成品需先写 lot_producing_ids。

## 4. Capability Flag Reality Map（配置权威 vs 原生现实）

依据：configuration-schema.md（flags 行 24-31/71/80-82/107-109）。flags 语义已冻结为"只控制 Factory OS 能力/UI/流程，不动态装卸 addon"（progressive-adoption.md；开发计划 §0.1 L22）。本表记录原生现实约束：

| Factory OS flag | 原生现实（r2 实测） | 影响/处置 |
|---|---|---|
| sales_enabled=true | sale+sale_management 安装时：报价/订单可用；若 stock 未装 → 无 picking；若 stock 已装 → 任何 consu 货物行确认即出 delivery picking | flag 只控制工厂OS字段/UI；原生联动由 addon 安装面决定。**安装方案必须与能力分层绑定**（Safe Minimal = 不装 stock） |
| purchasing_enabled=true | purchase 安装后 PO 确认即 incoming picking（含 plain goods） | 同上；来料检验触发点（incoming_inspection_enabled）需挂在 picking validate/收货动作上 |
| inventory_enabled=true | stock 安装即全部原生库存行为（picking/quant/move）开启；无"部分启用"原生开关 | flag 开启=模块层已安装；flag 关闭但模块仍在 = UI 隐藏 ≠ 引擎停用（不变量 #8 禁止菜单隐藏当安全）→ Factory OS 服务层必须自身执行校验 |
| mrp_production_enabled=true | mrp 安装即有 MO/BOM/workorder；但 MO 不因 SO 确认自动出现，须补货/调度触发 | flag 开启 ≠ 自动 MRP；正式 MO 创建入口由 factory_os_production 显式调用原生补货或直接建单（ADR-003） |
| quality_enabled=true | **原生无 quality addon 可依赖** | 薄模型自建；成品质检 Gate（不变量 #6）与"requires inventory"（#11）全部落在自建 inspection 语义上 |
| delivery_enabled=true | delivery/stock_delivery 存在但默认未装；原生发货=stock.picking | flag 开启应触发 stock_picking 层展示与工厂OS发货状态字段；carrier 计费需另装 delivery（Phase 6 决策） |
| operations_enabled=true | mrp.workorder 存在（Community）；无工序时 MO.workorder_ids 为空 | 工序能力=需在 BOM/路线配置工序（routing）；flag 只是 UI/流程 |
| 质检三触发（incoming/process/final） | 原生无 quality 触发器模型 | 触发器挂在 factory 自建 inspection + picking/MO 生命周期点 |

## 5. Quality Community 现实审计（开发计划 §19-§20 分支裁决）

- 实测：addons 目录无 `quality*`；DB registry 无 `quality.check`/`quality.point`/`quality.alert`（EXIST=False）；无 enterprise 目录。
- 裁决：走开发计划 §20「如果当前没有 Quality」路径（L875-884）——**只自建两个薄模型** `factory.quality.inspection` / `factory.quality.ncr`，不复制完整 Odoo Quality。映射已冻结进 model-mapping.md #14/#15。
- 对不变量 #5/#6 的落实：FAIL/拒收数量必须进入受控库存处置（isolation/scrap/return），由 factory 服务层调用 stock 动作实现；成品质检 Gate 用自建 inspection 状态 + 服务校验实现，不依赖原生菜单。

## 6. 原生状态/字段 API 事实清单（供 Phase 1+ 直接引用）

- `stock.move` 无 `name`、无 `quantity_done`；有 `product_uom_qty`/`quantity`/`origin`/`sale_line_id`/`purchase_line_id`/`production_id`/`raw_material_production_id`/`procure_method`（实测 _fields）。
- `stock.move.line` 无 `product_uom_qty`、无 `qty_done`；数量字段为 `quantity`；有 `lot_id`/`move_id`（实测）。
- `mrp.production` 无 `procurement_group_id`；有 `lot_producing_ids`（复数 M2M）、`qty_producing`、`move_raw_ids`/`move_finished_ids`/`workorder_ids`。
- `procurement.group` 模型不存在（registry EXIST=False）。
- 无持久 `stock.inventory`/`stock.count` 模型；盘点交互在 19 走 `stock.quant` + 向导（`stock.request_count`/`stock.inventory.adjustment.name` 等，addons/stock/wizard/）。

## 7. Phase 3+ 必须补测项（本 Phase 不阻塞）

1. 通过调度器/cron 环境显式触发补货生成 MO 的完整链路（C3 只证明 action_replenish 是向导动作）。
2. 盘点向导端到端（quant 调整 + 差异过账）。
3. delivery addon 安装后的 carrier/费用对发货流程的影响。
4. 多公司 record rule 在跨公司访问下的实际拦截（IRL 权限矩阵测试）。
