# Factory OS Hard Stop Conditions v1.0

状态：**Development / Agent Authority**。以下任何一条被触发，**立即停止一切相关 mutation**（不提交、不继续实现、不静默绕行），按文末格式输出 STOP 报告，等待授权变更。

STOP 不是失败，是治理的正常输出。误报 STOP 的成本远低于漏报。

---

## 1. Architecture（架构）

| # | STOP 条件 | Owner / 升级路径 |
|---|---|---|
| A1 | 提议新的数据真相源（Source of Truth） | 用户（架构负责人）→ ADR 流程 |
| A2 | 平行 Odoo 交易系统（第二套 sales/inventory/MRP 事实） | 用户 → ADR 流程 |
| A3 | Odoo core source 修改 / 补丁 | 用户 → ADR 流程 |
| A4 | per-factory 代码 fork | 用户 → ADR 流程 |
| A5 | 未经先前授权的破坏性数据迁移 | 用户 → 迁移方案评审 |
| A6 | 新的持久业务模型未通过"复用→扩展→薄模型"决策序列 | Agent 先行自检；不满足即 STOP 上报 |

## 2. Odoo Reality（Odoo 现实）

| # | STOP 条件 | Owner / 升级路径 |
|---|---|---|
| O1 | 原生 Odoo 行为存在实质性不确定（无法经检查/复现消除） | 用户 → Phase 0 native-behavior-audit 记录 |
| O2 | 运行时行为与开发权威矛盾 | 用户 → 判断改实现还是改权威（ARCHITECTURAL 流程） |
| O3 | capability flag 没有产生其声称的原生行为 | 用户 → native-behavior-audit；不得静默接受 |

## 3. Data（数据）

| # | STOP 条件 | Owner / 升级路径 |
|---|---|---|
| D1 | 库存正确性不确定（数量无法由 stock.* 复核） | 用户（+ Inventory 权威）→ 数据修复方案，禁止将错就错 |
| D2 | 追溯需要伪造关系（人工备注充当追溯边 / 凭空回填历史） | 用户 → 拒绝伪造，改由真实事务积累 |
| D3 | 状态转换语义需要被重新解释（Transaction/Execution/Health/Gate 被折叠） | 用户 → state-map 修正（ARCHITECTURAL） |

## 4. Security（安全）

| # | STOP 条件 | Owner / 升级路径 |
|---|---|---|
| S1 | 跨公司访问不确定（工厂 A 用户可能读到工厂 B 记录） | 用户 → 安全基线评审，先验证后放行 |
| S2 | record rule / ACL 行为不确定 | 用户 → security-baseline 验证 |
| S3 | 敏感字段暴露不确定（成本/毛利/报价等） | 用户 → 字段级 ACL 评审 |
| S4 | Connector 载荷隐私不确定 | 用户 → 白名单复核，禁止"先发了再说" |

安全必须穿透菜单验证：menu、直接 URL/action、ORM/RPC、search、export、import/write、connector payload。

## 5. Product / Scope（产品 / 范围）

| # | STOP 条件 | Owner / 升级路径 |
|---|---|---|
| P1 | 实现需要新的 MVP-P0/P1 能力 | 用户（产品负责人）→ Scope Change |
| P2 | 当前需求不改变 PRD 语义就无法满足 | 用户 → PRD 变更评审 |
| P3 | Post-MVP / Deferred / Phase 8 项在当前范围成为必需 | 用户 → Scope Change |

## 6. Governance（治理）

| # | STOP 条件 | Owner / 升级路径 |
|---|---|---|
| G1 | 两个活跃权威文档相互矛盾 | 用户 → 治理冲突裁决（本次任务已预置 resolution 见 governance-audit） |
| G2 | 已接受 ADR 与提议实现冲突 | 用户 → ADR 修订 / 新 ADR |
| G3 | 实现将违反 System Invariant | 用户 → 不变量修订（最高级 ARCHITECTURAL） |

---

## STOP 输出格式

触发 STOP 时，必须输出以下块（中英术语均可），并在获得授权前不继续 mutation：

```text
STOP CONDITION          <类别-编号，如 Architecture-A1>
Observed Fact           <观察到的客观事实，附证据>
Expected Authority      <所依据的权威文档与条目>
Delta                   <现实与权威的差距>
Affected Scope          <受影响的功能/模型/模块/Phase>
Safe Options            <2+ 个不破坏治理的选项>
Recommended Option      <推荐选项及理由>
```

示例：

```text
STOP CONDITION          Odoo Reality-O1
Observed Fact           SO 确认后（inventory_enabled=false）原生仍创建了 stock.picking（实测 Odoo 19 Community，xxx）
Expected Authority      configuration-schema：inventory_enabled=false 的禁用行为
Delta                   文档假设能力关闭即无库存副作用，原生行为相反
Affected Scope          Phase 0 订单执行 / 配置依赖图
Safe Options            (a) 更新依赖图记录真实行为并约束 UI；(b) 重新界定 inventory_enabled 语义（需 ADR）
Recommended Option      (a) 先记录真实行为，进入 native-behavior-audit，再决定是否触发 (b)
```

## 授权恢复

STOP 只能由**人类（产品/架构负责人）**解除，方式为显式书面授权之一：

- 接受 Recommended Option（或指明另一选项）；
- 批准 ADR / 权威文档修订；
- 批准 Scope Change。

Agent 收到授权后，按 [change-control.md](change-control.md) 对应级别执行。**"用户没回复就继续"与"用户沉默视为同意"都不成立。**
