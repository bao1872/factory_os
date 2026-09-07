# ADR-004 Progressive Adoption without Historical Fabrication or Parallel Models

Status: Accepted
Date: 2026-09-07

## Context

目标工厂（5–20 人、流程未标准化）必须能"先用起来再逐步变重"。若启用高级能力要求回填历史，工厂会因迁移成本拒绝升级；若允许伪造历史库存/MRP/追溯记录，则数据真相从第一天起就是假的，追溯与报表失去意义。

既有权威依据：

- progressive-adoption.md 全文（产品与开发权威）：Safe Minimal、向导映射、Just-in-Time Validation、无数据迁移升级路径；
- system-invariants #14（渐进采用）、#4（真实追溯）、#3（库存单一事实源）、#15（Just-in-Time Validation）；
- PRD §0.2。

## Decision

- 高级能力（采购、库存、正式 MRP、质量、追溯）启用后**只对适用的新动作增加约束**；
- **禁止**：重写历史订单、迁移到平行数据模型、批量创建虚假 MO/QC、伪造历史库存或追溯记录、为未来能力全局必填主数据；
- 升级路径 = `订单看板 → 订单+进销存 → 标准生产 → 质量追溯`，全程运行于同一批 `res.partner` / `product.template` / `sale.order` 历史之上；
- 任何历史补录必须是**显式、有审计的业务动作**，不是后台迁移；
- 向导/预设只展开为原子配置，运行时不存在 `management_level` / `maturity_level` / preset 字段（引用 configuration-schema：无此类技术键）。

## Alternatives Considered

- **启用能力时自动回填历史（如为旧订单补 MO/库存事务）**：被否。会产生 system-invariants #4 禁止的"伪造追溯边"，并让库存/成本数字凭空出现。
- **每阶段使用独立数据模型再迁移**：被否。与 ADR-002（单一真相源）冲突，且迁移即重写，违背渐进采用初衷。

## Consequences

- 历史订单在升级后"看起来"不完整（无 MO/库存/QC 关联），这是**有意为之的正确状态**，UI 需允许表达"该单未进入正式生产链路"；
- 追溯覆盖面随真实使用逐步扩大，从启用日期起的新事务开始；
- 测试必须验证：开启某能力不影响既有记录（回归测试）。

## Invariants / Authorities Affected

- 引用：system-invariants #14、#3、#4、#15；progressive-adoption.md 全文件；configuration-schema（无运行时等级字段）。
- 与 ADR-003（执行/MRP 分离）、ADR-002（库存真相）共同构成"升级不造假"的架构基础。

## Verification

- 测试：启用库存/MRP/质量后，既有 SO 无任何新增 stock.move / mrp.production / quality 记录；
- 测试：向导四种 preset 保存后，运行时无等级字段写入（schema 检查）；
- Phase 3/4/5 Gate 的回归证据。

## Supersedes / Superseded By

- Supersedes：任何暗示"升级需要数据迁移或补录历史"的早期表述。
- Superseded By：None。
