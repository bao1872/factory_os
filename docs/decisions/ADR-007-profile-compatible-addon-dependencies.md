# ADR-007 Profile-Compatible Addon Dependencies & Capability Classification

Status: **Accepted**（2026-09-07，用户 Gate 裁决 Accept with final architecture）
Date: 2026-09-07
Owner: 用户 Gate 裁决（Phase 0 dependency-closure STOP → Accepted）
Supersedes: ADR-006 中与依赖闭包/profile 契约/能力分类冲突的必要部分（§Decision 范围），其余 ADR-001~006 保持 active。

## Context — conflict evidence

ADR-006（Accepted）冻结 Technical Installation Profiles 0–3 与能力单调语义。但计划中的 Factory OS addon manifest 依赖闭包（开发计划原文，非臆测）与 profile 契约冲突：

```
开发计划 §8  （factory_os_supply）    deps = core + orders + purchase + purchase_stock + stock + mrp
开发计划 §13 （factory_os_production）deps = core + orders + supply + mrp + stock
开发计划 §23 （factory_os_delivery）  deps = orders + production + quality + stock + delivery
开发计划 §28 （factory_os_dashboard） deps = orders + supply + production + quality + delivery（全部内部）
```

原生 manifest 源码事实（odoo-19/addons，`auto_install` 桥，2026-09-07 实测）：

```
sale        depends=[sales_team, account_payment, utm]
stock       depends=[product, barcodes_gs1_nomenclature, digest]
mrp         depends=[product, stock, resource]
purchase    depends=[account]
sale_stock    auto depends=[sale, stock_account]
stock_account auto depends=[stock, account]
purchase_stock auto depends=[stock_account, purchase]
sale_mrp      auto depends=[mrp, sale_stock]
mrp_account   auto depends=[mrp, stock_account]
purchase_mrp  auto depends=[mrp, purchase_stock]
sale_purchase auto depends=[sale, purchase]
```

**闭包推演（决定性）**：在含 `sale` 的库安装 `factory_os_supply`（依赖 `mrp`）→ MRP 引擎随装 → `sale_mrp`/`mrp_account`/`purchase_mrp` 自动桥 → **Profile 1 安装面物理包含 MRP 引擎与 MTO 自动建 MO/RFQ 机制（Profile 2 专属能力，Test E/H3）**——Profile 1 会偷偷变成 Profile 2，"引擎在、能力未开"假关闭问题在闭包面复现。

同类冲突三处：supply→mrp（Profile 1 变 2）；delivery→production/quality/native delivery（基础发货强制 MRP/QC/carrier）；dashboard→全部内部 addon（Profile 0 起即强制最高引擎面）。`quality` 原生依赖表述含糊：若含 mrp 硬依赖则 Incoming/Final QC 被绑到 MRP。purchasing 单调分类（ADR-006 §A）与"supply 依赖 purchase → Inventory-only 工厂物理含 purchase substrate"冲突。

**治理审计漏检**：governance-audit v1.0.2/1.0.3 无"manifest 依赖闭包 vs Technical Installation Profile 契约"校验项——放过了 `supply→mrp`。§Profile Closure Permanent Test 在本 ADR 中升格为**永久架构验证**（含规范化 PROFILE_CONTRACTS 与算法），所有 addon 依赖变更强制复检。

## Decision（Accepted）

**方向：保持 8-addon；8 个 addon 的 manifest 依赖闭包（direct + transitive + auto_install bridges）不得超过所属 profile 允许的原生引擎面；Quality 不是 MRP 之后的必经层，而是 Inventory 之上的独立扩展；Purchasing 是 Workflow/Business capability 而非 engine-backed monotonic。**

关键不变量：

> Installing an addon assigned to Profile N must not force native engines belonging only to Profile N+1.

### 1. Installation Graph — FINAL（能力图，非单一阶梯）

**不把技术架构描述成严格成熟度链 `P0→P1→P2→P3`**（Quality 不需要 Formal MRP）。最终依赖图：

```text
P0 — Base / Orders
         │
         ▼
P1 — Inventory Substrate
    │         │          │
    ▼         ▼          ▼
Purchasing  Quality   Delivery
workflow    Extension  workflow
(ON<->OFF)  (addon,   (ON<->OFF,
            requires   requires P1,
            P1, NOT    NOT P2/Q)
            P2)
    │
    ▼
P2 — Formal MRP
```

更精确的模块化表述：

```text
P0
sale
core
orders

P1
+ stock
+ purchase substrate
+ supply

P2
+ mrp
+ production

Q
+ quality
requires P1
does NOT require P2

D
+ delivery workflow
requires P1
does NOT require P2/Q
```

"小工厂只做出货检查、但没有正式 MRP"因此真实成立。**User-facing Quick Start presets 保持不变**；Business Preset ≠ 本技术图。

### 2. Canonical capability relations — FINAL

```text
inventory
    ENGINE-BACKED / MONOTONIC

mrp
    ENGINE-BACKED / MONOTONIC
    requires inventory

quality
    FACTORY-ADDON-BACKED / MONOTONIC
    requires inventory
    does NOT require mrp

purchasing
    WORKFLOW / BUSINESS
    requires inventory
    ON <-> OFF

delivery
    WORKFLOW / BUSINESS
    requires inventory
    ON <-> OFF
```

Engine-backed monotonic（真实行为依赖原生引擎安装、进入即激活、v0.1 无 ON→OFF）：`inventory_enabled`、`mrp_production_enabled`。Factory-addon-backed monotonic（依赖 `factory_os_quality` 安装激活、语义同单调、v0.1 无 addon/profile downgrade）：`quality_enabled`。Workflow/Business（可 ON↔OFF，只控 Factory OS workflow/menu/roles/config，不宣称原生 addon 存在与否）：`purchasing_enabled`、`delivery_enabled`。

### 3. EXACT 8-ADDON MANIFEST CONTRACT（Development Authority）

以下依赖列表成为开发权威（写入开发计划与 addon-dependency-map）。**无第九个 addon。**

#### 3.1 factory_os_core

```python
"depends": [
    "base",
    "mail",
    "web",
    "contacts",
    "product",
]
```

不得依赖：`sale` / `purchase` / `stock` / `mrp`。

#### 3.2 factory_os_orders

```python
"depends": [
    "factory_os_core",
    "sale",
]
```

**禁止出现** `sale_stock` / `stock` / `purchase` / `mrp`。

Ownership：Customer order / Committed Date / Requested Date / Manual execution state / Manual progress / Health base / Notes & Attachments。

#### 3.3 factory_os_supply

```python
"depends": [
    "factory_os_core",
    "factory_os_orders",
    "stock",
    "purchase",
    "sale_stock",
    "purchase_stock",
]
```

**直接声明 `sale_stock` 与 `purchase_stock`**——有意为之，非"多装引擎"：supply 必须使用 `SO ↔ stock.move`、`PO ↔ stock.move/picking`、incoming / delivery movement 这些 bridge 字段/行为。它们**不增加新 Profile 层级**：P1 已同时拥有 sale + stock + purchase，Odoo 自动装这些 bridge；显式声明只把加载顺序与 API 契约写死。**严格禁止** `mrp` / `sale_mrp` / `purchase_mrp`。

Supply 属 Inventory substrate。MRP 前 ownership：Warehouse / Location / Quant / PO / Receipt / Incoming / Reservation / Availability / Lot·Serial / Reorder / Scrap / Inventory Count / Basic supply status。无 BOM explosion、无 `mrp.production` 依赖、无制造物料需求计算。

#### 3.4 factory_os_production

```python
"depends": [
    "factory_os_core",
    "factory_os_orders",
    "factory_os_supply",
    "stock",
    "mrp",
    "sale_mrp",
    "purchase_mrp",
]
```

Profile P2 自此开始。MRP 才第一次正式进入 Factory OS dependency closure。Ownership：BOM / MO / Work Order / MTO / Manufacturing demand / BOM explosion / Component consumption / Finished output / MRP-aware shortage integration。**Shortage 保持 DERIVED**——不建第二本物料需求账（ADR-002/003 不变）。

#### 3.5 factory_os_quality

```python
"depends": [
    "factory_os_core",
    "factory_os_orders",
    "stock",
]
```

**不依赖** `factory_os_supply` / `factory_os_production` / `mrp` / `purchase`。Incoming/Final inspection 只需要真实库存/批次/移动。Process inspection 仅当 `"mrp.production" in self.env.registry` 时开放对应集成（registry 守卫）——**不能为了可选 Process QC 把所有 Quality 工厂强制升级成 MRP 工厂**。

Community Quality 保持**恰好两个薄模型**：`factory.quality.inspection` / `factory.quality.ncr`。禁止 manifest 依赖 `quality` / `quality_control` / `quality_mrp`（Community 无此 addon，实测 EXIST=False）。

#### 3.6 factory_os_delivery

```python
"depends": [
    "factory_os_core",
    "factory_os_orders",
    "stock",
]
```

**严格禁止硬依赖** `factory_os_production` / `factory_os_quality` / `mrp` / `delivery`。真相对象 = `stock.picking`。Quality Gate / Production 状态若存在：条件读取；不存在：Delivery 仍独立工作。未来实现模式（本任务不实现）：

```python
def _factory_quality_available(self):
    return "factory.quality.inspection" in self.env.registry

def _factory_mrp_available(self):
    return "mrp.production" in self.env.registry
```

Odoo `delivery` addon（carrier/运费）保持 optional / Post-MVP。

#### 3.7 factory_os_dashboard

```python
"depends": [
    "factory_os_core",
    "factory_os_orders",
]
```

**不得依赖** `factory_os_supply` / `factory_os_production` / `factory_os_quality` / `factory_os_delivery` / `stock` / `mrp`。可选看板区块后续必须走 registry 守卫模式：

```python
if "stock.picking" in self.env.registry:
    # show inventory/delivery tile

if "mrp.production" in self.env.registry:
    # show production tile

if "factory.quality.inspection" in self.env.registry:
    # show quality tile
```

Dashboard base code 不得静态引用可选模型字段/类；不得建假 dashboard 缓存/真相表；保持 derived/read-only。否则 Dashboard 本身成为"安装所有模块"的木马。

#### 3.8 factory_os_connector

最低契约：

```python
"depends": [
    "factory_os_core",
    "factory_os_orders",
]
```

Phase 8 仅当 connector 实现设计完成后才允许增加**纯技术**依赖。不得为了同步某字段把 Supply/MRP/Quality/Delivery 变成静态 manifest 依赖；可选模型数据必须条件检测（registry 守卫）。

### 4. PURCHASING CLASSIFICATION — FINAL（ADR-006 §A 修订）

`purchasing_enabled` 从 **Engine-backed monotonic** 改为 **Workflow / Business capability**：

```text
technical_key:   purchasing_enabled
storage:         res.company.factory_purchasing_enabled
default:         false
requires:        inventory_enabled == true
transition:      false -> true : allowed
                 true  -> false: allowed subject to open-transaction guards
native substrate: purchase/purchase_stock may remain installed whenever Inventory substrate exists
meaning:         whether Factory OS purchasing workflow/menu/roles/config are active
does NOT mean:   whether Odoo purchase addon physically exists
```

- **无 Purchase-only**：`purchasing_enabled=true ∧ inventory_enabled=false` ⇒ INVALID。
- Inventory-only 合法：`inventory_enabled=true ∧ purchasing_enabled=false` ⇒ VALID。
- Purchasing OFF 时，普通 Factory OS 用户**不得获得原生 purchase groups 或采购菜单**；Admin/系统级原生模块存在 ≠ Factory OS workflow enablement（Phase 1 安全收紧不授予原生 `purchase.group_purchase_*` 于未启用采购工厂）。

**为何与 stock/mrp 不同（证据）**：安装 `stock` 经 `sale_stock` 自动改变 SO 确认行为（Goods SO→picking，Test A）；安装 `mrp` + MTO 配置在 SO 确认自动建 MO/RFQ（Test E/F/H3）——自动副作用，flag 无法抑制 → 必须 engine-truth 单调。而 `purchase` substrate 本身无 SO 确认自动副作用（自动 RFQ/MO 只由 MTO/Buy route 触发，Test F；MTO route 分配属 Profile 2 受控能力）；普通 PO 需显式人工/补货动作创建 → Purchase addon 在位 ≠ Factory OS Purchasing workflow 已启用。

### 5. QUALITY CLASSIFICATION — FINAL（ADR-006 §A/§D 澄清）

`quality_enabled` 是 **Factory-addon-backed monotonic capability**，**不是** "requires Formal MRP"：

```text
quality_enabled = true
    requires inventory_enabled = true
    does NOT require mrp_production_enabled
```

一旦 `factory_os_quality` 安装并激活，`true → false` 在 v0.1 不支持（addon/profile downgrade 不支持，与 ADR-006 §D 卸载/降级一致）。Inspection 子能力保持可配置：`incoming_inspection_enabled` / `process_inspection_enabled` / `final_inspection_enabled` / `incoming_qc_gate` / `final_qc_gate`，且：

```text
process_inspection_enabled = true
    requires mrp_production_enabled = true
```

这保留轻量 Final-only / Incoming QC 工厂而不强制 MRP。

### 6. DELIVERY CLASSIFICATION（不变，ADR-006 §E 保留）

`delivery_enabled` = Workflow/Business capability，requires `inventory_enabled`，可 `ON ↔ OFF`。Base truth = `stock.picking`。Odoo `delivery` carrier addon 不属于本 capability contract。

### 7. PHASE OWNERSHIP — FINAL（更正全部误导引用）

- **Phase 1 — Core & Security**：仅 `factory_os_core`、security foundation、roles/groups、configuration infrastructure、profile installer/detector foundation、monotonic engine checks、audit foundation、initial setup wizard foundation。**NO** Supply 业务实现；**NO** MRP 业务实现；**NO** MTO product 业务实现。
- **Phase 2 — Simple Orders**：实现 `factory_os_orders`（Customer/Product 基础订单流、Committed/Requested Date、Manual Execution/Progress、Basic Health、Attachments）。无 stock/MRP/QC 依赖。
- **Phase 3 — Inventory & Purchasing**：实现 `factory_os_supply`，**无 MRP**。范围 = Inventory engine、Warehouse、Location、Quant、PO、Receipt、Incoming、Available、Reserved、Lot/Serial、Reorder、Scrap、Inventory count、Purchasing→Inventory dependency、security。Phase 3 退出条件**不得要求** `mrp.bom` / `mrp.production` / BOM explosion / BOM-driven raw-material demand / MTO / Manufacture route。
- **Phase 4 — Formal MRP + BOM-driven Supply**：实现 `factory_os_production`。BOM、BOM Explosion、Manufacturing Demand、Available、Reserved、Incoming、Shortage、MO、Work Order、MTO、Component consumption、Finished quantity、Finished Lot。Material Shortage 保持 **DERIVED**（来自原生 Odoo truth）；**无** `factory.material.requirement` 事务账本。

### 8. PROFILE DEPENDENCY-CLOSURE TEST — PERMANENT（永久架构验证）

规范化算法（future audit tooling 契约；本轮只写合同，不实现）：

```python
def verify_profile_closure(profile_contract, installed_modules):
    forbidden = (
        set(installed_modules)
        & set(profile_contract["forbidden_engines"])
    )
    assert not forbidden, (
        f"Profile {profile_contract['name']} leaked "
        f"forbidden engines: {sorted(forbidden)}"
    )
```

规范化契约：

```python
PROFILE_CONTRACTS = {
    "P0": {
        "required_engines": {"sale"},
        "forbidden_engines": {
            "stock", "mrp", "sale_stock", "sale_mrp",
            "purchase", "purchase_stock", "purchase_mrp",
        },
    },
    "P1": {
        "required_engines": {
            "sale", "stock", "purchase",
            "sale_stock", "purchase_stock",
        },
        "forbidden_engines": {
            "mrp", "sale_mrp", "purchase_mrp",
        },
    },
    "P2": {
        "required_engines": {
            "sale", "stock", "purchase", "mrp",
            "sale_stock", "purchase_stock",
            "sale_mrp", "purchase_mrp",
        },
        "forbidden_engines": set(),
    },
}
```

- 对每个 Technical Installation Profile：`direct deps + transitive deps + auto_install bridges` 不得包含该 profile forbidden 的业务引擎。
- IDE 只能适配"Odoo 自动安装的非业务引擎会计/支持模块"（如 `account`/`stock_account` 等，P1/P2 自动面本已含）；**不得**因"Odoo 会自动装"而删除 forbidden 业务引擎条目。
- 若某个精确原生依赖使上述契约不可能：**STOP 并报告证据**。

### 9. DASHBOARD OPTIONAL-INTEGRATION RULE

Dashboard 可从 P0 存在但不能依赖更高模块。Base code 不得在 registry-load 时静态引用可选模型字段/类。允许模式（未来实现契约）：

```python
def _model_available(self, model_name):
    return model_name in self.env.registry
```

配合 `if self._model_available("stock.picking") / ("mrp.production") / ("factory.quality.inspection")`。不建 fake dashboard cache/source-of-truth 表。

### 10. OPTIONAL-MODULE INTEGRATION RULE

Quality / Delivery / Dashboard / Connector 通用：addon 仅当 `model exists in registry` **且** 对应 Factory OS capability active 时，才消费更高/可选模型。概念化未来 helper 契约（实现期 Phase 1+，本轮**不实现**）：

```python
def factory_capability_available(env, *, flag, model=None):
    company = env.company

    if not getattr(company, flag):
        return False

    if model and model not in env.registry:
        return False

    return True
```

## Alternatives Considered（裁决后定稿）

- **新增第 9 个 Factory OS bridge addon**：ADR-006 §B 已否决；§3 目标闭包证明 8-addon 可实现 → 不引入。
- **supply 保留 `mrp`、Profile 1/2 合并为一级**：违背 ADR-006（Profile 2 才装 MRP）与 Test G/H 渐进实证 → 拒绝。
- **supply 去掉 `purchase`、purchasing 扩展用 registry 守卫**：把 Purchasing+Inventory 拆出 supply、且 purchase.order 扩展需运行时守卫，违背开发计划 §8「不要拆成两个 addon」与用户 §3.3 目标 → 记录备选，不采纳。
- **quality 依赖 supply / production（经 supply 间接 mrp）**：使所有 Quality 工厂强制 MRP → 拒绝；用户 §3.5 最终契约 quality = core+orders+stock、process 经 registry 守卫。
- **delivery 依赖 production/quality**：基础发货强制 MRP/QC → 拒绝；用户 §3.6 最终契约 delivery = core+orders+stock、真相 stock.picking、条件集成。
- **dashboard 依赖全部内部 addon**：Dashboard 变"装一切"木马 → 拒绝；用户 §3.7/§9 registry 守卫。
- **Purchasing 维持 engine-backed monotonic**：与"Profile 1 Inventory-only 物理含 purchase substrate"自相矛盾，复造假关闭 → 本 ADR 修订为 Workflow/Business（§4）。
- **Quality 维持"requires Formal MRP"**：Quality 不是 MRP 必经层 → 本 ADR 修订为 Factory-addon-backed monotonic、requires inventory、不 requires mrp（§5）。
- **运行时"假依赖"（manifest 不声明但代码 import）**：Odoo 加载即崩 → 拒绝。

## Consequences

- **Supersedes 范围**：修订/取代 ADR-006 中以下必要部分——§A 能力分类（purchasing engine-backed → workflow；quality 补 factory-addon-backed/不要求 MRP 澄清）、§D Profile 1 措辞（purchase substrate 常驻、显式 sale_stock/purchase_stock）与 Profile 3 表述（quality 可作 P1 上独立扩展）；其余 ADR-006 决策（inventory/mrp 引擎型单调、8-addon、Profile 0–2、delivery 业务层、Business Preset≠Technical Profile、无卸载/降级）**维持不变**。不引入正常态引擎卸载/降级；仅到"使 manifest 闭包与 profile 契约一致"的必要程度。
- **权威更新（本 Accepted 提交内）**：ADR-006（Follow-up 状态）、docs/decisions/README.md、progressive-adoption.md、configuration-schema.md、configuration-dependency-graph.md、addon-dependency-map.md（§2 转正/§5/§6 闭包矩阵 + PROFILE_CONTRACTS）、开发计划（§3 addon 架构图 / §8 supply deps 去 mrp / quality 依赖段 / §23 delivery deps 收敛 / §28 dashboard deps 收敛 / §41 Phase 1 attribution / §43 Phase 3 Gate / §44 Phase 4 Gate / §5 orders 依赖确认）、native-behavior-audit.md、technical-risks.md（Gate/R11 转正）、governance-audit.md（v1.0.4 re-audit + 永久 closure 检查项）。
- **能力语义落点**：`purchasing_enabled` 的 schema/dependency-graph 行从 engine-backed monotonic 改为 Workflow/Business（requires inventory、ON↔OFF、open-transaction guards、不宣称 addon 存在）；`quality_enabled` 标注 factory-addon-backed monotonic、requires inventory、NOT requires mrp；`process_inspection_enabled requires mrp_production_enabled` 保留。
- **UI 不改**；22 个 MVP surface 不扩；System Invariants 仅在发现真实矛盾时修改（本轮无矛盾）。
- Profile 闭包检查成为**永久 audit item**：任何 addon manifest 依赖变更（direct/transitive/auto_install bridges）必须满足所属 profile 的 forbidden 集约束，否则该变更被 BLOCK。

## Invariants / Authorities Affected

- 引用（不变）：ADR-001/002/003/004/005、system-invariants #8/#14、progressive-adoption、configuration-schema、configuration-dependency-graph、addon-dependency-map、开发计划 §0.1/§3/§5/§8/§13/§19-§20/§23/§28/§41-§44。
- 已更新（本 Accepted 提交内）：如上 Consequences 权威清单。
- 未修改：System Invariants（无真实矛盾）；UI 设计文档；configuration-matrix.md（产品可读矩阵不含 capability flag/依赖语义）；Business preset 表（Quick Start 不变）。

## Verification

- 永久闭包契约（§8）：Profile 0/1/2 → `verify_profile_closure(PROFILE_CONTRACTS[p], installed_modules)`；Phase 1 profile installer 验收与 governance-audit 永久检查项共用同一契约。
- 文档/权威 grep（本轮执行）：`factory_os_supply` dependency 无 `mrp`；`factory_os_delivery` 无 production/quality/native `delivery`；`factory_os_dashboard` 无 supply/production/quality/delivery；`factory_os_quality` 无 `mrp`；`factory_os_orders` 无 `stock`/`sale_stock`；`purchasing_enabled` 非 engine-backed（schema/graph 行已改 workflow）；`purchasing_enabled requires inventory`；`quality_enabled` 不 requires mrp；`process_inspection_enabled` 确实 requires mrp；Phase 1 无 Supply 实现；Phase 3 无 BOM/MRP 退出条件；Phase 4 拥有 BOM-driven shortage。
- `git diff --check`；相对链接/引用验证；full Governance Audit（governance-audit v1.0.4，含新永久 closure 检查项）。
- A–H harness（scripts/audit/phase0）在 Odoo 升级后重跑；E/F/H3 断言 MTO 只在含 mrp 的 profile 触发。

## Supersedes / Superseded By

- **Supersedes**：ADR-006 中与上述 §Decision 冲突的依赖/profile/capability-classification 部分（§A purchasing/quality 分类、§D Profile 1/3 措辞），按"Consequences · Supersedes 范围"执行；不整体取代 ADR-006。
- Superseded By：None。
