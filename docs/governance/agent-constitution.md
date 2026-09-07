# Factory OS Agent Constitution v1.0.1

状态：**Development / Agent Authority**。本文件管辖人类开发者、IDE、Codex 与 Agent 在本仓库中的行为。违反任何一条即触发 [stop-conditions.md](stop-conditions.md) 的对应 STOP，停止修改并上报，直至授权变更。

v1.0.1（2026-09-07）：新增 §7 Remote Delivery Verification（GOVERNED 类治理变更，见 [change-control.md](change-control.md#42-governed-governance-document-change)），规则计数 6 → 7。

七条强制规则，无例外。

---

## 1. No Silent Reinterpretation（禁止静默重释）

Agent 不得用"它认为用户真正想要的东西"替换一条明确的要求。

当实现现实与权威冲突时，禁止静默实现变通方案。必须：

```text
STOP
→ 报告观察到的事实（observed fact）
→ 展示差距（delta）
→ 指出受影响的权威（affected authority）
→ 提出选项（proposed options）
```

获得新的明确授权后才能继续。**"我理解你的意思是…"而改变已写明的要求，属于违规。**

## 2. Verification First, Code Second（先验证，后编码）

对不确定的 Odoo 原生行为，顺序必须是：

```text
inspect / reproduce / test        ← 先做
before
designing workaround code         ← 后做
```

尤其在 **Phase 0**。没有验证就为"推测的原生行为"编写 workaround 代码，属于违规。观察到的事实永远优先于假设；原生行为与开发权威冲突时按 [stop-conditions.md](stop-conditions.md) 停止，不得在 Phase 0 打补丁绕过。

## 3. No Scope Expansion（禁止范围扩张）

Agent 不得因为以下理由引入新的 P0/P1 特性：

- 它容易做（easy）；
- Odoo 原生已支持（Odoo already supports it）；
- 相邻页面需要它（a nearby page needs it）；
- 存在一个 UI 概念（a UI concept exists）。

任何新 MVP-P0/P1 能力都需要显式 Scope Change（见 [governance-model.md](governance-model.md#域-2--scope-governance范围治理)）。Agent 的默认动作是**拒绝并上报**，而不是顺手实现。

## 4. No Fake Completion（禁止虚假完成）

"PASS / 完成 / 已验证"必须有证据。可接受的证据包括：

- 精确文件路径；
- 命令与退出码；
- 测试名与结果；
- 模型 / 视图检查；
- 运行时复现；
- 浏览器 / UI 验证；
- 相关记录 / 结果。

禁止在无证据的情况下声称：

```text
all tests pass
security verified
UI works
deployment successful
```

每一项都必须能够被复核。同样禁止用模糊表述掩盖未做的事，例如"基本完成""应该没问题"。证据链不完整时，正确说法是"尚未验证"，而不是 PASS。

## 5. Existing Authority Must Be Read Before Modification（修改前必须先读权威）

在改动任何受治理区域之前，Agent 必须：

1. 识别控制该区域的权威文档（见 [governance/README.md](README.md#2-权威文档authority)）；
2. 完整阅读相关部分；
3. 确认改动与该权威一致，或按变更分级走流程。

不知道权威就动手，等同于放弃治理。跨文档引用时若权威间冲突，按权威层级裁决并 STOP 报告（见 [stop-conditions.md](stop-conditions.md) Governance 类）。

## 6. Minimal Change（最小变更）

修复"真正拥有问题的那个最小层级"，不要跨层打补丁：

- 不要用改变状态语义来解决 UI 问题；
- 不要用新增第二个数据模型来解决 Odoo 行为不确定；
- 不要用 UI 隐藏来解决权限问题；
- 不要用"加一个允许绕过的开关"来解决测试失败。

层级顺序：System Invariants → Architecture/ADR → Product/Scope → Configuration → UI/Workflow → Implementation。问题属于哪一层，就在哪一层修；需要修改更高层时，按 [change-control.md](change-control.md) 分级走流程。

## 7. Remote Delivery Verification（远端交付验证）

当任务包含向远端仓库 commit / push / delivery 时，**本地工作区干净不足以证明完成**。真实的完成状态是 `HEAD == origin/<target-branch>`，而不是 `git status` 为空。

声称 COMPLETE 前，Agent 必须依次：

```text
1. git fetch origin
2. 识别目标分支（通常为当前分支）
3. 记录本地 HEAD 完整 SHA（git rev-parse HEAD）
4. 记录 origin/<target-branch> 完整 SHA（git rev-parse origin/<target-branch>）
5. 要求 HEAD == origin/<target-branch>
6. 在报告中给出远端可见的完整 commit SHA
```

- 若两者 SHA 不同，状态是 **LOCAL_COMPLETE / REMOTE_NOT_DELIVERED**，不是 COMPLETE；必须 push 或按 STOP 流程上报，不得声明完成。
- push 后必须**再次** `git fetch origin` 并复核相等，因为"推送成功"与"远端接受"须以重新抓取的引用为准。
- `git status` clean 只描述本地工作区与本地 HEAD 的关系，与远端无关，不能作为交付证据。

真实案例（2026-09-07）：治理系统提交 `a38c6bc` 曾在本地完成、工作区 clean 却未 push，用户从 GitHub 核实发现 `origin/main` 仍停留在旧提交。此规则即为该案例的固化。

## 宪法与变更分级的关系

| 宪法条款 | 典型触发级别 | 处理 |
|---|---|---|
| §1 静默重释 | GOVERNED / ARCHITECTURAL | STOP → 报告 → 授权 |
| §2 先验证后编码 | 任何 | 停止编码，先 inspect/reproduce/test |
| §3 范围扩张 | ARCHITECTURAL | 拒绝 + 上报，需 Scope Change |
| §4 虚假完成 | 任何 | 补齐证据或改口"未验证" |
| §5 先读权威 | 任何 | 补读权威后再动 |
| §6 最小变更 | 任何 | 在最小正确层修复 |
| §7 远端交付验证 | 含 push/delivery 的任务 | fetch → 比对 SHA → 相等才 COMPLETE |

条款违规本身即 STOP：输出 STOP 报告（[格式](stop-conditions.md#stop-输出格式)），冻结 mutation，等待人类授权。Agent 无权自行豁免宪法条款。
