# ADR-005 No Offline Business Transactions in v0.1

Status: Accepted
Date: 2026-09-07

## Context

生产现场网络不稳定，产品曾设想"离线也能干活、联网后自动同步"。但库存/MRP 事务如果离线写入本地、之后重放，会带来：并发冲突、双写、权威状态（单号/库存/质检结论）由客户端生成的正确性风险，以及"以为成功了其实没有"的用户误导。v0.1 的优先目标是让权威业务状态只由服务器产生并确认。

既有权威依据：

- system-invariants #13（MVP 网络失败边界）：v0.1 不支持 offline-first 或离线业务事务；
- configuration-governance-audit：以 `24-mobile-confirmation-and-network-failure-v2.png` 替换含"本地保存/自动同步"表达的旧稿（UI authority 已同步）；
- system-invariants #10 执行层：客户端不得生成权威单号/库存数量/MO 进度/质检结论。

## Decision

- **v0.1 不存在离线业务事务**：不得把权威库存/MRP 事务持久化到本地，不得建立离线事务队列、自动重放、reconnect merge 或冲突解决；
- 网络失败时的行为边界：只在**当前页面内**保留尚未提交的表单输入、明确显示失败、允许用户**手动 Retry**；收到服务器成功响应前不得显示业务动作成功；
- 关闭/刷新页面可能丢失未提交输入，UI 必须明确提示；
- 浏览器内存中的未提交控件值不得被称为"本地草稿/已保存"。

## Alternatives Considered

- **本地队列 + 后台自动重放**：被否。会在服务器侧产生不可控的重放顺序与重复事务，客户端还会生成权威数据，违反不变量 #10。
- **本地完整离线应用**：被否。成本高且与"one database per factory + 服务端权威"架构冲突；真实需求未验证前不做。

## Consequences

- 现场断网时只能继续查看与记录草稿输入，不能完成库存/生产/质检动作——这是 v0.1 的明确产品边界；
- UI 网络失败态是必须设计的一等状态（已锁定 24-v2 基准），不是错误处理附赠品；
- 未来若真实工厂证明离线写入是硬需求，需新 ADR 重开此决策（Post-MVP）。

## Invariants / Authorities Affected

- 引用：system-invariants #13、#10 执行层；UI authority（24-v2 网络失败基准）。
- 本 ADR 把不变量 #13 固化为架构决策，供 Connector/移动端实现引用。

## Verification

- 测试：断网提交不生成服务器业务记录、不进入后台队列；恢复网络后仅由用户主动重试一次（system-invariants Phase 1 退出条件）；
- UI 验证：网络失败页符合 24-v2 基准，无"本地已保存/自动同步"文案。

## Supersedes / Superseded By

- Supersedes：早期 `24-mobile-confirmation-and-offline-board` 概念中"本地保存 + 自动同步"的设计意向（UI authority 已将其标记为历史稿）。
- Superseded By：None（若未来允许离线事务，由新 ADR supersede 本 ADR）。
