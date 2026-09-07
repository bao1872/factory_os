# Factory OS Governance Consistency Audit

Date: 2026-09-07（v1.0.3 re-audit）
Scope: governance documentation + authority consistency; 本审计覆盖 Phase 0 dependency-closure STOP——ADR-006 phase attribution 更正（用户授权 §7）、ADR-007 Proposed 登记、affected evidence docs 加 BLOCKED 标记、新增永久 profile↔manifest dependency-closure 检查。No business code added.

## Audit type & staleness trigger

- ADR-006（Accepted ARCHITECTURAL）被编辑：phase attribution 更正（决策本体不变，用户 2026-09-07 dependency-closure 任务 §7 明确授权："clarifies phase attribution, does not change the accepted architecture decision"）——按 [change-control.md §4.4](change-control.md#44-audit-staleness-rule审计过期规则) 触碰 Accepted ARCHITECTURAL 文档 → Gate 置 **STALE**。本文件即 STALE 状态下重新执行的完整 consistency audit（v1.0.3）。
- 新发现架构冲突（用户 STOP）：计划 8-addon manifest 依赖闭包 ≠ ADR-006 Technical Installation Profiles → Phase 0 Gate 由 PASS 回 **BLOCKED**；冲突经 ADR-007（**Proposed**，无权威）+ affected evidence docs BLOCKED 标记**登记并隔离**，未静默改写 authority。
- 审计缺口承认：v1.0.2 的 18 项检查无"profile↔manifest dependency-closure"项 → 放过了 `factory_os_supply→mrp`。本版新增永久检查（见 #19/#20），并对 v1.0.2 状态回溯判定：若该检查当时存在，supply/delivery/dashboard 行将 FAIL → Phase 0 不会以 PASS 收口。

### Gate 状态机

```text
COMPLETE →（GOVERNED / ARCHITECTURAL 治理语义修改）→ STALE →（本 full re-audit）→ COMPLETE
COMPLETE →（STANDARD 治理修复：typo / link-only）→ targeted check，Gate 不失效
```

禁止出现"审计全 PASS 但被审权威随后已变化"的状态。

## Delta（v1.0.2 → v1.0.3）

- **ADR-006**：顶部加 Follow-up 标记（指向 ADR-007 Proposed）；Consequences/Verification 两处 "Phase 1 将实现/验收" 改为**实现期属主分相**（Phase 1 profile installer 基础 / Phase 2 orders manifest / Phase 3 supply 扩展 / Phase 4 MRP·MTO 校验）——phase attribution 更正，决策本体不变。
- **ADR-007（新，Proposed，未采纳）**：8-addon 目标依赖闭包表（supply=core+orders+stock+purchase 无 mrp；delivery=core+orders+stock；dashboard=core+orders+registry 守卫；quality 无 mrp 硬依赖；production=core+orders+supply+mrp）；purchasing_enabled 改 Workflow capability 分类（修订 ADR-006 §A/§D 提议）；Phase 3/4 Gate realignment；Alternatives/Consequences/Verification。
- **Evidence docs（仅 BLOCKED/证据标记，不静默改写计划依赖）**：`addon-dependency-map.md` §0 Gate BLOCKED + §2 三行 CONFLICT + §6 Dependency-Closure Matrix（8 addon × 闭包推演）；`native-behavior-audit.md` §0 与 `technical-risks.md` Gate Status → **BLOCKED**；technical-risks 新增 **R11**（闭包冲突）、R1/R10 阶段属主更正。
- **decisions/README.md**：ADR-007 索引行（Proposed）。
- 未修改（Authority rewrite 待 ADR-007 Accepted 后执行）：progressive-adoption / configuration-schema / configuration-dependency-graph / 开发计划 / configuration-matrix / System Invariants / UI 设计。

## Consistency results（v1.0.3，20 项）

| # | Check | Result | Evidence |
|---|---|---|---|
| 1 | ADR-006 = Accepted 状态与 Supersedes 范围未因 follow-up 变更 | PASS | Status: Accepted 不变；Follow-up 标记明示 ADR-007 Proposed 裁决前本决策仍为有效权威；Supersedes 节（受控单调安装、不引入卸载/降级）原样保留。 |
| 2 | ADR-006 phase attribution 更正 = 属主澄清、非语义变更 | PASS | Consequences/Verification 两处仅把"Phase 1 将实现/验收"拆分为 Phase 1/2/3/4 属主，与开发计划 §41-§45 Gate 对齐；决策本体（profile 定义、8-addon、purchasing→inventory、单调分类现状）未改；用户任务 §7 显式授权。 |
| 3 | ADR-007 = Proposed（无权威），未写入任何 authority 语义 | PASS | ADR-007 Status: Proposed；README 索引标 Proposed；§Decision intent 明确"待用户裁决后转 Accepted"；authority 文档（progressive-adoption/schema/dependency-graph/开发计划）本 commit 未改（git status 核对）。 |
| 4 | 新发现冲突被登记而非隐藏（no silent reinterpretation） | PASS | addon-dependency-map §0/§2/§6 + native-behavior-audit §0 + technical-risks Gate/R11 均显式 BLOCKED 并指向 ADR-007；无任何文件把目标闭包写成已采纳。 |
| 5 | dependency-closure 冲突事实与源码一致 | PASS | §6 矩阵闭包推演基于 odoo-19/addons manifest 实测（sale_mrp=[mrp,sale_stock] auto、mrp_account=[mrp,stock_account] auto、purchase_mrp=[mrp,purchase_stock] auto、sale_stock/purchase_stock/stock_account auto）；supply/delivery/dashboard 计划依赖引用开发计划 §8/§23/§28 行号。 |
| 6 | supply/delivery/dashboard 冲突行被显式标记（未静默改写） | PASS | addon-dependency-map §2 三行结论标 **CONFLICT（§6 / ADR-007 Proposed）**，计划依赖列保持原文；§0 banner 声明"裁决前不静默改写计划依赖"。 |
| 7 | 保持 8-addon；无新增第 9 桥接 addon 提议 | PASS | ADR-007 Decision intent 明示"保持 8-addon"；Alternatives 记录第 9 bridge 已由 ADR-006 §B 裁决否决；目标闭包表仅 8 行。 |
| 8 | purchasing 语义修订以 Proposed 形式呈现（engine-backed 现状未改） | PASS | ADR-007 §Purchasing 语义修订 = amendment proposal；configuration-schema/dependency-graph 的 purchasing engine-backed 行**本 commit 未改**（待裁决）；ADR-006 §A 现状保留并在 Follow-up 指向 ADR-007。 |
| 9 | 仍强制 purchasing→inventory、无 Purchase-only 语义残留 | PASS | ADR-007 明示"仍强制 purchasing_enabled=true→inventory_enabled=true；v0.1 仍不支持 Purchase-only（Deferred）"；grep `Purchase-only` 全为否定语境。 |
| 10 | inventory/mrp 引擎型单调、delivery 业务层语义未被动摇 | PASS | ADR-007 仅提议修订 purchasing 分类与 Profile 1 purchase 表述；inventory_enabled/mrp_production_enabled engine-backed monotonic 与 delivery_enabled workflow ON↔OFF 全库表述未改（schema/dependency-graph/progressive-adoption 未触碰）。 |
| 11 | MTO 受控归 Profile 2（Test E/F/H3）证据链未变 | PASS | native-behavior-audit §8 E–H 原文保留；§0 新 BLOCKED 明确"STOP B 已闭环，不再构成阻塞项"；R10 结论不变，仅实现期属主更正为 Phase 4。 |
| 12 | Phase 3/4 realignment 以 Proposed 呈现 | PASS | ADR-007 §Phase-Gate realignment 表格（Phase 3 Supply&Inventory 无 MRP 退出条件 / Phase 4 Formal MRP+BOM-driven Supply）；开发计划 §43/§44 本 commit 未改（待裁决）；"不建第二缺料真相，ADR-002/003 不变"显式保留。 |
| 13 | 审计缺口被承认并修复 | PASS | 本文件"Audit type"节显式承认 v1.0.2 18 项无闭包检查并回溯判定；新增 #19/#20 永久检查。 |
| 14 | 新增永久 dependency-closure 检查已登记 | PASS | #20 检查定义：对每个 Technical Installation Profile 解析 manifest 传递闭包+auto_install 桥，actual closure == allowed profile engine closure 才 PASS；governance/Phase 验证流程将复用。 |
| 15 | 权威同步范围与 STOP 合同一致 | PASS | 变更清单 = ADR-006（属主更正）、ADR-007+README、addon-dependency-map/native-behavior-audit/technical-risks（BLOCKED/证据）、governance-audit（本文件）；无 authority 语义改写、无业务代码。 |
| 16 | 无业务代码修改 | PASS | git status 仅含 docs/decisions、docs/factory_os、docs/governance/governance-audit.md；无 odoo-19/ 或 scripts/audit 改动。 |
| 17 | Governance Gate 状态机合规 | PASS | STALE 触发（ADR-006 被编辑）→ 本 full re-audit；Phase 0 Gate BLOCKED 为注册冲突的隔离态（非治理失败），与 a19840b 轮先例一致。 |
| 18 | 所有链接可解析 | PASS | 递归相对链接检查全部指向存在文件（ADR-007 新文件 + §0/§6 内部引用 + 文档间链接）。 |
| 19 | ADR-006/technical-risks 无旧"Phase 1 实现 supply 扩展/MTO 校验"误导表述残留 | PASS | grep：ADR-006 Consequences/Verification 与 technical-risks R1/R10 均已改为分相属主；`supply 对 sale.order 的库存扩展`/`MTO 校验` 不再与 Phase 1 绑定（仅 Phase 3/4）。 |
| 20 | **profile↔manifest dependency-closure（新永久检查，回溯）** | REGISTERED | 回溯当前计划依赖：supply→mrp、delivery→production/quality/native delivery、dashboard→全部内部 → 强制引擎面超所属 profile → **FAIL（本应使 v1.0.2 Phase 0 收口 BLOCK）**；经 ADR-007 Proposed + BLOCKED 标记隔离，待用户裁决后按目标闭包落地并复检。 |

## Reported contradictions（resolution 更新）

1. **治理级（v1.0.0 已解决）**：reading order 与 precedence 分离；不变量置顶。未回归。
2. **产品-技术映射级（v1.0.1 已解决，ADR-002 澄清）**：平行库存排除。未回归。
3. **能力/引擎架构级（v1.0.2 已解决，ADR-006 Accepted）**：progressive-adoption L10 绝对规则 vs Safe Minimal——经 STOP A/B + E–H 实证，映射为 Technical Installation Profile（单调安装、不卸载/降级、无假关闭）。未回归。
4. **执行面闭包级（本版登记，ADR-007 Proposed）**：ADR-006 的 profile 契约 vs 计划 8-addon manifest 依赖闭包——supply→mrp 使 Profile 1 变 Profile 2、delivery/dashboard 计划依赖偏高、purchasing 单调分类与 Inventory-only substrate 冲突（addon-dependency-map §6 矩阵）。隔离态 = Phase 0 Gate BLOCKED + ADR-007 Proposed + affected rows CONFLICT；authority 语义改写待用户裁决。

## Gate decision

**Governance Gate: COMPLETE（v1.0.3 re-audit；20 项中 19 PASS + 1 REGISTERED-OPEN（#20 闭包冲突，经 Proposed ADR + BLOCKED 标记按流程隔离，非静默矛盾））。**

- v1.0.2 COMPLETE →（ADR-006 phase-attribution 更正 + dependency-closure STOP）→ STALE →（本 full re-audit）→ **COMPLETE**。
- **Phase 0 Gate: BLOCKED — awaiting ADR-007 user decision**（addon dependency closure inconsistent with ADR-006；证据收集 complete，架构裁决待用户）。
- 不授权任何业务实现；Authority rewrite（progressive-adoption / configuration-schema / configuration-dependency-graph / 开发计划 §8/§23/§28/§43/§44 / addon-dependency-map §2 转正）仅在用户 Accept ADR-007 后执行；System Invariants 与 UI 权威未改。
