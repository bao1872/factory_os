# ADR-001 One Independent Odoo Database per Factory

Status: Accepted
Date: 2026-09-07

## Context

工厂OS面向多家中小工厂。每家工厂是不同的法律/经营主体，数据不得互见；同时工厂之间流程差异真实存在。若用多公司（multi-company）或 record rule 在同一库内隔离所有工厂，隔离的证明与维护成本随工厂数上升，且任何规则漏洞都可能造成跨工厂泄漏。

既有权威依据：

- PRD §3.7 数据隔离：每工厂独立 Workspace 与独立数据库，工厂数据归工厂所有；
- 开发计划 §1 总体技术决策：一个工厂 Workspace = 一个独立 Odoo Database；禁止 Factory A/B/C branch。

## Decision

- 每座工厂拥有**一个独立的 Odoo 数据库**（one database per factory）；
- 全仓库维持 **one codebase**：所有工厂运行同一份 Factory OS Addons，禁止 per-factory fork；
- 工厂间差异只通过 **configuration / capability flag / master data** 表达，不通过代码分支表达；
- 租户隔离优先由"数据库物理边界"保证；`system-invariants` #1 的 company check / ACL / record rule 仍用于**数据库内**（如未来多公司或测试环境）的记录级隔离。

## Alternatives Considered

- **单库多公司（multi-company）**：被否。需要为每个工厂配置 company 维度的 record rule 与数据域，跨工厂访问的证明负担与泄漏面都更大，不符合"工厂数据归工厂所有"的产品承诺。
- **per-factory 代码分支**：被否。分支数量随工厂数线性增长，修复与升级成本失控（开发计划 §1 明确禁止）。

## Consequences

- 每座工厂需要独立的数据库实例与备份/升级流程，运维成本按工厂线性增加（可接受：工厂数在 MVP 阶段为个位数）；
- 跨工厂数据交换只能走 Connector / 显式共享对象，不存在库内直读路径；
- Capability/配置差异天然隔离，不会出现"改 A 厂配置影响 B 厂代码"的问题；
- 多工厂统一升级 = 同代码多库升级，需有升级剧本（Pilot 阶段验证）。

## Invariants / Authorities Affected

- 引用：PRD §3.7；开发计划 §1（架构）；system-invariants #1（库内租户隔离）。
- 不复制上述内容；本 ADR 只是把它们固化为架构决策并明确与 record rule 的分工。

## Verification

- 每座试点工厂运行于独立数据库（Pilot Gate 检查）；
- 代码库中不存在 Factory-specific 分支或条件编译（governance-audit 检查）；
- 跨库数据读取只能通过 Connector 白名单路径（Phase 8 Connector Privacy Gate）。

## Supersedes / Superseded By

- Supersedes：None（此前仅存在于 PRD/开发计划表述，本 ADR 首次固化为 Accepted 决策）。
- Superseded By：None。
