# ADR-006 Capability Engine vs Native Addon Installation

Status: **Proposed**（NOT Accepted — 待用户裁决；裁决前不修改 progressive-adoption / configuration-schema / 开发计划）
Date: 2026-09-07
Owner: 用户 Gate 裁决（Phase 0 STOP resolution）

## Context

Phase 0 出口评审发现两条 Hard STOP（出口状态已改 **BLOCKED**，见 native-behavior-audit §0）：

1. **STOP A — capability flag 不能抑制已安装原生 addon 的行为。** `progressive-adoption.md` L10 规定 "capability flags 控制 Factory OS 菜单、UI 和流程，不动态安装或卸载 Odoo addons"，同时 L8/L92 承诺 Safe Minimal 订单看板模式在无库存/MO/QC 事务下运行。实测证明二者在"引擎已装 + flag 关"组合下互斥：只要 `stock`/`sale_stock` 已安装，即使概念上 `inventory_enabled=false`，Goods SO/PO 确认仍创建 `stock.picking`/`stock.move`（测试 A/B）；不存在"flag 关掉即回到无库存事务"的状态。
2. **STOP B — MTO 原生行为此前未测。** 原 Test C 使用 Manufacture 但 MTO（Replenish on Order）未激活（`is_mto=False`），曾得出过宽结论。补测 E/F/H3 证明：MTO 激活后 SO 确认**立即自动创建 MO**（Manufacture+BoM）或 **draft RFQ**（Buy+供应商），且该行为**不可被 capability flag 抑制**。

### 实测证据（E–H 运行时复现，详见 native-behavior-audit §8；配方对齐官方 `sale_mrp/tests/test_sale_mrp_procurement.py`）

| 测试 | 结论 |
|---|---|
| E TRUE MTO+Manufacture | `mo 0→1`：SO 确认即 WH/MO（confirmed, origin=SO）；`action_view_mrp_production()['res_id']==mo.id` |
| F TRUE MTO+Buy | `po/rfq 0→1`：SO 确认即 draft RFQ（origin=SO）；并预留 waiting 发货单 |
| G REAL Safe Minimal | 仅 `-i sale` → 54 模块；stock/purchase/mrp 引擎与全部桥接**不存在**；Goods SO 确认零物流对象 → **Safe Minimal 是真实可存在的安装 profile** |
| H 同库渐进安装 | 54→61(+stock/sale_stock/stock_account)→64(+mrp/sale_mrp/mrp_account)；旧单（含旧产品）每次加装后**零回溯**；新单即入新引擎；MTO 产品 SO 确认自动产 MO |

### manifest 结构性事实

- `factory_os_orders` 计划依赖 = `factory_os_core + sale + sale_stock`（开发计划 L315-321；addon-dependency-map §2）——**Safe Minimal 若真实不装 stock，该依赖不能原样保留**。
- 原生侧：`sale` 仅依赖 sales_team/account_payment/utm（**不依赖 stock**）；`sale_stock`/`stock_account`/`purchase_stock`/`sale_mrp`/`purchase_mrp` 均为 `auto_install=True` 桥接——Odoo 自己就是用"依赖双方都装齐则自动挂桥"表达渐进安装。
- `purchase` 在 19 **不依赖 stock**（depends=['account']），纯采购（收票/应付款）可在无库存引擎下运行；库存联动由 `purchase_stock` 桥接提供。

## Decision（Proposed）

**推荐 OPTION 1 — Installed-addon profiles / monotonic capability upgrades**（证据指向，见 Alternatives；**未采纳**，等待裁决）。

- **UI/business capability 与 native engine capability 分离定义**：Factory OS capability flag 继续只控制 Factory OS 菜单/UI/流程/字段；但"某个能力可用"的**前置条件 = 对应原生引擎 addon 已安装**。二者由初始化向导一次性对齐，运行时不再互相假装。
- **原生 addon 安装 profile**：能力等级 ↔ 安装 profile 绑定——Safe Minimal 真实不装 `stock`/`purchase`/`mrp`（G 实证）；Inventory 级 = `+stock(+sale_stock 桥)`；正式生产级 = `+mrp(+sale_mrp 桥)`；Quality 级 = `+factory 薄 QC`（无原生 quality 可装）。profile 由初始化向导按渐进顺序建立。
- **单调升级（monotonic）**：升级 = 安装更多引擎 addon（及触发对应 auto_install 桥接）；装引擎时同步把对应 flag 置 true。**引擎级卸载/降级 v0.1 不支持**（Odoo 对存在数据引用的模块拒绝卸载；不承诺破坏性卸载）。降级路径 = 新建库重放（与 ADR-001 一厂一库一致），不属常规运维。
- **引擎已装后的 capability-off 语义**：profile 单调性使"引擎已装而 flag 关"仅可能来自手工越权翻转 → 语义 = 只隐藏/禁用 Factory OS UI 与流程，**不宣称卸载或抑制原生引擎**；wizard/治理审计报不一致并阻止继续（Phase 1 实现机制；不变量 #8——菜单隐藏不等于安全——在"模型仍存在"的高 profile 库由 factory_os 服务层校验落实）。
- **历史单据行为**：任何加装/升级不改写旧订单、不伪造历史（H 实证），继续满足 ADR-004 与不变量 #14。
- **MTO 管理**：MTO route 只在含 `mrp`（或对应采购）的 profile 库允许分配；产品建模/导入向导校验 MTO 与当前 profile 一致（R10）。

## Alternatives Considered（并列呈现，未静默选型）

### OPTION 1 — Installed-addon profiles / monotonic upgrades（推荐方向）
- progressive-adoption：L10 语义修订为"flags 不动态装卸 addon；能力可用性以安装 profile 为前提"；Safe Minimal/L92 承诺与实测一致（无引擎 → 无原生事务）。
- configuration-schema：flags 增加"所需原生引擎/桥接"元数据；wizard 写 profile→flags 映射。
- 依赖图/manifest：见下 §Manifest 影响；addon-dependency-map §5 同步。
- 初始化向导：按 profile 安装原生引擎（含 auto_install 桥接预测）再装对应 factory addon。
- 升级/cutover：单调、显式（安装动作本身是审计事件）；旧单不回溯。
- 回滚/关闭语义：无引擎卸载承诺；flag-off 仅 UI/流程；不一致由审计报警。
- 代价：安装动作与"启用能力"耦合（初次安装时间长、需原生模块权限）；需要新增桥接 addon 或调整依赖（§Manifest）；历史上"随手开个菜单试试"的体验不再可用。

### OPTION 2 — 所有原生 addon 始终安装（保持"flags 不影响安装"原句）
- Safe Minimal：退化为"全引擎已装但 Factory OS 界面只露出订单"——**物理上仍是库存/MRP 库**（原生菜单/模型全在）。
- "无库存/MO/QC 事务"承诺：无法兑现——A/B 证明任何 Goods SO/PO 确认都产生 picking/move；MTO 产品确认即 MO/RFQ；只能靠"不给产品配 route/is_storable"维持表面，任何用户在原生侧的操作或未来自动补货都会产生原生事务。
- progressive adoption：变成纯 UI 隐藏，旧单虽不伪造但"渐进"无实质（第一天已拥有全部引擎与权限面）。
- 库存真相：仍是 stock.* 唯一，但"订单看板库"实际存在库存后台对象与全公司 record rule 可见性 → 不变量 #8 默认安全要求更难满足（security-baseline：库存/生产默认仅 multi-company 规则）。
- 结论：与 L8/L92、preset 语义直接矛盾；若采纳需接受订单看板用户面对的库是完整 ERP 引擎库（本 ADR 不建议）。

### OPTION 3 — Factory OS 拦截抑制原生副作用（flags OFF 时）
- 需拦截：`sale.order.line._action_launch_stock_rule`、PO 确认的规则触发、`mrp`/MTO 规则、orderpoint/cron 补货、picking validate、原生菜单/RPC/import 建单路径等。
- 升级脆弱性：Odoo minor 升级改方法即破（本 Phase 已踩 5 处 17/18→19 API 差异；拦截面会放大该风险）。
- bypass 风险：RPC、数据导入、原生菜单、第三方模块直接 create 均可绕过 hook → 承诺仍然不成立，且比 OPTION 2 更危险（"看起来关了其实没关"）。
- 与不变量冲突：ADR-002/003 精神是只读/derived 层不做第二事实、服务层自身校验——全局业务钩子属新一类"平行语义"。
- 维护成本：每 Odoo 升级重审拦截点；测试面大。
- 结论：可作为个别 Gate 的服务层校验（如 orders 层拒绝 MTO 行），**不作为**全局引擎抑制架构。

## Manifest 影响（factory_os_orders 与采购边界——裁决时一并定）

1. `factory_os_orders` 现依赖 `sale_stock` → 在 OPTION 1 下 Safe Minimal（无 stock）不可满足。候选拆法（Odoo auto_install 惯例，与 sale_stock 同构）：
   - a) 新增 `factory_os_orders_stock` 桥接（depends `factory_os_orders + sale_stock`, auto_install=True）：orders 本体只依赖 `factory_os_core + sale`；装 stock 后桥接自动挂载，提供发货/库存联动 UI。
   - b) 或 orders 本体同时提供两种 UI 且以运行时探测 stock 模型切换（不新增 addon，但把 engine-conditional 逻辑放进核心 addon，较不干净）。
   - → 建议 a，需用户确认允许新增第 9 个 factory addon（本 ADR 一并裁决）。
2. **purchase without inventory** 三选一（架构选择，非 Phase 0 细节；建议 ①）：
   - ① v0.1 要求 purchasing → inventory（缺料/来料检验/收货以 stock 为底，与 factory_os_supply 一致；纯采购收票属 Accounting guardrail 范围外，MVP 不涉）；
   - ② 支持 purchase-only 干净模块边界（独立 `factory_os_purchasing`，只依赖 purchase，19 中 purchase 本身不依赖 stock）——若订单看板用户只想下单采购而不建库存；
   - ③ 引入内部 bridge（supply 拆 core+stock 桥，同 1a 模式）。
   - → 本 ADR 只呈现后果：② 在 v0.1 意味着"采购单-收货-质检-追溯"链路不完整（R2/R4 均假设库存存在）；③ 增加 addon 数量。
3. `factory_os_production`/`supply`/`quality`/`delivery` 仅在对应引擎 profile 下安装（depends 链已隐含 stock/purchase/mrp）；不动态改 manifest。

## Consequences

- Phase 0 Gate 状态维持 **BLOCKED — awaiting ADR-006 decision**；未裁决前不更新 progressive-adoption / configuration-schema / 开发计划 / 任何业务代码。
- 若采纳 OPTION 1：progressive-adoption L10 语义修订、configuration-schema 增加 profile→flags/引擎绑定、开发计划 §3 addon 清单与 §0.1 L22 表述更新、addon-dependency-map §5 约束更新——均在 Accepted 后作为一次显式治理变更执行（governance-audit 将标 STALE）。
- 一厂一库（ADR-001）下，"厂的能力等级" = "该厂库的安装 profile"，两者永久一致，避免"配置说一套、引擎做另一套"。

## Invariants / Authorities Affected

- 引用：ADR-001（一厂一库）、ADR-002（stock.* 唯一真相）、ADR-003（简单执行 vs 正式 MRP）、ADR-004（渐进不伪造历史）、system-invariants #8（默认安全，菜单隐藏≠安全）、#14（不伪造历史）、progressive-adoption L8/L10/L92-99、configuration-schema flags、开发计划 §0.1/§3。
- Accepted 后将修订：progressive-adoption L10 与 Safe Minimal/preset 措辞；configuration-schema capability flags 语义（绑定引擎前置条件）；开发计划 §3 8-addon 清单与依赖；addon-dependency-map §5。

## Verification

- 验收证据：Test E/F/G/H 运行时输出（native-behavior-audit §8）；Odoo 升级后由 `scripts/audit/phase0/` harness 重跑（A–H）检测原生行为漂移。
- Phase 1 验收：初始化向导按 profile 建库后，低 profile 库原生引擎模型不存在（G 断言）；高 profile 库 MTO 行为与官方一致（E/F/H3 断言）；旧单零回溯（H 断言）。
- governance-audit：ADR-006 从 Proposed → Accepted 后触发相关权威文档 STALE → 更新 → re-audit。

## Supersedes / Superseded By

- **未采纳前不 Supersede 任何文档**（Proposed 状态）。此前 Phase 0 输出（r2）对 capability flag 的"安装方案与能力分层绑定"表述（technical-risks R1 旧版）在 STOP resolution 中已撤回为待裁决项。
- Accepted 后：Supersedes progressive-adoption L10 之"capability flags 完全不涉及 addon 安装"的既有解释（以本 ADR 语义为准）。
- Superseded By：None（若用户选择 OPTION 2/3，本 ADR 将改写 Decision 段落并重新 Proposed）。
