# Factory OS Governance Consistency Audit

Date: 2026-09-07
Scope: governance documentation only; authorization is Governance documentation only. No business code was added, no product semantics changed.

## Delta

- Added `docs/governance/`：`README.md`（唯一治理入口）、`governance-model.md`（8 治理域、权威层级、Phase Gates）、`agent-constitution.md`（6 条 Agent 规则）、`stop-conditions.md`（硬停止 + 升级路径）、`change-control.md`（STANDARD/GOVERNED/ARCHITECTURAL + 文档更新规则）。
- Added `docs/decisions/`：`README.md`、`ADR-TEMPLATE.md`、ADR-001…ADR-005（全部由既有已批准决策归纳，无新架构发明）。
- Modified root `README.md`：保留产品简介；"Authority" 段改为 "Start here → docs/governance/README.md"；明确阅读顺序 ≠ 冲突解决层级；新增 Governance 与 Architecture Decisions 链接。

## Consistency results

| # | Check | Result | Evidence |
|---|---|---|---|
| 1 | 无互相矛盾的权威层级 | PASS | 单一权威层级定义于 `governance-model.md` §1（System Invariants → ADR → PRD → Dev Plan → Configuration → UI → Implementation）；根 README 与 governance README 均引用同一层级，无第二套顺序。 |
| 2 | Reading order 与 precedence 被明确区分为不同概念 | PASS | governance/README.md §3 与根 README 均写明"列表是推荐阅读顺序，不是冲突解决层级"；冲突裁决只引用 governance-model §1。原 README 将两者混合的表述已删除。 |
| 3 | 治理文档与 PRD 无重复 | PASS | governance 文档以"引用 + 编号"指向 PRD/开发计划/schema，不复制其正文；唯一例外是五个产品问题（本任务 §5 明确要求锁定为 scope filter），已注明引用 PRD §2.2。 |
| 4 | 无第二套 A/B/C 变更分类 | PASS | `change-control.md` 使用 STANDARD/GOVERNED/ARCHITECTURAL；显式声明 A/B/C 仅保留给配置治理的配置项性质，两者分工写明。全文 grep 无 A/B/C 变更分级。 |
| 5 | 每个硬 STOP 有 owner / 升级路径 | PASS | `stop-conditions.md` 六个类别逐条给出 Owner 与升级路径；"授权恢复"节规定 STOP 只能由人类解除。 |
| 6 | ADR 与既有已批准决策一致 | PASS | ADR-001←开发计划 §1/PRD §3.7；ADR-002←不变量 #3/开发计划 §10-12；ADR-003←不变量 #2/#14/schema 基础执行段；ADR-004←progressive-adoption/不变量 #14；ADR-005←不变量 #13/UI 24-v2。均引用既有权威，无新架构决策。 |
| 7 | System Invariants 仍强于实现文档 | PASS | 未修改 `system-invariants.md`；层级置顶为最高权威；`governance-model.md` 明确"测试是证据不是权威，通过测试不能使违反不变量的行为合法化"。 |
| 8 | Configuration Governance 保持完整 | PASS | 未修改 configuration-matrix/schema/dependency-graph 及 configuration-governance-audit；change-control GOVERNED 类要求配置变更先更新权威；C 类无配置入口重申于 governance-model 域 5。 |
| 9 | Progressive Adoption 保持完整 | PASS | 未修改 progressive-adoption.md 及其 audit；ADR-003/004 引用并固化其语义。 |
| 10 | 22-surface MVP scope 不变 | PASS | 未修改 UI 覆盖矩阵；governance-model 域 2 重申 70/70 仅设计覆盖、开发以 22 工作面为准。 |
| 11 | Phase 0 仍是唯一授权实施阶段 | PASS | governance-model §3 定义 Phase 0–8/Pilot Gates；明示"当前仅 Phase 0 获得实施授权"；governance/README §5 同步声明。 |
| 12 | 无业务代码新增 | PASS | `git status` 仅含 docs/governance/、docs/decisions/ 新增与 README.md 修改；变更文件全为 .md。 |
| 13 | 所有链接可解析 | PASS | 脚本校验 65 个相对链接全部指向存在的文件。 |
| 14 | `git diff --check` 通过 | PASS | 无空白错误（含 audit 文件）。 |

## Reported contradictions（预检查报告，仅治理级在本任务解决）

1. **治理级（已解决）**：原根 README 把阅读顺序表述为权威层级，且 `system-invariants` 被排在配置文档之后。本任务将两者分离：阅读顺序保留于 README，权威层级唯一化于 governance-model.md，不变量置顶。
2. **产品-技术映射级（仅报告，未解决，留给 Phase 0）**：PRD §35 建议模型名（`factory.customer`、`factory.sales_order`、`factory.inventory` 等）与 PRD §36 / 开发计划 §4、§51"扩展 Odoo 原生模型、禁止平行模型"冲突。PRD §35 自带免责条款（"如优先复用 Odoo 原生模型…"），治理上以 ADR-001/002/003 + 开发计划为准；最终裁决由 Phase 0 `model-mapping.md` 完成并需用户确认。本次未修改任何产品文档。

## Gate decision

**Governance Gate: COMPLETE — all checks PASS.**

本决策授权 Phase 0（Odoo Reality Audit）作为唯一实施阶段。不授权任何业务实现；不改变 22-surface MVP scope；不改变配置/渐进采用/UI 既有权威。
