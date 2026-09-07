# Factory OS Governance Model v1.0

状态：**Development / Agent Authority**。本文定义 Factory OS 的治理域、权威层级、治理分级（STANDARD / GOVERNED / ARCHITECTURAL 见 [change-control.md](change-control.md)）与 Phase Gates。

治理目的不是添加产品规则，而是控制"未来的人类 / IDE / Codex / Agent 开发"。产品内容引用权威文档，不在本文复制。

---

## 1. 治理层级（Governance Hierarchy）

系统内存在一个不可倒置的权威秩序。越靠上的层级约束力越强，实现层自由度越小。

```text
System Invariants           正确性 / 安全 / 隐私 / 数据真相
        ↓
Architecture / ADR          明确的架构决策
        ↓
Product / Scope             产品目的、范围、业务语义
        ↓
Configuration               可配置业务策略与技术实现
        ↓
UI / Workflow               交互与呈现
        ↓
Implementation              代码必须符合以上全部
```

**规则：层级越高，实现 Agent 的自由度越小。**

- 较低层级必须服从较高级层。
- 文档冲突时按 [阅读顺序与权威层级分离原则](README.md#3-agent--开发者在动工前必须读什么)：reading order 只服务理解，precedence 只服务冲突解决。
- 冲突解决顺序：System Invariants → Accepted ADR → PRD → Development Plan → Configuration authorities → UI authorities → Implementation。
- **测试是证据，不是更高权威。** 一个通过的测试不能使违反不变量或已接受 ADR 的行为合法化；测试失败通常意味着实现或测试错了，不意味着权威该改。若证据表明权威本身错了，按 [change-control.md](change-control.md#architectural) 走 ARCHITECTURAL 流程修改权威，而不是静默绕过。

---

## 2. 八个治理域

### 域 1 — Product Governance（产品治理）

| 项 | 内容 |
|---|---|
| Purpose | 维持产品定位、核心目标与业务语义不被开发过程侵蚀 |
| Authority | PRD；系统不变量只覆盖正确性/安全底线 |
| Governed decisions 示例 | 五个产品问题的定义；产品原则（订单驱动、异常优先…）；非目标边界（财务/HR/MES/APS/PLM/WMS） |
| Agent 可自主决定 | 无——Agent 不裁决产品语义 |
| 需升级 | 任何需要改变 PRD 语义才能满足的需求（→ STOP） |

### 域 2 — Scope Governance（范围治理）

| 项 | 内容 |
|---|---|
| Purpose | 阻止未经授权的范围扩张（"容易做 / Odoo 自带 / 相邻页面需要"都不是实施理由） |
| Authority | PRD §33 MVP 范围；UI 覆盖矩阵的 22 个 MVP 工作面；开发计划 Phase Gates |
| Governed decisions 示例 | 每个特性的 Scope Status；MVP-P0/P1 与 Post-MVP / Phase 8 / Deferred 边界 |
| Agent 可自主决定 | 只实施已被当前授权 Phase 明确包含的实现工作；拒绝新增 P0/P1 的提议 |
| 需升级 | 新增 MVP-P0/P1 特性 → 显式 Scope Change（→ STOP） |

**五个产品问题（范围过滤器）**——任何建议的特性必须能回答其一，否则默认拒绝（引用 PRD §2.2，不复制）：

```text
1. What orders exist?          现在有哪些订单？
2. What material is missing?   这些订单需要什么物料、缺不缺？
3. Where is production now?    每个订单生产到什么阶段？
4. What quality problems?      当前有什么质量问题或异常？
5. When can the order deliver? 每个订单何时能交付？
```

**每个提议特性必须有一个 Scope Status：**

```text
MVP-P0
MVP-P1
Post-MVP
Phase 8
Deferred
Rejected
```

以下表述**不授权实施**：`nice to have`、`easy to add`、`do while here`。新 MVP-P0/P1 特性需要显式 Scope Change。

**70/70 UI Design Coverage ≠ Development Scope。** UI 覆盖矩阵的 70/70 仅表示设计覆盖；开发只以 22 个 MVP 工作面与各 Phase Gate 为准。两者必须始终分开表述。

### 域 3 — Architecture Governance（架构治理）

| 项 | 内容 |
|---|---|
| Purpose | 维持 one-codebase 架构宪法与"扩展 Odoo 而非替换 Odoo"原则 |
| Authority | 开发计划 §1/§51；已接受 ADR（docs/decisions/）；System Invariants |
| Governed decisions 示例 | 新持久业务模型；数据真相源；模块边界；addon 依赖 |
| Agent 可自主决定 | 在既有架构宪法内实现；决定某字段/方法归属哪个既有模块 |
| 需升级 | 创建新的持久业务模型 / 新 Source of Truth / Odoo core 修改 / per-factory fork / 平行交易系统（→ STOP → ADR） |

**架构宪法（引用开发计划 §1、§51 与 ADR，不复制细节）：**

```text
One codebase
One independent Odoo database per factory      （ADR-001）
Extend Odoo rather than replace Odoo
No Odoo core-source modification
No per-factory source-code forks
No parallel Sales Order                        （ADR-003）
No parallel inventory ledger                   （ADR-002）
No parallel formal MRP                         （ADR-003）
No fake traceability database
No dashboard copy as business truth
```

**新业务模型的决策序列**——每个提议的新业务模型必须顺序通过：

```text
Can native Odoo model be reused?
        ↓ no
Can native Odoo model be extended?
        ↓ no
Is a thin Factory OS model genuinely required?
```

在创建任何新的持久业务模型前，Agent 必须记录：

- 为什么原生 Odoo 模型无法表达它；
- 它是否成为新的数据真相源（Source of Truth）；
- 生命周期归属；
- 与既有 Odoo 模型的关系；
- 一致性机制；
- 删除 / 归档语义；
- 为什么 computed / report / service 模型不足以满足需求。

**创建新的 Source of Truth 是 ARCHITECTURAL 变更，必须 STOP → ADR → 明确授权。**

### 域 4 — Data & State Governance（数据与状态治理）

| 项 | 内容 |
|---|---|
| Purpose | 保持 Odoo 原生模型为唯一业务真相；禁止派生层升级为业务真相 |
| Authority | System Invariants；configuration-schema；已接受 ADR（ADR-002） |
| Governed decisions 示例 | 哪个模型承载某类数据；状态字段归属；派生/报表层读取规则 |
| Agent 可自主决定 | 在已映射的原生模型上加派生计算；决定某状态由哪个服务维护 |
| 需升级 | 引入可独立修改的平行数据表；Dashboard/报表层要成为业务真相（→ STOP） |

**数据权威映射（当前映射；Phase 0 model-mapping 后冻结并细化，不复制 schema 全部字段）：**

```text
Partner        -> res.partner
Product        -> product.template / product.product
Sales Order    -> sale.order
Purchase Order -> purchase.order
Inventory      -> stock.*  (quant / move / move.line / picking / lot)
Lot/Serial     -> stock.lot
Formal MRP     -> mrp.production / mrp.workorder / mrp.bom
Shipment       -> stock.picking
Simple execution -> sale.order.factory_*（执行状态/人工进度/预计完成，非交易状态）
```

**四个互不相同的状态概念**——不得静默折叠进同一个 state 字段：

```text
Transaction State          原生交易生命周期（sale.order.state / stock.picking.state…）
Execution State            履约执行阶段（factory_execution_state）
Health State               正常 / 预警 / 风险（factory_health_state）
Gate / Permission-to-act   是否可以执行某动作（QC Gate、Committed Date Gate…）
```

Dashboard、报表与追溯层是 **read / derived** 层，只能从底层真相读取与聚合，不能成为独立业务真相，不得保存第二份业务事实（引用开发计划 §29）。

### 域 5 — Configuration Governance（配置治理）

| 项 | 内容 |
|---|---|
| Purpose | 维护 A/B/C 配置语义与依赖行为；保证"不确定就配置"只用于业务策略 |
| Authority | configuration-matrix（产品可读目录）、configuration-schema（字段级实现）、configuration-dependency-graph（依赖行为）；C 类内容最终归属 System Invariants |
| Governed decisions 示例 | A/B 类配置项的默认值、范围、可编辑角色；依赖启停策略（BLOCK / AUTO_DISABLE / HIDE_KEEP / ENABLE_REQUIRED） |
| Agent 可自主决定 | 按 schema 实现既有配置项的读写、依赖与审计逻辑 |
| 需升级 | 改变任一配置项的语义 / 默认值 / 依赖行为 / 新增配置项（→ GOVERNED，且须先更新权威） |

C 类（系统不变量）无配置入口，不出现在设置页，不提供关闭开关。Configuration Governance Gate 已由 [`configuration-governance-audit.md`](../factory_os/configuration-governance-audit.md) 通过，Progressive Adoption Gate 已由 [`progressive-adoption-audit.md`](../factory_os/progressive-adoption-audit.md) 通过；两者只授权进入 Phase 0。

### 域 6 — Security & Privacy Governance（安全与隐私治理）

| 项 | 内容 |
|---|---|
| Purpose | 保证租户隔离、最小权限、Connector 最小披露不被实现细节破坏 |
| Authority | System Invariants（#1、#8、#9）；configuration-schema 权限与 Connector 段 |
| Governed decisions 示例 | 角色权限边界；record rule；字段级 ACL；Connector 字段白名单 |
| Agent 可自主决定 | 实现既有安全设计的机制（access CSV / ir.rule / 字段 groups / 白名单） |
| 需升级 | 跨公司访问不确定；ACL / record rule 行为不确定；敏感字段暴露不确定；Connector 载荷隐私不确定（→ STOP） |

安全验证必须穿透菜单层：menu、直接 URL/action、ORM/RPC、search、export、import/write、connector payload。菜单隐藏不是安全控制（引用 system-invariants #8 执行层）。

### 域 7 — Development / Agent Governance（开发 / Agent 治理）

| 项 | 内容 |
|---|---|
| Purpose | 约束开发者与 Agent 行为：不静默重释、先验证后编码、不扩范围、不虚假完成、最小变更 |
| Authority | [agent-constitution.md](agent-constitution.md)；[change-control.md](change-control.md) |
| Governed decisions 示例 | 编码前应做哪些验证；变更应落在哪一层；汇报需要什么证据 |
| Agent 可自主决定 | 在授权范围内按宪法与变更分级执行；选择验证手段 |
| 需升级 | 任何触犯 Agent 宪法规则的情况（→ 按宪法各条处理，多数直接 STOP） |

### 域 8 — Verification & Release Governance（验证与发布治理）

| 项 | 内容 |
|---|---|
| Purpose | 保证"完成"有证据、Gate 有出口、回归有记录 |
| Authority | 开发计划测试体系（§49-50）；各 Phase Gate 的 required evidence；System Invariants 执行层测试要求 |
| Governed decisions 示例 | 一个功能是否达到可提交的验证标准；Phase Gate 是否满足退出条件 |
| Agent 可自主决定 | 编写并运行测试；收集证据；报告结果 |
| 需升级 | 宣称某个 Phase Gate 通过 / 某项不变量验证通过（→ 证据须完整且可复核；Gate 通过由用户确认） |

---

## 3. Phase Gates

Phase Gate 定义在本文（为治理结构的一部分），具体功能要求以[开发计划](../../工厂OS%20Odoo%20模块设计与开发计划%20v0.1.md)为准，不在本文重复。

每个 Gate 的通用含义：

- **Entry conditions**：进入该 Phase 的前置条件；
- **Required evidence**：判定完成所必须的证据；
- **Exit conditions**：离开该 Phase（进入下一 Phase）的条件；
- **STOP conditions**：该 Phase 内出现即停止的条件（通用硬停止见 [stop-conditions.md](stop-conditions.md)，此处仅列 Phase 特有项）。

### Phase 0 — Odoo Reality Gate（当前唯一授权 Phase）

> 目的：用真实 Odoo 19 Community 行为验证 Factory OS 假设；**Observed Odoo behavior outranks assumptions。**

| 项 | 内容 |
|---|---|
| Entry conditions | Governance 系统建立（本任务完成）；配置治理 Gate 与渐进采用 Gate 已通过；不修改产品语义 |
| Required evidence | 产出或验证以下文件：`docs/factory_os/model-mapping.md`、`native-behavior-audit.md`、`addon-dependency-map.md`、`state-map.md`、`security-baseline.md`、`technical-risks.md`（若等价文件已存在则复用/更名，须有证据，不得凭空新建）；每项不变量到模型约束/服务校验/ACL/record rule/测试用例的映射 |
| Mandatory native-behavior tests | ① Simple SO + inventory capability OFF → 确认 Odoo 是否创建 stock picking/moves；② Purchasing ON + inventory OFF → 确认真实收货行为；③ Formal MRP OFF → 确认 procurement/MO 行为；④ Capability 稍后启用 → 确认历史交易是否收到原生副作用 |
| Exit conditions | 上述文件与测试完成；native 行为结论记录；配置/schema/依赖图冻结 |
| STOP conditions | 现实 Odoo 行为与当前架构冲突 → STOP（**不得在 Phase 0 打补丁绕过**，须先更新权威/ADR 再继续） |

### Phase 1 — Core & Security Gate

| 项 | 内容 |
|---|---|
| Entry | Phase 0 exit；invariant→test 映射完成 |
| Required evidence | 开发计划 §41 验收项全 PASS（模块安装/卸载、菜单、权限、越权测试、配置页、向导、依赖隐藏、配置审计、不变量绕过测试、Safe Minimal、Committed Date Gate、JIT Validation…）；Phase 1 退出条件对应测试 |
| Exit | 全部验收 PASS；Operator 无法经 URL/RPC 读取采购价、客户/供应商数据、Admin 设置 |
| STOP（Phase 特有） | 任何"允许绕过"配置被提出作为失败解决方案（应修正模型/权限/服务/测试） |

### Phase 2 — Simple Order Execution Gate

| 项 | 内容 |
|---|---|
| Entry conditions | Phase 1 exit |
| Required evidence | 开发计划 §42 流程与验收 PASS（Customer→Quotation→SO→Execution Status；Customer PO、Requested/Committed 日期、Order Health、附件、搜索、角色访问） |
| Exit conditions | 无库存/MO/QC 依赖的订单执行闭环 PASS |
| STOP conditions | 执行状态与原生交易状态被混用（不变量 #2）；订单进入 Active 前无 Committed Date（不变量 #12） |

### Phase 3 — Supply & Inventory Gate

| 项 | 内容 |
|---|---|
| Entry conditions | Phase 2 exit |
| Required evidence | 开发计划 §43 真实 BOM 端到端 PASS（SO→BOM Explosion→Demand→Available→Shortage→PO→Receipt→Available）；库存完整性测试 |
| Exit conditions | 端到端 Supply 闭环 PASS；库存数量可由 stock.* 复核 |
| STOP conditions | 需要平行库存台账或伪造库存记录才能通过（不变量 #3） |

### Phase 4 — Formal MRP Gate

| 项 | 内容 |
|---|---|
| Entry conditions | Phase 3 exit |
| Required evidence | 开发计划 §44 全流程 PASS（Material Ready→MO→Work Orders→Operator Update→Finished Qty→Finished Lot）；库存变化 / 组件消耗 / 成品库存 / Lot 正确 |
| Exit conditions | 真实 MO 闭环 PASS 且未破坏 stock/mrp 事务 |
| STOP conditions | 为 UI 简单化破坏 Odoo stock/mrp transaction；历史订单被重写成 MO（不变量 #14） |

### Phase 5 — Quality Gate

| 项 | 内容 |
|---|---|
| Entry conditions | Phase 4 exit |
| Required evidence | 开发计划 §45：故意 FAIL → QC Hold → NCR → Corrective Action → Verification → Closed；订单 Health=RED；FAIL 数量进入受控库存处置 |
| Exit conditions | 三种检验（来料 / 过程 / 成品）闭环 PASS；Gate 无法被绕过 |
| STOP conditions | QC Gate 可经 RPC / import 绕过；"仅记录"让不合格品继续表现为可用（不变量 #5、#6） |

### Phase 6 — Delivery & Traceability Gate

| 项 | 内容 |
|---|---|
| Entry conditions | Phase 5 exit |
| Required evidence | 开发计划 §46：SO→MO→Lot→QC Pass→Ready to Ship→Picking→Shipped→Delivered；批次正反向追溯完整追出 |
| Exit conditions | 交付与追溯闭环 PASS；追溯关系全部来自真实 stock/mrp/QC |
| STOP conditions | 追溯需要伪造关系或人工备注充当追溯边（不变量 #4） |

### Phase 7 — Dashboard Gate

| 项 | 内容 |
|---|---|
| Entry conditions | Phase 6 exit |
| Required evidence | 开发计划 §47：Dashboard 每个数字可从底层记录人工复算并可下钻到精确记录集；异常优先布局 |
| Exit conditions | 工作台数字 = 记录集；无第二份业务事实 |
| STOP conditions | Dashboard 保存业务数据副本或作为业务真相（开发计划 §29） |

### Phase 8 — Connector Privacy Gate

| 项 | 内容 |
|---|---|
| Entry conditions | Phase 7 exit |
| Required evidence | 开发计划 §48：单工厂 ↔ Central Trade DB 共享订单链路 PASS；载荷只含白名单字段；私有字段零泄漏；幂等验证 |
| Exit conditions | 共享链路 PASS；隐私测试 PASS |
| STOP conditions | Connector 载荷包含被禁字段；跨工厂 / 无关数据可被中央查询（不变量 #9） |

### Pilot — Real Factory Adoption Gate

| 项 | 内容 |
|---|---|
| Entry conditions | Phase 1–8 授权范围内完成；1–2 家真实工厂愿意试用 |
| Required evidence | 真实工厂连续使用；80% 活跃生产订单入系统；替代至少 2/3 的 Excel（订单 / 库存 / 生产进度 Excel）；老板 30 秒内回答"这个订单做到哪里" |
| Exit conditions | MVP 成功标准达成（PRD §32） |
| STOP conditions | 试用暴露未授权的新 P0/P1 需求 → 走 Scope Change，不得边试点边临时加功能 |

**Gate 纪律**：未通过当前 Gate，不进入下一 Phase；当前唯一授权 Phase 为 **Phase 0**。Phase 0 的授权来自本治理任务本身及既有两份 Gate audit。
