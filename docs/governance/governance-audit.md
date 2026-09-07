# Factory OS Governance Consistency Audit

Date: 2026-09-07（v1.0.2 re-audit）
Scope: governance documentation + authority consistency; 本审计覆盖 ADR-006 从 Proposed → Accepted 及其对相关权威文档的同步影响。No business code added, no product semantics changed beyond the authorized ADR-006 decision.

## Audit type & staleness trigger

ADR-006（capability/addon 安装）由 **Proposed → Accepted** 且同步修订 progressive-adoption / configuration-schema / configuration-dependency-graph / 开发计划 / addon-dependency-map —— 属 **ARCHITECTURAL 治理语义变更**，按 [change-control.md §4.4](change-control.md#44-audit-staleness-rule审计过期规则)，Gate 置 **STALE**。本文件即 STALE 状态下重新执行的完整 consistency audit（v1.0.2）。

### Gate 状态机

```text
COMPLETE →（GOVERNED / ARCHITECTURAL 治理语义修改）→ STALE →（本 full re-audit）→ COMPLETE
COMPLETE →（STANDARD 治理修复：typo / link-only）→ targeted check，Gate 不失效
```

禁止出现"审计全 PASS 但被审权威随后已变化"的状态。

## Delta（v1.0.1 → v1.0.2）

- `docs/decisions/ADR-006`：Proposed → **Accepted**（Option 1 + amendments，用户 2026-09-07 裁决）：
  1. Engine-backed capabilities（inventory / formal MRP / 进入 profile 的 purchasing / quality）**单调**——`OFF→ON` 支持，v0.1 无正常 `ON→OFF`、无原生引擎卸载/降级；禁止"引擎在而 flag 关"假关闭状态。Workflow/UI 子能力（operations / mobile / inspection / QC gates / reports / notifications）仍可 `ON↔OFF`。
  2. **保持 8-addon**：否决 `factory_os_orders_stock`；`factory_os_orders` 依赖 → `factory_os_core + sale`（去 `sale_stock`）；库存视角归 `factory_os_supply`（扩展 sale.order）、发货/追溯归 `factory_os_delivery`（扩展 stock.picking）。
  3. **v0.1 `purchasing_enabled requires inventory_enabled`**（无 Purchase-only；Deferred/Post-MVP）。
  4. Technical Installation Profiles 0–3 冻结；Business Preset ≠ Technical Installation Profile；delivery 为业务层能力（操作 stock.picking，**不绑定 Odoo delivery addon**，carrier optional）。
- Authority 同步：`progressive-adoption.md` v1.1（L10 绝对规则按 ADR-006 Supersedes 失效；新增 Technical Installation Profiles 节）；`configuration-schema.md`（capability 分类段 + 引擎 flag 行单调/依赖）；`configuration-dependency-graph.md`（Graph 节点 + machine rule table：monotonic BLOCK disable / purchasing→inventory / delivery no-binding）；开发计划 v0.1（§0.1 基线、§5 orders 依赖 core+sale、§9 purchasing→inventory、§23 delivery 注释）；`addon-dependency-map.md`（§2 orders 行、§4 含义、§5 manifest 约束 8-addon）。
- Gate 文档：`native-behavior-audit.md` §0 与 `technical-risks.md` Gate Status 由 BLOCKED → **PASS（awaiting user authorization for Phase 1）**；R1 标记已裁决（残留执行风险转 Phase 1）、R10 标记 MRP Profile 受控。
- System Invariants / UI 设计 / configuration-matrix / 22-MVP 工作面：**未修改**（无真实不变量冲突）。

## Consistency results（v1.0.2，18 项）

| # | Check | Result | Evidence |
|---|---|---|---|
| 1 | ADR-006 = Accepted，且 Supersedes 范围受限（不引入卸载/降级） | PASS | `ADR-006` Status: Accepted；Supersedes 节明示"仅允许上架/升级期受控单调引擎安装，不引入正常态原生引擎卸载/降级"；README 索引同步 Accepted。 |
| 2 | 引擎型 capability 单调表述全库一致 | PASS | configuration-schema「capability 分类」段 + dependency-graph（3 处 engine-backed monotonic）+ progressive-adoption（单调规则）+ ADR-006 §A 一致：OFF→ON 支持、ON→OFF v0.1 不支持；grep `不动态安装或卸载` 于 docs/ 与开发计划**零命中**（旧绝对规则已清除）。 |
| 3 | 禁止"假关闭"状态（config false / engine true）被明确排除 | PASS | ADR-006 §A、schema 分类段、dependency-graph inventory/mrp/purchasing/quality 节点 incompatible_with = engine-installed-but-flag-off；progressive-adoption「不假装抑制已安装引擎」。 |
| 4 | 保持 8-addon；`factory_os_orders_stock` 被否决而非新增 | PASS | ADR-006 §B + addon-dependency-map §5.1；grep `factory_os_orders_stock` 仅出现在"否决/不新增"上下文（ADR-006、addon-map 约束）。 |
| 5 | `factory_os_orders` 不依赖 `sale_stock`（manifest 声明处） | PASS | 开发计划 §5 Odoo dependencies 实测块 = `factory_os_core + sale`（grep 输出）；addon-dependency-map §2 行同步；无残留 manifest 级 orders→sale_stock 声明。 |
| 6 | Purchasing requires Inventory（v0.1 显式） | PASS | ADR-006 §C、schema `purchasing_enabled` 行、dependency-graph purchasing 节点（ENABLE_REQUIRED inventory）、progressive-adoption Profile 约束、开发计划 §9 注释五处一致。 |
| 7 | 无 Purchase-only 模式语义残留 | PASS | grep `Purchase-only` 全部为显式"无/不支持/Deferred/否决"语境（schema/dev-plan/ADR/addon-map/dependency-graph/technical-risks）；无"支持纯采购运行模式"表述。 |
| 8 | Safe Minimal ↔ 无 stock 安装 profile（Profile 0） | PASS | progressive-adoption Technical Profiles 表 Profile 0 = `sale`（core+orders，无库存/MRP/QC/delivery 事务，Test G 为契约证据）；开发计划 §5 orders 依赖注释同证。 |
| 9 | MRP profile 单调；MTO 受控归 Profile 2 | PASS | schema/dependency-graph `mrp_production_enabled` engine-backed monotonic；MTO 语义注释（E/H3：SO 确认自动 MO 属受控能力、非 flag 可关）；native-behavior-audit §9 边界一致。 |
| 10 | Delivery 不绑定 Odoo `delivery` addon | PASS | schema `delivery_enabled` 行"不绑定 Odoo `delivery` addon（carrier optional, Post-MVP）"、dependency-graph delivery 节点 "does NOT require/install Odoo delivery addon"、开发计划 §23 注释一致。 |
| 11 | Business Preset ≠ Technical Installation Profile | PASS | progressive-adoption「Technical Installation Profiles」节 + preset 节翻译链（Preset → Profile → Atomic Config → Role）；未向用户暴露 addon 术语；无 `management_level`/`maturity_level` 引入（preset 只写原子配置）。 |
| 12 | 权威同步清单与 ADR-006 Consequences 相符 | PASS | ADR-006 Consequences 所列 7 处更新（progressive-adoption/configuration-schema/configuration-dependency-graph/开发计划/addon-dependency-map/native-behavior-audit/technical-risks）本 commit 全部落地（git status 核对）；README 索引已更新。 |
| 13 | System Invariants / UI / configuration-matrix / 22-MVP 未改 | PASS | git status 不含 system-invariants、UI/*、configuration-matrix；governance-model 域与 PRD 未触碰（v1.0.1 check 9/10 回归未破坏）。 |
| 14 | 无业务代码修改 | PASS | 本次变更仅 docs/decisions、docs/factory_os、docs/governance/governance-audit.md、根开发计划文档；无 odoo-19/ 或新业务模块代码（scripts/audit/phase0 为只读审计工具，上一 commit 已收编，本次未改）。 |
| 15 | 治理文档层级未被突破（Proposed→Accepted 由用户授权） | PASS | change-control §4.3 ARCHITECTURAL 流程：用户明示 "Accept with amendments" 并授权修订/标记 Accepted/更新权威/重跑审计；ADR-006 记录 Owner=用户 Gate 裁决。 |
| 16 | Phase 0 Gate 状态一致（PASS awaiting Phase 1 authorization） | PASS | native-behavior-audit §0 与 technical-risks Gate Status 均标 PASS + awaiting user authorization for Phase 1；闭环节点 5 条件（ADR Accepted/authority 一致/Test E–H 未变/8-addon 映射/purchasing→inventory/无引擎降级承诺）逐条列入。 |
| 17 | 所有链接可解析 | PASS | 脚本校验 docs/ 递归相对链接全部指向存在的文件（含 ADR-006 新链接与 progressive-adoption → ADR-006）。 |
| 18 | `git diff --check` 通过 | PASS | 无空白错误（audit 文件写入后 commit 前复检）。 |

## Reported contradictions（resolution 更新）

1. **治理级（v1.0.0 已解决）**：reading order（governance README §3）与 precedence（governance-model §1）分离；不变量置顶。未回归。
2. **产品-技术映射级（v1.0.1 已解决，ADR-002 澄清）**：平行库存被不变量 #3 + ADR-002 排除，Phase 0 冻结具体 mapping。未回归。
3. **能力/引擎架构级（本版解决，ADR-006）**：progressive-adoption（v1.0）L10 绝对规则"capability flags 不动态安装或卸载 Odoo addons"与 Safe Minimal "无库存事务"承诺的互斥——经 STOP A/B 实证、三选项分析，**Accepted ADR-006** 把能力层级映射为 Technical Installation Profile（单调安装、不卸载/降级、无假关闭），旧 L10 仅在被 Supersedes 限定的范围内失效；订单看板"无库存事务"承诺仅在 Profile 0（不装引擎）成立，且 Test G 证明其真实可存在。

## Gate decision

**Governance Gate: COMPLETE（v1.0.2 re-audit 全 PASS，18/18）。**

- v1.0.1 COMPLETE →（ARCHITECTURAL：ADR-006 Proposed→Accepted + authority 同步）→ STALE →（本 full re-audit）→ **COMPLETE**。
- **Phase 0 Gate: PASS（evidence complete）— awaiting user authorization for Phase 1**；ADR-006 裁决产生的 Phase 1 执行项（profile 安装/单调校验、orders 去 sale_stock、supply 库存扩展、MTO profile 校验）不自动启动。
- 不授权任何业务实现；不改变 22-surface MVP scope；System Invariants 与 UI 权威未改。
