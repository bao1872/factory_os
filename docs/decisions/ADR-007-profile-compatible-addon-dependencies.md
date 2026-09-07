# ADR-007 Profile-Compatible Addon Dependencies

Status: **Proposed**（NOT Accepted）
Date: 2026-09-07
Owner: 用户 Gate 裁决（Phase 0 dependency-closure STOP）

## Context — conflict evidence

ADR-006（Accepted）冻结 Technical Installation Profiles 0–3：Profile 1 = Inventory & Purchasing（**无 MRP**）、Profile 2 = + Formal MRP、Profile 3 = + thin Quality；`delivery_enabled` = Inventory 之上的业务层能力（可 ON↔OFF、不绑 Odoo `delivery` addon）；`purchasing_enabled requires inventory_enabled`（v0.1 无 Purchase-only）；Inventory-only（Inventory ON + Purchasing OFF）是允许形态；保持 **8 个** Factory OS addons。

但计划中的 Factory OS addon manifest 依赖闭包（开发计划原文，非臆测）与上述 profile 契约冲突：

```
开发计划 §8  （L515-524） factory_os_supply    deps = core + orders + purchase + purchase_stock + stock + mrp
开发计划 §13 （L674-682） factory_os_production deps = core + orders + supply + mrp + stock
开发计划 §23 （L972-980） factory_os_delivery   deps = orders + production + quality + stock + delivery
开发计划 §28 （L1107-1115）factory_os_dashboard  deps = orders + supply + production + quality + delivery（全部内部）
```

原生 manifest 源码事实（odoo-19/addons，`auto_install` 桥，2026-09-07 实测）：

```
sale        depends=[sales_team, account_payment, utm]
stock       depends=[product, barcodes_gs1_nomenclature, digest]        （不含 account！）
mrp         depends=[product, stock, resource]                          （不含 purchase）
purchase    depends=[account]                                           （不含 stock）
sale_stock    auto depends=[sale, stock_account]
stock_account auto depends=[stock, account]
purchase_stock auto depends=[stock_account, purchase]
sale_mrp      auto depends=[mrp, sale_stock]
mrp_account   auto depends=[mrp, stock_account]
purchase_mrp  auto depends=[mrp, purchase_stock]
sale_purchase auto depends=[sale, purchase]
```

**闭包推演（决定性）**：在含 `sale`（经 orders）的库安装 `factory_os_supply` → manifest 直接依赖 `mrp` → `mrp` 随装；`stock`+`account` 齐 → `stock_account` 自动；`sale`+`stock_account` → `sale_stock` 自动；`mrp`+`sale_stock`/`stock_account`/`purchase_stock` → `sale_mrp`/`mrp_account`/`purchase_mrp` 自动。即 **Profile 1 安装面物理包含 MRP 引擎与 MTO 自动建 MO/RFQ 机制（Profile 2 专属能力，Test E/H3）**——Profile 1 会偷偷变成 Profile 2，重新制造 ADR-006 刚消灭的"引擎在、能力未开"假关闭问题（闭包面复现）。

同类冲突三处：

| 冲突 | 现状 | 后果 |
|---|---|---|
| Supply vs MRP | `factory_os_supply` 计划依赖含 `mrp` | 启用 Profile 1 → MRP 引擎+桥已装（sale_mrp 等）→ MTO 机制在位 |
| Inventory-only | ADR-006 允许 Inventory ON + Purchasing OFF | `factory_os_supply` 强依赖 `purchase` → Purchase 引擎/substrate 在 Inventory-only 库必然存在 |
| Delivery | ADR-006 §E：Delivery 是 Inventory 上业务层能力 | 计划依赖仍含 `production`（→supply→mrp）+ `quality` + 原生 `delivery` → 基础发货强制 MRP/QC/carrier |

`factory_os_dashboard`（"产品体验核心"）若按计划依赖全部内部 addon，则 Profile 0 安装即强制最高引擎面——若订单看板需在 Profile 0 可用，该依赖必须收敛。

**治理审计漏检**：governance-audit v1.0.2 的 18 项检查全部 PASS，但无任何"manifest 依赖闭包 vs Technical Installation Profile 契约"校验项——因此放过了 `supply→mrp`。§Audit check 在本 ADR 中补为永久检查。

## Decision intent（Proposed — 待用户裁决后转 Accepted）

**方向：保持 8-addon；每个 addon 的 manifest 依赖闭包（含 auto_install 桥）不得超过其所属 profile 允许的原生引擎面。** 关键不变量：

> Installing an addon assigned to Profile N must not force native engines belonging only to Profile N+1.

### 目标依赖闭包（裁决参考）

| Factory OS addon | Factory 依赖 | 原生依赖 | 闭包后原生引擎面 | 最小/所属 Profile | 说明 |
|---|---|---|---|---|---|
| `factory_os_core` | — | base/product/mail/web/contacts 等原生最小集 | —（无 stock/purchase/mrp） | Profile 0 | 无销售/采购/库存/MRP 业务逻辑 |
| `factory_os_orders` | core | `sale` | {sale→account} | Profile 0 | 无 `sale_stock`（ADR-006 已决） |
| `factory_os_supply` | core + orders | `stock` + `purchase` | {stock, purchase, account}；自动桥 stock_account/sale_stock/purchase_stock/sale_purchase；**无 mrp** | Profile 1 | 拥有 Inventory + Purchasing workflow + Receipt + Availability + basic supply status；任何需 mrp.bom/production/MTO/Manufacture route/BOM explosion 的能力在 Profile 2 前不可用 |
| `factory_os_production` | core + orders + supply | `mrp`（stock/purchase 经 supply 已在） | {stock, purchase, mrp, account}；自动桥 sale_mrp/mrp_account/purchase_mrp | Profile 2 | Formal BOM/MRP 自此开始；MRP-aware shortage/demand 可在此层实现并继续经 Supply UI/服务暴露（**不建第二缺料真相**，ADR-002/003 不变） |
| `factory_os_quality` | core + orders | `stock`（最低：incoming/final QC 操作 picking/quant/lot） | {stock, …} **无 mrp** | Profile 1 substrate；Profile 3 时点安装 | 保持两薄模型；Incoming/Final inspection 不强制 MRP；Process inspection 仅在 MRP 存在时条件启用（registry 守卫） |
| `factory_os_delivery` | core + orders | `stock` | {stock, …}；**无 production/quality/Odoo delivery 依赖** | Profile 1 substrate（业务能力） | 操作 stock.picking；production/quality 相关发货 gate 为存在时条件集成；Odoo `delivery`/carrier optional（Post-MVP） |
| `factory_os_dashboard` | core + orders（base board/health） | — | 不引原生引擎 | Profile 0 起可用 | supply/production/quality/delivery 数据瓦片经 registry 模型存在性守卫可选显示，**不静态依赖**高 profile addon |
| `factory_os_connector` | core + orders（最低订单/产品同步面） | mail/bus/web | 不引引擎 | 兼容全部 | 中央平台同步；最后开发 |

### Purchasing 语义修订（Proposed amendment to ADR-006 §A/§D）

8-addon 结构使 `factory_os_supply` 必须依赖 `purchase`（扩展 purchase.order）→ Inventory-only 工厂物理上有 Purchase substrate，即使 `purchasing_enabled=false`。因此 **`purchasing_enabled` 从 ADR-006 §A 的"进入 profile 后单调（engine-backed）"改为 Workflow/Business capability**：

```
inventory_enabled      ENGINE-BACKED / monotonic   Profile 1 truth（不变）
purchasing_enabled     WORKFLOW / BUSINESS         requires inventory_enabled；ON ↔ OFF；
                                                   不宣称 Odoo purchase addon 是否存在（substrate 常驻）
mrp_production_enabled ENGINE-BACKED / monotonic   Profile 2 truth（不变）
quality_enabled        单调（Profile 3 属主，薄 addon）          （不变）
delivery_enabled       WORKFLOW / BUSINESS         ON ↔ OFF（不变，ADR-006 §E）
```

**为何与 stock/mrp 不同（证据）**：
- 安装 `stock` 会经 `sale_stock` **自动改变 SO 确认行为**（Goods SO→picking/move，Test A）；安装 `mrp` + MTO 配置会在 SO 确认时**自动建 MO/RFQ**（Test E/F/H3）——自动副作用，flag 无法抑制 → 必须 engine-truth 单调。
- `purchase` substrate 本身**无 SO 确认自动副作用**：自动 RFQ/MO 只由 MTO/Buy route 配置触发（Test F），而 MTO route 分配属 Profile 2 受控能力；普通 PO 需显式人工/补货动作创建。因此 Purchase addon 在位 ≠ Factory OS Purchasing workflow 已启用。
- 残余风险（必须登记）：原生 PO 创建入口（菜单/RPC）需要 Factory OS 角色安全收紧（Phase 1 不授予原生 `purchase.group_purchase_*` 于未启用采购的工厂）；MTO route 分配 Profile 2 受控（Phase 4 校验）。

仍强制：`purchasing_enabled=true → inventory_enabled=true`；v0.1 仍**不支持 Purchase-only**（Deferred/Post-MVP）。

### Phase-Gate realignment（Proposed）

| Phase | 范围 | 退出条件是否需 MRP |
|---|---|---|
| Phase 1 | Core / Security / Configuration / **Profile installer foundation**（按 profile 闭包装引擎+factory addon；单调校验；引擎在而 flag 关探测） | 否 |
| Phase 2 | `factory_os_orders`（core + sale）实现 | 否 |
| Phase 3 | **Supply & Inventory**：Inventory engine / PO / Receipt / stock move-quant / Incoming / Availability / purchasing→inventory / security | **否**（BOM-driven Material Demand 不作为 Phase 3 退出条件，否则强装 mrp） |
| Phase 4 | **Formal MRP + BOM-driven Supply**：BOM / Explosion / Demand / Available / Incoming / Shortage / MO / 组件消耗 / 成品数量与 Lot / MTO | 是（本相引入 mrp） |

缺料引擎仍是原生真相的派生视图——本修订只改**时序**（Phase 3/4 边界），不改 Source of Truth（ADR-002/003 不变）。Quality/Delivery/Dashboard/Connector 按其 profile 时点交付（§目标依赖闭包表），不属本修订范围外新增阶段。

## Alternatives Considered

- **新增第 9 个 Factory OS bridge addon**（如把 supply 拆成 inventory / purchasing 两个）：用户已在 ADR-006 §B 裁决否决 8-addon 外扩；上表目标闭包证明 8-addon 可实现 → 不引入。
- **supply 保留 `mrp` 依赖、Profile 1/2 合并为一级**：违背用户已 Accept 的 ADR-006（Profile 2 才装 MRP）与 Test G/H 的渐进实证 → 拒绝。
- **supply 去掉 `purchase` 依赖、purchasing 扩展用 registry 守卫**（Inventory-only 无 purchase substrate；purchasing 启用时单调加装 purchase+purchase_stock）：技术上干净，但把"Purchasing+Inventory+Material Requirement"拆出 supply 模块、且 `purchase.order` 扩展需运行时守卫——违背开发计划 §8「不要拆成两个 addon」与用户 §3 目标（supply deps = core+orders+stock+purchase）→ 记录备选，不采纳为 v0.1 目标。
- **运行时"假依赖"**（manifest 不声明但代码 import）：Odoo 加载即崩 → 拒绝。
- **Purchasing 维持 engine-backed 单调**（现状 ADR-006 §A）：与"Profile 1 Inventory-only 物理含 purchase substrate"自相矛盾，重新制造假关闭状态 → 本 ADR 提议修订。

## Consequences（若 Accepted）

- 开发计划：§8 supply deps 去 `mrp`（→ core+orders+stock+purchase）；§23 delivery deps 收敛（→ core+orders+stock，去 production/quality/delivery）；§28 dashboard deps 收敛（→ core+orders + registry 守卫可选瓦片）；quality 依赖显式（无 mrp 硬依赖）；§43/§44 Phase 3/4 Gate 边界按 realignment 更新；§9 purchasing 注释补 substrate/workflow 语义。
- `addon-dependency-map.md`：§2 CONFLICT 行按目标闭包修订；§6 矩阵转正。
- `configuration-schema.md` / `configuration-dependency-graph.md`：`purchasing_enabled` 分类改 Workflow/Business（requires inventory、ON↔OFF、不宣称 addon 存在）；inventory/mrp 维持 engine-backed monotonic。
- `progressive-adoption.md`：Profile 表措辞同步（Profile 1 purchase substrate 常驻 + purchasing workflow flag 控制）。
- governance-audit：新增永久 **profile↔manifest dependency-closure** 检查项；v1.0.4 re-audit。
- **Supersedes 范围（若 Accepted）**：修订 Accepted ADR-006 的 §A（purchasing 单调分类 → workflow）与 §D Profile 1 措辞（purchase 底材常驻、非"当选中采购"），其余 ADR-006 决策（引擎型单调、8-addon、Profile 0–3、delivery 业务层、Business Preset≠Technical Profile、无卸载/降级）**维持不变**。不引入正常态引擎卸载/降级；仅到"使 manifest 依赖闭包与 profile 契约一致"的必要程度。
- 本 ADR **Accepted 前**：authority 文档仅可加 BLOCKED/evidence 标记（addon-dependency-map §0/§6、native-behavior-audit §0、technical-risks Gate/R11），不静默改写计划依赖与 profile 语义。

## Verification（若 Accepted）

- 闭包契约测试（Phase 1 profile installer 验收）：按 Profile 0/1/2 分别初始化 → 断言引擎模型存在/不存在与自动桥集合，等于 §目标闭包表（Test G/H 扩展：装 supply 的库断言 `mrp.production`/`sale_mrp` 不存在；装 production 的库断言存在）。
- 永久审计检查（新增到 governance-audit）：对每个 Technical Installation Profile 解析 manifest 传递闭包 + auto_install 桥 → 与 profile 契约引擎集比对；仅当 `actual closure == allowed profile engine closure` 通过。
- A–H harness（scripts/audit/phase0）Odoo 升级后重跑；E/F/H3 断言 MTO 只在含 mrp 的 profile 触发。
- grep 验证：`supply` manifest 无 `mrp`；delivery manifest 无 production/quality/`delivery`；dashboard manifest 无高 profile 硬依赖；purchasing 语义无 engine-backed 残留。

## Supersedes / Superseded By

- Superseded By：None（Proposed，待裁决）。
- 若 Accepted：按上「Supersedes 范围」修订 ADR-006 两处措辞（§A purchasing 分类、§D Profile 1 purchase 表述），不整体取代 ADR-006。
