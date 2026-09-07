# Factory OS Change Control v1.0.1

v1.0.1（2026-09-07）：治理文档自身变更由"一律 ARCHITECTURAL"改为按语义影响分级（新增 §4），并增加 Audit staleness rule。

状态：**Development / Agent Authority**。本文定义所有代码与文档变更的分级与流程。

> **不是每个代码变更都需要治理文档变更。** 这一条是防止治理变成开发开销的关键。绝大多数变更属于 STANDARD，直接实现即可；只有改变语义或边界的变更才触发上级流程。

变更分级不使用 A/B/C 命名——Factory OS Configuration Governance 已把 A/B/C 用于配置项性质（A 工厂策略 / B 产品默认 / C 系统不变量），为避免第二个 A/B/C 含义，变更分级固定使用：

```text
STANDARD
GOVERNED
ARCHITECTURAL
```

两者关系：A/B/C 描述**配置项的静态性质**；STANDARD/GOVERNED/ARCHITECTURAL 描述**一次变更的动态控制级别**。C 类不变量没有配置入口；任何触碰不变量的实现变更都至少是 GOVERNED，触及语义则升级为 ARCHITECTURAL。

---

## 1. STANDARD（标准变更）

**含义**：不改变语义、不改变权威文档的常规改动。

示例：

- CSS / 布局；
- 文案（wording）；
- 搜索过滤器（非语义调整）；
- 非语义 UI 改进；
- 保持行为的内部重构；
- 测试改进。

**流程**：

```text
code
+ relevant test
```

**要求**：Agent 可直接实现。通常无需更新任何权威文档。

## 2. GOVERNED（受治理变更）

**含义**：改变系统行为语义或边界条件，需要权威文档先行的变更。

示例：

- 配置语义（A/B 配置项的默认值、范围、可编辑角色、依赖行为）；
- 字段语义（字段含义、计算逻辑、校验时机）；
- 状态转换（Execution/Health/Gate 语义）；
- 风险规则（`factory.risk.rule` 边界）；
- 角色权限（ACL / record rule / 字段 groups 边界内调整）；
- Gate（QC Gate、Committed Date Gate 行为）；
- 能力行为（capability flag 的实际效果）；
- 业务校验（服务层校验逻辑）。

**流程**：

```text
identify/update authority      ← 先更新对应权威文档（configuration-matrix/schema/dependency-graph…）
→ implementation
→ automated tests
→ consistency check
```

**要求**：Agent 可在授权 Phase 内执行，但**必须先更新权威再写代码**；权威更新本身需符合 [文档更新规则](#5-文档更新规则)。典型入口：修改 configuration-schema 的某行 → 实现 → 测试 → 与 dependency-graph 一致性检查。

## 3. ARCHITECTURAL（架构变更）

**含义**：改变架构宪法、产品边界或不可逆结构。

示例：

- 新持久业务模型；
- 新数据真相源（Source of Truth）；
- 数据迁移；
- Connector 披露范围扩张（白名单新增字段类别）；
- Odoo core 修改；
- 新工作流引擎；
- 租户架构变更（one-codebase / one-db-per-factory）；
- MVP 范围扩张（新 P0/P1）；
- 破坏性外部契约变更。

**治理文档自身的变更不按"文件路径是否属于 docs/governance"一刀切归类，改按语义影响分级，见 [§4](#4-治理文档自身的变更governance-document-change)。**

**流程**（强制性，顺序不可跳过）：

```text
STOP                        ← 触发 stop-conditions，先停
→ ADR proposal              ← 形成 ADR（Proposed）
→ explicit user authorization ← 用户明确批准
→ authority update          ← 更新权威文档（含将 ADR 置 Accepted）
→ implementation
→ regression evidence
```

**要求**：无用户明确授权，Agent 不得进入 implementation 阶段。

## 4. 治理文档自身的变更（Governance-document Change）

治理文档（`docs/governance/`、`docs/decisions/` 及根 README 的治理链接段）的变更**按语义影响分类，不按文件路径分类**。治理文档内的改动不是自动 ARCHITECTURAL——多数是 STANDARD 或 GOVERNED；反过来，真正改变治理语义的改动即使只改一行也是 ARCHITECTURAL。

### 4.1 STANDARD governance-document change

只包括：

- typo / 错别字；
- formatting（排版）；
- broken link 修复；
- 不改变语义的措辞澄清（wording clarification）；
- audit 证据 / 结果刷新（按 [§4.4](#44-audit-staleness-rule审计过期规则) 的 targeted check 或 full re-audit 结果落盘至 [Governance Audit](governance-audit.md)）；
- 引用 SHA / 路径更新。

**无需 ADR**，Agent 可直接修改、验证并提交。

### 4.2 GOVERNED governance-document change

包括：

- Agent 操作纪律（operational discipline）；
- 完成证据要求（completion evidence requirements）；
- 报告格式（report format）；
- 执行流程（execution procedure）；
- 非架构性的开发控制行为。

要求：

```text
explicit authority identification   ← 指出被修改的治理文档与条款
→ document update
→ consistency check
→ user authorization（若用户已就该行为变更明确发出指令，本步即已满足）
```

**不需要 ADR。**

典型示例：**Remote Delivery Verification**（Agent Constitution §7，2026-09-07 加入）——它改变的是 Agent 操作纪律与完成证据要求，不触碰权威层级、STOP 权力、变更分级语义、ADR 流程或 Phase 授权模型，因此归类为 GOVERNED，而非 ARCHITECTURAL。

### 4.3 ARCHITECTURAL governance change

仅包括真正改变以下任一语义的治理修改：

- authority precedence（权威层级顺序）；
- System Invariant authority（不变量权威边界）；
- STOP authority / 谁能解除 STOP；
- change-class semantics（本文件的分级语义本身）；
- ADR authority / process；
- tenant / data-truth architecture governance；
- scope escalation rights（谁有权扩大范围）；
- Phase authorization model（阶段授权模型）。

必须：

```text
STOP → Proposed ADR → explicit user approval → authority update → verification
```

### 4.4 Audit staleness rule（审计过期规则）

治理文档的语义性修改会使既有的 Governance Audit 过期：

- **STANDARD**（typo / link-only）治理修复：可只做 targeted check，**不**使整个 Governance Gate 失效；
- **GOVERNED / ARCHITECTURAL** 治理语义修改：既有审计结果自动失效，**Governance Gate 置为 STALE**，必须重新执行完整 [Governance Audit](governance-audit.md) 后才能重新声明 `Governance Gate: COMPLETE`；
- Gate 状态机（见 governance-audit）：`COMPLETE →（治理语义修改）→ STALE →（full re-audit）→ COMPLETE`。

禁止出现"审计全 PASS，但被审权威随后已变化却未重新审计"的状态。

## 5. 文档更新规则

本表管辖**产品 / 业务 / 实现权威**（PRD、ADR、Invariants、configuration-*、progressive-adoption、UI 权威）在何种语义变化时更新。**治理文档自身的变更（governance/ 与 decisions/）按 [§4](#4-治理文档自身的变更governance-document-change) 分类**，不落入本表。
|---|---|
| 产品意义或产品范围改变 | PRD |
| 架构决策改变 | ADR（新 ADR 或修订） |
| 正确性 / 安全 / 隐私 / 数据真相边界改变 | System Invariants |
| 技术配置语义改变 | configuration-schema |
| 配置依赖行为改变 | configuration-dependency-graph |
| 采用 / cutover 语义改变 | progressive-adoption |
| 交互模型实质性改变 | UI authority（评审稿 / 覆盖矩阵） |
| 配置目录（产品可读层）改变 | configuration-matrix |

**不要为以下内容更新任何治理文档：**

- CSS 修复；
- 间距；
- 标签；
- 普通 bug 修复（行为语义不变时）；
- 内部重构；
- 测试清理；
- 非语义的 XML 视图修正。

## 5. 变更与测试的配套

| 级别 | 代码 | 测试 | 权威更新 | 审批 |
|---|---|---|---|---|
| STANDARD | ✓ | relevant test | 通常不需要 | Agent 自主 |
| GOVERNED | ✓ | automated tests | 需要（先行） | Agent 在授权 Phase 内自主，但须一致性检查 |
| ARCHITECTURAL | ✓ | regression evidence | 需要 | 用户明确授权 |

## 7. 变更记录

- GOVERNED 与 ARCHITECTURAL 变更应在 commit message 中注明涉及的权威文档与 ADR 编号；
- 涉及配置的变更自动落入 `factory.config.audit`（运行时审计），本文件管辖的是文档与实现变更纪律；
- commit 前必须 `git diff --check` 通过。
