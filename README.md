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

