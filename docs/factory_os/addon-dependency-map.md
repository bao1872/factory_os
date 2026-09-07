# Factory OS — Addon Dependency Map（Odoo 19 Community Reality）

Date: 2026-09-07（Phase 0 r2）
Authorities: 开发计划 §3（addon 结构）、§39/§40；本文件把"计划依赖"与"Community 原生可用性"对照，供 manifest 设计与 Phase 1 验收使用。

## 1. 审计实例事实（Evidence）

- 代码库 `odoo-19/addons`：638 个 addon；`odoo/release.py:15` = 19.0 FINAL；无 enterprise。
- 审计数据库 `factory_phase0_r2` 安装 72 模块（`sale_management,stock,purchase,mrp` 初始安装后依赖自动带入）。关键原生模块实测可用：

```
sale sale_management sale_stock sale_mrp sale_purchase sale_purchase_stock
purchase purchase_stock purchase_mrp mrp mrp_account stock stock_account
stock_delivery delivery sales_team product contacts（可用，未装）mail base web
```

- 实测 **不存在**：`quality`、`quality_control`、`quality_mrp`、`mrp_workorder`（已并入 mrp）、`procurement`（procurement.group 移除）。

## 2. 8 个 Factory OS addon 计划依赖 → 原生可用性

| Factory OS addon | 计划依赖（开发计划引用行） | 原生状态（实测） | 结论 |
|---|---|---|---|
| factory_os_core | base/mail/web/contacts/product（L180-188） | 全部存在（contacts 在 addons/，未被审计库安装但可装） | 无阻塞 |
| factory_os_orders | factory_os_core + sale（**ADR-006 Accepted：去 sale_stock**，原 L315-321 失效） | sale_stock 存在且已安装（引擎级库）；sale.order.line 的 route_ids/is_mto/_action_launch_stock_rule 实测存在（sale_stock/models/sale_order_line.py:385） | 无阻塞；orders 只含基础订单执行（Profile 0 真实安装面=仅 sale，Test G）；route/库存联动由 supply 扩展 sale.order、delivery 扩展 stock.picking 提供 |
| factory_os_supply | core + orders + purchase + purchase_stock + stock + mrp（L514-523） | 全部存在；purchase_mrp 也已自动安装 | 无阻塞；mrp 依赖使 MO→组件采购可用（purchase_mrp） |
| factory_os_production | core + orders + supply + mrp + stock（L671-679） | mrp 为 Community 模块，含 mrp.bom/production/workorder/workcenter（实测 EXIST） | 无阻塞 |
| factory_os_quality | 无原生 quality 可依赖 → core（+按需 stock/purchase/mrp 触发器） | **quality.check/point/alert 全部缺失**（实测 False） | 走开发计划 §20「当前没有 Quality」路径：仅建 factory.quality.inspection / factory.quality.ncr 两薄模型；不允许复制 Odoo Quality |
| factory_os_delivery | orders + production + quality + stock + delivery（L969-977） | delivery 与 stock_delivery 存在（未装）；delivery 缺失时以 stock 为最低依赖（L979） | 无阻塞；按需 delivery |
| factory_os_dashboard | orders/supply/production/quality/delivery（内部，L1102-1110） | 内部依赖，不引原生业务模块 | 无阻塞 |
| factory_os_connector | 无原生 ERP 强依赖（中央平台，L1219-1237） | 复用 mail/bus/web 基础设施 | 无阻塞 |

## 3. Community 现实缺口（影响建模）

| 原计划假设 | Community 19 实测 | 对 Factory OS 的影响 |
|---|---|---|
| 扩展 `quality.*`（PRD §36 复用清单含 quality.*；开发计划 §20 第一路径） | 无任何 quality addon（Enterprise-only） | QC 映射冻结为 THIN CUSTOM（model-mapping.md #14/#15）；成品质检 Gate（不变量 #6）须建在自建 inspection 模型之上 |
| 复用"补货 procurement 组"思路 | `procurement.group` 模型移除 | 原生补货仍经 stock.rule/orderpoint 工作（测试 C3）；Factory OS 缺料/追溯为 DERIVED，不依赖旧 procurement API |
| workorder 独立模块 | `mrp_workorder` 并入 `mrp`，模型仍为 mrp.workorder | operations_enabled 依赖仍成立；manifest 不需列 mrp_workorder |
| 持久盘点单（stock.inventory 风格） | 无 stock.inventory/stock.count 模型；盘点改为 stock.quant + 向导（stock.request_count / stock.inventory.adjustment.name 等，stock/wizard/） | 盘点入口按原生 19 向导设计；不写平行盘点表 |
| 产品 type='product' | 枚举仅 consu/service/combo（product_template.py:54-65）；"可存储物" = consu + `is_storable`（stock/models/product.py:829） | 配置/导入/UI 全部改用 is_storable 语义（已同步 configuration 权威无需改——配置文档未用 type='product'） |

## 4. 桥接模块自动安装效应（必须知情）

审计库同时安装了 sale+mrp+purchase+stock 后，以下桥接模块自动带入并**立即生效**：

- `sale_stock`：SO 确认→ `_action_launch_stock_rule`（sale_order.py:213-215）→ 生成 delivery picking/stock.move（测试 A）。
- `purchase_stock`：PO 确认→ incoming picking/stock.move（测试 B）。
- `purchase_mrp` / `sale_mrp`：产品带 Manufacture/Buy 路线时补货可生成 MO（测试 C）；仓库默认含 Manufacture、Buy 两条路线（实测 ALL_ROUTES）。

**含义（ADR-006 Accepted 更新）**：能力开关与原生引擎的关系 = **Technical Installation Profile**（单调）——启用引擎型能力（库存/正式 MRP/采购/质量）执行受控、可审计、单调的原生 addon profile 安装（含 auto_install 桥接）；v0.1 无正常 ON→OFF、无原生引擎卸载/降级；workflow/UI 子能力只控 Factory OS UI/流程/字段可见性。Safe Minimal（Profile 0）物理上不装这些引擎与桥接（Test G：模型不存在），因此不存在"已装引擎而 flag 关"的假关闭状态；引擎若绕过 Factory OS 被安装，Phase 1 一致性检查负责探测并阻止矛盾配置（详见 configuration-dependency-graph / configuration-schema）。

## 5. manifest 设计约束（ADR-006 Accepted 后生效）

1. **保持 8-addon 架构**：不新增任何第 9 个 Factory OS bridge addon（`factory_os_orders_stock` 之类被裁决否决）。
2. `factory_os_orders` manifest = `factory_os_core + sale`（**不再依赖 `sale_stock`**）；库存/物料视角归 `factory_os_supply` 扩展 `sale.order`，发货/追溯视角归 `factory_os_delivery` 扩展 `stock.picking`。
3. `factory_os_quality` 不得在 manifest 声明不存在的 quality* 依赖；始终走 Community thin 路径（factory.quality.inspection/ncr）。
4. `factory_os_delivery`：最低依赖 `stock`（delivery picking 即发货基础）；**不依赖也不主动安装 Odoo `delivery` addon**（carrier/运费能力 optional，Post-MVP 再评估）。
5. 安装由向导按 Technical Installation Profile 0–3（progressive-adoption）映射原生引擎与 factory addon：单调（进入后不卸载/不降级），升级只增；`purchasing` 仅在 `inventory` profile 内可选（v0.1 无 Purchase-only）。
6. 若未来工厂启用 Enterprise quality addon，需新增映射版本（本 Phase 0 冻结 Community）。
