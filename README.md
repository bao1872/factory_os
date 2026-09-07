# Factory OS

Factory OS（工厂OS）是一套基于 Odoo 19 Community 的轻量制造执行系统，围绕客户订单贯通物料、采购、库存、生产、质量、交付与追溯。

## 产品原则

- 订单驱动
- 异常优先
- 状态清晰
- 手机友好
- 全链路可追溯
- 每个工厂独立数据库

## 项目结构

```text
addons/                 Factory OS 自定义 Odoo addons
docs/factory_os/        架构、模型、权限、状态机和测试文档
UI/                     UI 设计、页面矩阵和视觉概念
scripts/                本地开发与验证脚本
tests/                  跨模块端到端测试
```

本地 Odoo 19 Community 源码放在 `odoo-19/`，仅作为开发运行时，不提交到本仓库。

## 当前状态

项目处于 Phase 0 技术审计与开发骨架准备阶段。业务定义参见根目录 PRD、开发计划以及 `UI/` 中的设计资料。

## Governance / Start here

所有开发行为（人类 / IDE / Codex / Agent）的治理入口：

- **Governance** → [`docs/governance/README.md`](docs/governance/README.md)：唯一治理入口，含权威层级、Agent 宪法、硬停止条件与变更分级。
- **Architecture Decisions** → [`docs/decisions/README.md`](docs/decisions/README.md)：ADR 索引；只有 Accepted ADR 是架构权威。

### 主要产品权威（冲突解决顺序见治理文档）

1. [`docs/factory_os/system-invariants.md`](docs/factory_os/system-invariants.md)：正确性 / 安全 / 隐私 / 数据真相底线（最高权威）。
2. [`工厂OS 产品需求文档 PRD v0.1.md`](工厂OS%20产品需求文档%20PRD%20v0.1.md)：产品目标、范围与业务语义。
3. [`工厂OS Odoo 模块设计与开发计划 v0.1.md`](工厂OS%20Odoo%20模块设计与开发计划%20v0.1.md)：Odoo 架构、阶段和验收 Gate。
4. [`docs/factory_os/configuration-matrix.md`](docs/factory_os/configuration-matrix.md)：产品可读的 A/B/C 配置目录。
5. [`docs/factory_os/configuration-schema.md`](docs/factory_os/configuration-schema.md)：字段名、存储、类型、默认值、约束、权限、审计和消费方的实现权威。
6. [`docs/factory_os/configuration-dependency-graph.md`](docs/factory_os/configuration-dependency-graph.md)：配置依赖、可见性和禁用行为的实现权威。
7. [`docs/factory_os/progressive-adoption.md`](docs/factory_os/progressive-adoption.md)：Safe Minimal、向导 preset、Just-in-Time Validation 与无迁移升级路径。
8. [`UI/Factory OS UI 设计评审稿 v0.2.md`](UI/Factory%20OS%20UI%20设计评审稿%20v0.2.md)：Odoo 视觉与交互边界。
9. [`UI/Factory OS 页面与UI覆盖矩阵 v0.3.md`](UI/Factory%20OS%20页面与UI覆盖矩阵%20v0.3.md)：设计覆盖与开发范围；70/70 仅表示设计覆盖。

> 上述列表同时是推荐阅读顺序；**它不是冲突解决层级**。文档冲突时的裁决顺序见 [`docs/governance/governance-model.md`](docs/governance/governance-model.md)。

Configuration Governance Gate 已通过 [`docs/factory_os/configuration-governance-audit.md`](docs/factory_os/configuration-governance-audit.md)，Progressive Adoption Gate 已通过 [`docs/factory_os/progressive-adoption-audit.md`](docs/factory_os/progressive-adoption-audit.md)。两项结果只授权进入 Phase 0 技术审计，不代表 70 个设计页面全部进入 v0.1 开发。
