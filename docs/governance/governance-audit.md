# Factory OS Governance Consistency Audit

Date: 2026-09-07（v1.0.1 re-audit）
Scope: governance documentation only; authorization is Governance documentation only. No business code was added, no product semantics changed, no new product/architecture decision self-declared.

## Audit type & staleness trigger

v1.0.1 包含 GOVERNED 级治理语义修改（治理文档变更分级语义调整、Audit staleness rule 新增、Agent Constitution 计数修正、ADR-002 Supersedes 澄清），按 [change-control.md §4.4](change-control.md#44-audit-staleness-rule审计过期规则)，v1.0.0 审计结果自动失效，**Governance Gate 置为 STALE**。本文件即 STALE 状态下重新执行的完整 consistency audit。

### Gate 状态机

```text
COMPLETE →（GOVERNED / ARCHITECTURAL 治理语义修改）→ STALE →（本 full re-audit）→ COMPLETE
COMPLETE →（STANDARD 治理修复：typo / link-only）→ targeted check，Gate 不失效
```

禁止出现"审计全 PASS 但被审权威随后已变化"的状态。

## Delta（v1.0.1 修复）

- `change-control.md` v1.0 → v1.0.1：§3 ARCHITECTURAL 示例移除"治理文档本身的变更"；新增 §4「治理文档自身的变更」——按语义影响分级（4.1 STANDARD / 4.2 GOVERNED / 4.3 ARCHITECTURAL governance-document change）+ 4.4 Audit staleness rule；原 §4-6 顺延为 §5-7，内部引用同步修正。
- `agent-constitution.md` v1.0 → v1.0.1：§7 Remote Delivery Verification（63ad14a 加入）确认归类 **GOVERNED**（见 [change-control §4.2](change-control.md#42-governed-governance-document-change)）；规则计数 6 → 7。
- `governance/README.md`：§3 读取要求由"每次任务必读 5 份"改为按 STANDARD / GOVERNED / ARCHITECTURAL 分层；§8「治理文档本身如何变更」改为按语义分类并附 staleness 简述。
- `docs/decisions/ADR-002…`：Supersedes 文案澄清——不撤销技术结论；ADR-002 **约束 PRD §35 的解释**（平行库存不得实现），具体 model mapping（reuse / extend / thin）在 Phase 0 冻结；`factory.customer` / `factory.sales_order` / `factory.production_order` 等保留给 Phase 0 逐项验证。
- `.gitignore`：新增 `.workbuddy/`（IDE 本地 workspace memory，确认仅含本地日志、不含 authority/source/test fixtures/required configuration）。
- 本文件：v1.0.0 PASS → STALE → v1.0.1 re-audit。

## Consistency results（v1.0.1，14 项）

| # | Check | Result | Evidence |
|---|---|---|---|
| 1 | Governance-document changes 按语义影响分类，而非按文件路径 | PASS | `change-control.md` §4 建立三类（STANDARD/GOVERNED/ARCHITECTURAL governance-document change）；§3 不再含"治理文档本身一律 ARCHITECTURAL"；grep 无残留旧规则。 |
| 2 | Remote Delivery Verification 正确归类为 GOVERNED | PASS | `change-control.md` §4.2 明示其归类与理由（操作纪律/完成证据要求，不触碰层级/STOP/分级/ADR/Phase 语义）；`agent-constitution.md` 标题注释与 `README.md` §8 同步引用。 |
| 3 | Agent Constitution 活动规则数 = 7（所有位置一致） | PASS | `agent-constitution.md` 正文"七条强制规则，无例外"，§1–§7 齐全；grep `六条/6 条强制/6 条 Agent` 于 docs/ 零命中。 |
| 4 | ADR-002 与 Phase 0 model-mapping 边界一致 | PASS | ADR-002 Supersedes 澄清为"约束 PRD §35 解释 + Phase 0 冻结具体 mapping"；与 governance-model Phase 0 Gate 的 Required evidence（`model-mapping.md`）一致。 |
| 5 | 未重新开放平行库存选项 | PASS | system-invariants #3 未修改；ADR-002 Decision 未变；ADR-002 澄清行明示"Phase 0 不重新开放该已被排除的架构选择"。 |
| 6 | Audit staleness rule 存在 | PASS | `change-control.md` §4.4 定义 STANDARD targeted check / GOVERNED+ARCHITECTURAL 置 STALE / 状态机；`README.md` §8 简述；本文件 Gate 状态机节落地。 |
| 7 | 读取负担按变更级别分层 | PASS | `governance/README.md` §3 分 STANDARD（README + relevant authority）/ GOVERNED（+Constitution/Change Control/STOP 相关节/ADR）/ ARCHITECTURAL（完整 pack）；无"每次任务必读全部"残留。 |
| 8 | `.workbuddy/` 处理明确，仓库状态不再被污染 | PASS | `.gitignore` 新增 `.workbuddy/`；目录内容核实仅为 `memory/2026-09-07.md`（IDE 本地日志）；`git status --short` 已不再列出 `.workbuddy/`。 |
| 9 | System Invariants 仍为最高权威 | PASS | 未修改 `system-invariants.md`；governance-model §1 层级未变；change-control §5 仍要求语义改变先更新对应权威。 |
| 10 | 22 MVP 工作面不变 | PASS | 未触碰 UI 覆盖矩阵与 PRD；governance-model 域 2 未改。 |
| 11 | Phase 0 仍是唯一下一授权阶段 | PASS | governance-model §3 与 README §5 未改；本任务未引入任何新 Phase 授权。 |
| 12 | 无业务代码修改 | PASS | `git status` 变更仅 5 文件：`.gitignore`、ADR-002、governance README、agent-constitution、change-control，全为治理文档/repo hygiene；audit 自身待本 commit 加入。 |
| 13 | 所有链接可解析 | PASS | 脚本校验 71 个相对链接全部指向存在的文件。 |
| 14 | `git diff --check` 通过 | PASS | 无空白错误（audit 文件写入后于 commit 前复检）。 |

## Reported contradictions（resolution 更新）

1. **治理级（v1.0.0 已解决）**：原根 README 把阅读顺序表述为权威层级。已分离：reading order（governance README §3）与 precedence（governance-model §1）为不同概念，不变量置顶。本次复核未回归。
2. **产品-技术映射级（本次裁决边界收紧，ADR-002 澄清）**：PRD §35 早期模型建议名（`factory.customer` / `factory.sales_order` / `factory.production_order` / `factory.inventory` 等）与 PRD §36 / 开发计划"扩展原生模型"的关系，此前表述为"留 Phase 0 裁决"。现澄清为：**凡涉及平行库存事实源的部分（`factory.inventory` / `factory.stock_move` / `factory.lot`）已被 system-invariants #3 + Accepted ADR-002 排除，不再由 Phase 0 重新裁决**；Phase 0 `model-mapping.md` 的任务是对每个 PRD 业务对象确认 reuse native / extend native / thin custom 的具体映射，不重开已被不变量禁止的架构选择。PRD §35/§36 产品文档本身未修改（超出本次授权）。

## Gate decision

**Governance Gate: COMPLETE（v1.0.1 re-audit 全 PASS）。**

- v1.0.0 COMPLETE →（GOVERNED 语义修改）→ STALE →（本 full re-audit）→ **COMPLETE**。
- 授权维持 Phase 0（Odoo Reality Audit）为唯一实施阶段。不授权任何业务实现；不改变 22-surface MVP scope；不改变配置/渐进采用/UI 既有权威。
- 后续治理建设停止：除非发生 GOVERNED / ARCHITECTURAL 变化，不再继续"优化治理"；进入 Phase 0 用真实 Odoo 19 Community 验证。
