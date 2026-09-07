# Factory OS Governance — 项目治理入口

本目录是 Factory OS 项目的**唯一治理入口**。它约束人类开发者、IDE、Codex 与 Agent 在本仓库中的一切开发行为，回答"做什么、依据什么、何时停下、如何证明做完"。

本文件只描述治理结构，不新增产品规则。产品内容以各权威文档为准。

---

## 1. 治理是为什么

治理存在的目的只有一个：**保证任何开发行为都不会破坏系统正确性、安全性、数据真实性或已批准的产品边界**。

- 它是控制机制，不是文档堆砌。
- 治理必须减少歧义；如果某个新增文档没有减少歧义，就不应创建。
- 不改变产品语义；只改变"谁有权决定、按什么流程决定"。

## 2. 权威文档（Authority）

以下文档是权威来源。冲突解决顺序见 [治理模型](governance-model.md) 中的权威层级（reading order ≠ precedence）。

### 产品权威

| 文档 | 管辖 | 位置 |
|---|---|---|
| 系统不变量 | 正确性 / 安全 / 隐私 / 数据真相 | [`docs/factory_os/system-invariants.md`](../factory_os/system-invariants.md) |
| 已接受的 ADR | 明确作出的架构决策 | [`docs/decisions/README.md`](../decisions/README.md) |
| PRD | 产品目的 / 范围 / 业务语义 | [`../../工厂OS 产品需求文档 PRD v0.1.md`](../../工厂OS%20产品需求文档%20PRD%20v0.1.md) |
| 开发计划 | 模块架构 / 阶段边界 / Gate | [`../../工厂OS Odoo 模块设计与开发计划 v0.1.md`](../../工厂OS%20Odoo%20模块设计与开发计划%20v0.1.md) |

### 配置权威

| 文档 | 管辖 | 位置 |
|---|---|---|
| 配置矩阵 | 产品可读配置目录（A/B/C） | [`docs/factory_os/configuration-matrix.md`](../factory_os/configuration-matrix.md) |
| 配置 Schema | 字段级实现权威 | [`docs/factory_os/configuration-schema.md`](../factory_os/configuration-schema.md) |
| 配置依赖图 | 依赖与禁用行为 | [`docs/factory_os/configuration-dependency-graph.md`](../factory_os/configuration-dependency-graph.md) |
| 渐进采用 | 采用 / cutover 语义 | [`docs/factory_os/progressive-adoption.md`](../factory_os/progressive-adoption.md) |

### UI 权威

| 文档 | 管辖 | 位置 |
|---|---|---|
| UI 设计评审稿 | 视觉与交互边界 | [`../../UI/Factory OS UI 设计评审稿 v0.2.md`](../../UI/Factory%20OS%20UI%20设计评审稿%20v0.2.md) |
| UI 覆盖矩阵 | 设计覆盖 70/70；MVP 范围 = 22 个工作面 | [`../../UI/Factory OS 页面与UI覆盖矩阵 v0.3.md`](../../UI/Factory%20OS%20页面与UI覆盖矩阵%20v0.3.md) |

## 3. Agent / 开发者在动工前必须读什么

**必读**（每次任务开始前，无论任务大小）：

1. [治理 README（本文件）](README.md)
2. [治理模型](governance-model.md)（治理域、权威层级、Phase Gates）
3. [Agent 宪法](agent-constitution.md)（禁止静默重释、禁止虚假完成等）
4. [硬停止条件](stop-conditions.md)
5. [变更控制](change-control.md)（变更分级）

**按需读取**：

- 将修改的受治理区域所对应的权威文档（见上表）；
- 相关的已接受 ADR（见 [`docs/decisions/`](../decisions/README.md)）；
- 当前 Phase 的审计 / 映射文档。

**推荐阅读顺序**（仅为理解顺序，不是冲突解决顺序）：

```text
1. docs/governance/README.md
2. PRD
3. Development Plan
4. System Invariants
5. 相关 ADRs
6. Configuration Schema / Dependency Graph / Progressive Adoption
7. UI Review / UI Coverage
8. 当前 Phase 的 audit / mapping 文档
```

## 4. 什么必须 STOP

遇到以下任何情况，**停止修改并上报**，直到授权变更：

- 触碰 [硬停止条件](stop-conditions.md) 中任何一条；
- 检测到两个活跃权威文档相互矛盾；
- 实现与已接受 ADR 或系统不变量冲突；
- 需要新的 MVP-P0/P1 能力；
- 对原生 Odoo 19 Community 行为的判断不确定，且尚未通过检查/复现确认。

STOP 不是失败，是治理的正常输出。停止后按 [硬停止格式](stop-conditions.md#stop-输出格式) 汇报。

## 5. Agent 可自主执行的变更

仅限 [变更控制](change-control.md) 中的 **STANDARD** 与 **GOVERNED** 类（且遵守 Phase Gate 授权）：

- STANDARD：CSS / 文案 / 非语义改进 / 保持行为的内部重构 / 测试改进——直接实现，附相关测试。
- GOVERNED：配置语义、字段语义、状态转换、Gate、权限等——先确认/更新权威文档，再实现并测试。

**ARCHITECTURAL** 类变更一律先 STOP → 提出 ADR → 获得明确授权后才实现。

当前仅 **Phase 0（Odoo Reality Audit）** 获得实施授权；其他 Phase 在各自 Gate 通过前不得实施。

## 6. 架构决策记录在哪里

架构决策记录在 [`docs/decisions/`](../decisions/README.md)：

- 模板见 [`ADR-TEMPLATE.md`](../decisions/ADR-TEMPLATE.md)；
- 只有 **Accepted** 状态的 ADR 才是架构权威；
- 新建持久业务模型、新数据真相源、Odoo 内核修改等必须先形成 ADR。

## 7. 完成工作需要什么证据

"完成 / PASS"必须有证据。可接受的证据包括：

- 精确文件路径；
- 命令与退出码；
- 测试名与结果；
- 模型 / 视图检查结果；
- 运行时复现；
- 浏览器 / UI 验证；
- 相关记录 / 结果。

禁止在无证据的情况下声称"全部测试通过 / 安全已验证 / UI 可用 / 部署成功"。完整规则见 [Agent 宪法 §4](agent-constitution.md#4-no-fake-completion-禁止虚假完成)。

测试是**证据**，不是更高权威；通过测试不能使违反不变量的行为合法化。见 [治理模型](governance-model.md) 权威层级。

## 8. 治理文档本身如何变更

治理文档的变更属于 **ARCHITECTURAL** 类，必须走 [变更控制](change-control.md#architectural) 流程：STOP → ADR 提议 → 明确授权 → 更新权威 → 实施 → 回归证据。治理文档本身不得随意堆砌，任何新增治理文档都必须能明确减少歧义。
