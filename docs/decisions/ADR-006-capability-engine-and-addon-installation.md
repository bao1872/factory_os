# ADR-006 Capability Engine vs Native Addon Installation

Status: **Accepted**
Date: 2026-09-07（Proposed → Accepted，用户裁决 Accept with amendments）
Owner: 用户 Gate 裁决（Phase 0 STOP resolution）
Follow-up（2026-09-07，dependency-closure STOP）：本决策的安装 profile 与 8-addon manifest 依赖闭包存在冲突（`factory_os_supply`→`mrp` 使 Profile 1 强制装 MRP；delivery/dashboard 计划依赖偏高；purchasing 单调分类与 supply→purchase 的 Inventory-only substrate 冲突）。修订提议见 **ADR-007（Status: Proposed，未采纳）**；裁决前本决策仍为有效权威，affected evidence docs 仅加 BLOCKED 标记。

## Context

Phase 0 出口评审发现两条 Hard STOP（出口状态 BLOCKED，见 native-behavior-audit §0）：

1. **STOP A — capability flag 不能抑制已安装原生 addon 的行为。** `progressive-adoption.md`（v1.0）L10 规定 "capability flags 控制 Factory OS 菜单、UI 和流程，不动态安装或卸载 Odoo addons"，同时 L8/L92 承诺 Safe Minimal 订单看板模式在无库存/MO/QC 事务下运行。实测证明二者在"引擎已装 + flag 关"组合下互斥：只要 `stock`/`sale_stock` 已安装，即使概念上 `inventory_enabled=false`，Goods SO/PO 确认仍创建 `stock.picking`/`stock.move`（测试 A/B）；不存在"flag 关掉即回到无库存事务"的状态。
2. **STOP B — MTO 原生行为此前未测。** 原 Test C 使用 Manufacture 但 MTO（Replenish on Order）未激活（`is_mto=False`），曾得出过宽结论。补测 E/F/H3 证明：MTO 激活后 SO 确认**立即自动创建 MO**（Manufacture+BoM）或 **draft RFQ**（Buy+供应商），且该行为**不可被 capability flag 抑制**。

### 实测证据（E–H 运行时复现，详见 native-behavior-audit §8；配方对齐官方 `sale_mrp/tests/test_sale_mrp_procurement.py`）

| 测试 | 结论 |
|---|---|
| E TRUE MTO+Manufacture | `mo 0→1`：SO 确认即 WH/MO（confirmed, origin=SO）；`action_view_mrp_production()['res_id']==mo.id` |
| F TRUE MTO+Buy | `po/rfq 0→1`：SO 确认即 draft RFQ（origin=SO）；并预留 waiting 发货单 |
| G REAL Safe Minimal | 仅 `-i sale` → 54 模块；stock/purchase/mrp 引擎与全部桥接**不存在**；Goods SO 确认零物流对象 → **Safe Minimal 是真实可存在的安装 profile** |
| H 同库渐进安装 | 54→61(+stock/sale_stock/stock_account)→64(+mrp/sale_mrp/mrp_account)；旧单（含旧产品）每次加装后**零回溯**；新单即入新引擎；MTO 产品 SO 确认自动产 MO |

### manifest 结构性事实（Odoo 19 Community，源码级）

- `factory_os_orders` 原计划依赖 = `factory_os_core + sale + sale_stock`（开发计划 §5）——Safe Minimal 若真实不装 stock，该依赖不能保留。
- 原生侧：`sale` 仅依赖 sales_team/account_payment/utm（**不依赖 stock**）；`sale_stock`/`stock_account`/`purchase_stock`/`sale_mrp`/`purchase_mrp` 均为 `auto_install=True` 桥接——Odoo 用"依赖双方齐装则自动挂桥"表达渐进安装。
- `purchase` 在 19 **不依赖 stock**（depends=['account']），纯采购可在无库存引擎下运行（原生现实，非 Factory OS v0.1 支持形态）；库存联动由 `purchase_stock` 桥接提供。

## Decision（Accepted）

**OPTION 1 — Installed-addon profiles with monotonic capability upgrades**，附用户裁决的三项强制修订（§A–C）与语义澄清（§D–F）。

### A. 引擎型 capability 单调（不允许"假关闭"）

配置分两类，**禁止** `config=false 而 engine=true` 的长期自相矛盾状态：

- **Engine-backed capabilities**（其真实行为依赖原生引擎安装）：最低 `inventory`、`formal MRP`（即 `inventory_enabled`、`mrp_production_enabled`）；进入对应 profile 即安装引擎。
  - 转移 `OFF → ON` 支持；
  - `ON → OFF` 在 v0.1 **不支持**（正常路径禁止；BLOCK 语义）。一旦引擎安装且能力激活，该 capability 保持 true；
  - 不宣称任何 Boolean 能抑制已安装的原生引擎。
- **Workflow/UI subordinate capabilities**（`operations`、`mobile_warehouse/operator/quality`、各 inspection 类型、QC gates、`reports`、notifications 等）：仍可正常 `ON ↔ OFF`，只影响 Factory OS UI/流程/字段，不触碰引擎。
- 若原生引擎在 Factory OS 管理之外被安装：Phase 1 一致性检查必须探测现实，阻止 Factory OS 配置宣称矛盾状态（如引擎在而 flag 关）。检测/机制 Phase 1 实现，本任务不实现。
- `purchasing_enabled`、`quality_enabled`：进入其 profile（安装对应引擎/工厂 addon）后同样**单调**（见 §D Profile 1/3）；`delivery_enabled` 属业务层能力（§E），不单调、可 `ON ↔ OFF`。

### B. 保持 8-addon 架构（不新增 `factory_os_orders_stock`）

- **不加第 9 个桥接 addon**；保持既有 8 个 Factory OS 业务 addon。
- `factory_os_orders` 依赖修订为：`factory_os_core + sale`（**去掉 `sale_stock`**）。orders 只拥有基础客户订单执行（执行状态/人工进度/交期/健康度/Chatter）。
- 库存/物料视角属 `factory_os_supply`（依赖 purchase_stock/stock/mrp，扩展 `sale.order` 的缺料/available/incoming/material readiness/order health）。
- 发货/追溯视角属 `factory_os_delivery`（操作 `stock.picking`，扩展 Ready-to-Ship/Shipment/tracking/delivery chain）。
- 遵循 Odoo 自己的渐进模式（sale+stock→sale_stock、sale+mrp→sale_mrp），不需要为此再造一个 Factory OS bridge。

### C. v0.1 Purchasing → Inventory（无 Purchase-only）

- 显式 v0.1 决策：`purchasing_enabled requires inventory_enabled`。Factory OS **不支持** Purchase-only 运行模式。
- 理由：Factory OS 采购是"物料需求→缺料→PO→收货→库存→生产"闭环的一环，不是通用采购/会计应用；Odoo 能装 `purchase` 无 `stock` 仅是原生现实，不作为 Factory OS v0.1 形态暴露。
- Purchase-only 标记 **Deferred / Post-MVP**，除非未来真实工厂需求证明其价值。
- Profile 1 允许 Inventory ON + Purchasing OFF（只管现有库存、不在系统下 PO 的小厂），但反向不允许。

### D. Technical Installation Profiles（冻结）

| Profile | 原生最小安装（+Odoo 自动桥） | Factory OS addon | capability | 原生契约证据 |
|---|---|---|---|---|
| 0 — Order Board / Safe Minimal | `sale` | `factory_os_core` + `factory_os_orders` | Customer/Product/SO/Committed Date/Manual Execution/Health/Chatter；**无 stock/purchase/mrp/QC/delivery 事务** | Test G |
| 1 — Inventory & Purchasing | + `stock`（+ `purchase`，当选中采购）+ 自动桥 `sale_stock`/`purchase_stock`/`stock_account` 等 | + `factory_os_supply` | Inventory=permanently enabled；Purchasing=enabled if selected（requires inventory） | Test A/B/H2 |
| 2 — Formal Manufacturing | + `mrp` + 自动桥 `sale_mrp`/`purchase_mrp`/`mrp_account` | + `factory_os_production` | `mrp_production_enabled`=permanently true；MTO/Manufacture route 开始有真实原生效果，按本 profile 受控 | Test E/H3 |
| 3 — Quality | + `factory_os_quality`（薄模型，非原生 quality） | + `factory_os_quality` | 保持 `factory.quality.inspection`/`factory.quality.ncr`；requires Inventory（FAIL 需受控库存处置） | model-mapping #14/#15 |

- 升级 = **受控、可审计、单调的引擎安装**（对既有 profile 只增不减）。
- **原生引擎卸载/降级 v0.1 不支持**（Odoo 对存在数据引用的模块拒绝卸载；不承诺破坏性卸载）。降级路径 = 新建库重放（ADR-001 一厂一库），非常规运维。
- 引擎安装由初始化向导/升级动作执行（受控），不允许"flag 假装关了引擎还在跑"。

### E. Delivery 语义修正

- **不把 `delivery_enabled` 与安装 Odoo `delivery` addon 一一绑定。** Factory OS Delivery 本质操作 `stock.picking`：Inventory profile 一开，原生 delivery picking 已存在。
- `delivery_enabled` = Factory OS 业务/workflow capability（开 Factory OS Delivery UI/fields/workflow），requires inventory，可 `ON ↔ OFF`。
- Odoo `delivery` addon（Carrier/Shipping Method）为 **optional / Post-MVP**，仅在需要承运商/运费功能时安装（开发计划已有"无 delivery 时以 stock 为最低依赖"）。

### F. Business Preset ≠ Technical Installation Profile

- 用户可见的 Quick Start preset（订单看板 / 订单+进销存 / 标准生产 / 质量追溯）保持为 **Business UX**，不向普通工厂用户暴露 "install stock/mrp addon" 术语。
- 设置流程翻译链：`Business Preset → Installation Profile → Atomic Configuration → Role assignment`。
- 不引入 `management_level`/`maturity_level` 或其他运行时等级（preset 只是向导答案快捷填充，保存后只写原子配置）。

### 历史单据

- 任何加装/升级不改写旧订单、不伪造历史（Test H 实证），继续满足 ADR-004 与不变量 #14。高级 profile 只影响其后新事务。

## Alternatives Considered（裁决前并列，现维持拒绝）

- **OPTION 2 — 所有原生 addon 始终安装**：被否。Safe Minimal 承诺失效（物理上仍为库存/MRP 库，原生菜单/模型全在）；A/B 证明任何 Goods SO/PO 确认都产生 picking/move，"无库存事务"无法兑现；渐进退化为纯 UI 隐藏；与不变量 #8 默认安全冲突。
- **OPTION 3 — Factory OS 拦截抑制原生副作用**：被否。需拦截 `_action_launch_stock_rule`/PO 规则/MTO 规则/orderpoint cron/picking validate/RPC/import/原生菜单等；Odoo minor 升级即破（本 Phase 已踩 5 处 17/18→19 API 差异）；bypass 面大；与 ADR-002/003"只读/derived 层不做业务拦截"精神冲突；维护成本高。
- **第 9 个 bridge addon（`factory_os_orders_stock`）**：Proposed 期曾考虑，用户裁决**否决**——8-addon 已能自然容纳（orders 只管订单执行；supply/delivery 分别扩展库存与发货视角）。
- **Purchase-only 模式**：Proposed 期三方案并呈，用户裁决 v0.1 选 **① Purchasing→Inventory**；②③ 标记 Deferred。

## Consequences

- `progressive-adoption.md`：L10 绝对规则按 §Supersedes 范围修订；新增 Technical Installation Profiles 与 preset/profile 分离表述。
- `configuration-schema.md` / `configuration-dependency-graph.md`：引擎型 flag 标注 engine/profile 关系与单调约束；不新增第二套重复 capability truth 字段。
- 开发计划：`factory_os_orders` 依赖去 `sale_stock`（→ core+sale）；purchasing→inventory；delivery 最低依赖 stock、不绑 delivery addon；8-addon 架构确认。
- `addon-dependency-map.md`：§2/§4/§5 manifest 约束同步。
- native-behavior-audit / technical-risks：Gate 由 BLOCKED 转 PASS（条件满足后）。
- 治理：ARCHITECTURAL 语义变更 → Governance Gate STALE → full re-audit → COMPLETE（governance-audit v1.0.2）。
- 实现期属主（2026-09-07 phase attribution 更正，不改决策本体；与开发计划 §41-§45 Gate 对齐）：**Phase 1** 实现 profile→引擎安装映射与单调校验（引擎在而 flag 关的一致性检测）与 profile installer 基础；**Phase 2** 落实 `factory_os_orders` manifest（core + sale，无 sale_stock）；**Phase 3** 实现 `factory_os_supply` 的 sale.order 库存/采购扩展；**Phase 4** 实现 MRP/BOM/MTO 生产集成与 MTO route 按 profile 校验。依赖闭包边界详见 ADR-007（Proposed）。

## Invariants / Authorities Affected

- 引用：ADR-001（一厂一库）、ADR-002（stock.* 唯一真相）、ADR-003（简单执行 vs 正式 MRP）、ADR-004（渐进不伪造历史）、system-invariants #8（默认安全，菜单隐藏≠安全）、#14（不伪造历史）、progressive-adoption（v1.0 语义修订）、configuration-schema / configuration-dependency-graph、开发计划 §0.1/§5/§9/§13/§23、addon-dependency-map。
- 已更新权威（本 Accepted 提交内）：progressive-adoption.md、configuration-schema.md、configuration-dependency-graph.md、开发计划 v0.1、addon-dependency-map.md、native-behavior-audit.md（§0 Gate 状态）、technical-risks.md（Gate 状态 + R1/R10）、governance-audit.md（v1.0.2）。
- System Invariants：**未修改**（无真实不变量冲突；#8/#14 与决策一致，反而被更严格执行）。UI 设计文档：未修改。
- configuration-matrix.md：产品可读矩阵不含 capability flag/依赖语义 → 不受影响，未修改。

## Verification

- 原生契约证据：Test E/F/G/H 运行时输出（native-behavior-audit §8）；Odoo 19.x 升级后用 `scripts/audit/phase0/` harness 重跑 A–H。
- 验收按实现期属主分相（见 Consequences）：Phase 1 — 初始化向导按 profile 建库（G/H 断言：低 profile 无引擎模型、旧单零回溯）+ monotonic 校验；Phase 2 — orders manifest 无 sale_stock 依赖；Phase 4 — MTO 行为仅 Profile 2 存在（E/H3 断言）与 MTO route 校验。
- 治理验收：governance-audit v1.0.2 全 PASS；grep 无旧 capability/addon 绝对规则残留、无 `factory_os_orders`+`sale_stock`、无 Purchase-only 语义。

## Supersedes / Superseded By

- **Supersedes**：`progressive-adoption.md`（v1.0）"capability flags 不动态安装或卸载 Odoo addons" 的绝对表述——仅限为允许**上架/升级期的受控单调引擎安装**所需的程度；本 ADR **不引入**正常态原生引擎卸载/降级。开发计划 §0.1 L22 与 §5 orders 依赖中与上述冲突的表述同步失效。
- Superseded By：None。
