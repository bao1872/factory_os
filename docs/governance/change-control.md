# Factory OS Change Control v1.0

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

**要求**：Agent 可在授权 Phase 内执行，但**必须先更新权威再写代码**；权威更新本身需符合 [文档更新规则](#4-文档更新规则)。典型入口：修改 configuration-schema 的某行 → 实现 → 测试 → 与 dependency-graph 一致性检查。

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
- 破坏性外部契约变更；
- 治理文档本身的变更。

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

## 4. 文档更新规则

| 发生什么 | 更新哪份文档 |
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

## 6. 变更记录

- GOVERNED 与 ARCHITECTURAL 变更应在 commit message 中注明涉及的权威文档与 ADR 编号；
- 涉及配置的变更自动落入 `factory.config.audit`（运行时审计），本文件管辖的是文档与实现变更纪律；
- commit 前必须 `git diff --check` 通过。
