# Factory OS Governance Consistency Audit

Date: 2026-09-07（v1.0.5 re-audit）
Scope: governance documentation + authority consistency; 本审计覆盖 **ADR-007 Proposed → Accepted**（v1.0.4 已审）+ 之后 commit `b74a6e4`（GOVERNED authority-first change，修改 `configuration-schema.md` 角色属主与字段归属）触发的 re-audit，以及 Phase 1A core kernel 实现（`d0f191c`）与 Phase 1A.1 hardening 的 authority 一致性复检。No business code added.

## Audit type & staleness trigger

- **ADR-007（ARCHITECTURAL）由 Proposed 转 Accepted**（用户 2026-09-07 裁决 Accept with final architecture：能力图、8-addon 精确 manifest 合同、Purchasing=Workflow、Quality=Factory-addon-backed monotonic、Delivery=Workflow、Phase 1–4 属主、PROFILE_CONTRACTS 永久闭包、Dashboard/Optional-module registry 规则）——按 [change-control.md §4.4](change-control.md#44-audit-staleness-rule审计过期规则)，新 Accepted ARCHITECTURAL 语义 + 更新多条 authority → Governance Gate 置 **STALE**。本文件即 STALE 状态下重新执行的完整 consistency audit（v1.0.4）。
- **b74a6e4（GOVERNED authority-first change，2026-09-07）**：commit 自身标记为 GOVERNED，修改 `configuration-schema.md`——①权限映射的角色 XML ID 从各业务 addon（orders/supply/production/quality/delivery/connector）改归 `factory_os_core`（角色身份 ≠ 业务模型 ACL）；②新增「Optional-engine field ownership」规则（core 只拥有 identity/role identity/capability truth/audit/consistency，stock/mrp/quality/delivery 关系字段归 owning addon）。按 change-control §4.4，GOVERNED 治理语义修改 → Governance Gate 再次 STALE → 需 full re-audit。**v1.0.4 的审计范围早于此改动，故 v1.0.4 的 COMPLETE 状态不适用于当前仓库**——本文件 v1.0.5 即为此 STALE 状态下的完整 re-audit。
- v1.0.3 遗留的 **REGISTERED-OPEN #20**（profile↔manifest dependency-closure）：ADR-007 现已 Accepted 并落地 → 本版转 **PASS**，并新增永久检查 #21（Technical Installation Profile manifest closure，PROFILE_CONTRACTS 逐 profile 复检）。

### Gate 状态机

```text
COMPLETE →（GOVERNED / ARCHITECTURAL 治理语义修改）→ STALE →（本 full re-audit）→ COMPLETE
COMPLETE →（STANDARD 治理修复：typo / link-only）→ targeted check，Gate 不失效
```

禁止出现"审计全 PASS 但被审权威随后已变化"的状态。

## Delta（v1.0.3 → v1.0.4）

- **ADR-007（Proposed → Accepted）**：Status 转正；写入最终能力图（P0→P1 分支 Purchasing/Quality/Delivery、P1→P2 Formal MRP；非梯子）；**8-addon 精确 manifest 合同**（§3.1–3.8：core=base/mail/web/contacts/product；orders=core+sale；supply=core+orders+stock+purchase+sale_stock+purchase_stock 无 mrp；production=core+orders+supply+stock+mrp+sale_mrp+purchase_mrp；quality=core+orders+stock 无 mrp/supply/production/purchase；delivery=core+orders+stock 无 production/quality/mrp/delivery；dashboard=core+orders；connector=core+orders）；**capability 分类改判**（purchasing=Workflow/Business ON↔OFF、quality=Factory-addon-backed monotonic requires inventory NOT mrp、delivery=Workflow）；**Phase 1–4 属主**；**PROFILE_CONTRACTS + verify_profile_closure**（永久架构验证，本轮只写合同）；Dashboard/optional-module registry 守卫规则；Supersedes 范围（仅 ADR-006 §A/§D 必要部分）。
- **ADR-006**：Follow-up 更新为"ADR-007 Accepted，supersede §A purchasing/quality 分类、§D Profile 1/3 表述"；§A/§D 受影响行加 supersede 指针（决策本体保留，不重写）。
- **decisions/README.md**：ADR-007 行转 Accepted（含一句话决策）。
- **progressive-adoption.md v1.2**：capability 分类语义更新；Technical Installation Profiles 重构为能力图 + 独立扩展表（Quality/Delivery/Dashboard/Connector manifest 目标）；约束补 purchasing OFF 用户不获原生 groups + 永久闭包检查。Quick Start presets 与质量映射表**未改**（Business UX 不变）。
- **configuration-schema.md**：capability 分类段重构为三类（Engine-backed / Factory-addon-backed monotonic / Workflow-Business）；`purchasing_enabled` 行改 Workflow（ON↔OFF、不宣称 addon 存在）；`quality_enabled` 行改 Factory-addon-backed monotonic（NOT requires mrp）。
- **configuration-dependency-graph.md**：Graph 注释 + Machine-readable table 的 purchasing/quality/delivery 行同步改判。
- **addon-dependency-map.md**：§0 Gate 转正（PASS）；§2 表格改为 **manifest 目标合同**（CONFLICT 消除）；§5 约束重写；§6 闭包矩阵转正（8 行 PASS）；新增 **§7 PROFILE_CONTRACTS 永久契约**（含算法与允许适配/STOP 条款）。
- **开发计划**：§0.1 capability 语义更新；§3 addon 结构改为能力图 + 精确依赖指引（含 addon-dependency-map 链接）；§5 orders 精确目标（core+sale，禁 stock/sale_stock/purchase/mrp）；§8 supply deps 去 mrp（+显式 sale_stock/purchase_stock）；§13 production deps 显式 mrp/sale_mrp/purchase_mrp；Quality 新增精确 Dependencies 段（core+orders+stock，无 mrp/supply/production/purchase）；§23 delivery deps 收敛；§28 dashboard deps 收敛；§41 Phase 1 属主（NO Supply/MRP/MTO）；§43 Phase 3 Gate 重写（无 BOM/MRP 退出条件，E2E=收货→库存→可用）；§44 Phase 4 Gate 重写（Formal MRP + BOM-driven shortage，Material Shortage DERIVED）。
- **native-behavior-audit.md**：§0 Gate → **PASS**（保留 BLOCKED 历史时间线；证据本体 E–H 未改）。
- **technical-risks.md**：Gate → **PASS**；R1/R11 更新为 ADR-006+ADR-007 Accepted 双裁决表述（残留执行风险 Phase 1/3/4）。
- 未修改：System Invariants（无真实矛盾）；UI 设计文档；configuration-matrix.md（产品可读矩阵不含 capability/依赖语义）；Quick Start preset（Business UX 不变）。

## Delta（v1.0.4 → v1.0.5）

- **b74a6e4（GOVERNED authority-first change）触发 STALE**：该 commit 明确标记 GOVERNED，修改 `configuration-schema.md`——①权限映射角色 XML ID 从各业务 addon（`factory_os_orders.group_factory_sales_manager` 等）改归 `factory_os_core.group_factory_*`；②新增「Optional-engine field ownership」规则。按 change-control §4.4，GOVERNED 治理语义修改 → Gate STALE → 必须 full re-audit（v1.0.5）。v1.0.4 审计范围早于此改动，故其 COMPLETE 不适用当前仓库。
- **Phase 1A core kernel（d0f191c）+ Phase 1A.1 hardening 的 authority 一致性复检**：core 角色组定义、字段归属、manifest P0 安全、安全模型、ADR-007 边界是否仍与权威一致。属实现落地后的 authority 一致性核验（实现类变更本身不属治理语义，但需确认未越权威边界）。
- **SETTINGS-AUDIT-01 登记为 Phase 1B 延后验证项**：属实现验证事项，**非**治理矛盾，不置 Gate BLOCKED。详见下方 #23。

## Consistency results（v1.0.5，23 项）

| # | Check | Result | Evidence |
|---|---|---|---|
| 1 | ADR-007 = Accepted；supersede 范围仅限 ADR-006 依赖/profile 必要部分 | PASS | ADR-007 Status: **Accepted**；§Consequences/Supersedes 明示"supersede ADR-006 §A（purchasing/quality 分类）与 §D（Profile 1/3 表述），其余 ADR-001~006 维持 active"；ADR-006 Follow-up + §A/§D 行内指针一致。 |
| 2 | ADR-007 §3 8-addon 精确依赖 = 开发计划 manifest 目标 | PASS | 逐模块比对：开发计划 §5(orders)/§8(supply)/Quality deps/§13(production)/§23(delivery)/§28(dashboard) 与 ADR-007 §3.2–3.7 列表一致（含顺序语义）；core/connector 目标见 §3.1/§3.8。 |
| 3 | addon-dependency-map §2 转正 = ADR-007 §3；§6 闭包矩阵全 PASS | PASS | §2 表 8 行结论 PASS（CONFLICT 已解，保留原计划依赖作为历史对照与修改说明）；§6 矩阵 8 行 PASS（含 forbidden 检查列）。 |
| 4 | supply 依赖无 mrp/sale_mrp/purchase_mrp | PASS | ADR-007 §3.3、开发计划 §8、addon-dependency-map §2/§6 均无 mrp 系；grep `supply.*mrp` 无 manifest 目标命中。 |
| 5 | delivery 依赖无 production/quality/mrp/native delivery | PASS | ADR-007 §3.6（禁 factory_os_production/quality/mrp/delivery）、开发计划 §23 = core+orders+stock。 |
| 6 | dashboard 依赖无 supply/production/quality/delivery/stock/mrp | PASS | ADR-007 §3.7、开发计划 §28 = core+orders；registry 守卫瓦片仅为未来实现模式，非 manifest 依赖。 |
| 7 | quality 依赖无 mrp/supply/production/purchase/quality* | PASS | ADR-007 §3.5、开发计划 Quality Dependencies = core+orders+stock；禁 mrp/supply/production/purchase/quality/quality_control/quality_mrp。 |
| 8 | orders 依赖无 stock/sale_stock/purchase/mrp | PASS | ADR-007 §3.2、开发计划 §5 = core+sale；grep 无 sale_stock 于 orders 目标。 |
| 9 | purchasing_enabled = Workflow/Business（非 engine-backed） | PASS | configuration-schema capability 分类段 + `purchasing_enabled` 行、configuration-dependency-graph Graph+Machine 表、progressive-adoption v1.2、开发计划 §9 均标注 Workflow/Business ON↔OFF；grep `purchasing.*engine-backed monotonic` 无命中。 |
| 10 | purchasing_enabled requires inventory；无 Purchase-only | PASS | 四权威同述 `requires inventory_enabled`；Purchase-only 全库否定语境（INVALID/Deferred）；Inventory-only 合法。 |
| 11 | quality_enabled = Factory-addon-backed monotonic、requires inventory、NOT requires mrp | PASS | configuration-schema `quality_enabled` 行、dependency-graph、progressive-adoption、ADR-007 §5 一致；无 "quality requires mrp" 残留（process 除外）。 |
| 12 | process_inspection_enabled 确实 requires mrp_production_enabled | PASS | configuration-schema 行 + dependency-graph Machine 表：`process_inspection_enabled` requires quality+mrp（保留，未被 quality 独立化波及）。 |
| 13 | delivery_enabled = Workflow、requires inventory、不绑 Odoo delivery addon | PASS | ADR-006 §E/ADR-007 §6、schema/dependency-graph/progressive-adoption 一致；Odoo delivery/carrier = Post-MVP optional。 |
| 14 | Phase 1 无 Supply/MRP/MTO 业务实现 | PASS | 开发计划 §41 顶部 ADR-007 属主注；technical-risks R1/R10 实现期属主 = Phase 3/4；无"Phase 1 实现 supply 扩展/MTO 校验"残留。 |
| 15 | Phase 3 无 BOM/MRP 退出条件 | PASS | 开发计划 §43 重写：范围=Warehouse/Location/Quant/PO/Receipt/Incoming/Available/Reserved/Lot/Serial/Reorder/Scrap/Inventory Count；显式"不得要求 mrp.bom/mrp.production/BOM explosion/MTO/Manufacture route"；原 BOM E2E 移至 §44。 |
| 16 | Phase 4 拥有 BOM-driven shortage | PASS | 开发计划 §44 重写：BOM/Explosion/Manufacturing Demand/Shortage/MO/Work Order/MTO/Consumption/Finished Lot；Material Shortage = DERIVED（不建第二账本）。 |
| 17 | 能力图替代梯子；Quality 独立于 P2；Quick Start presets 未改 | PASS | ADR-007 §1、progressive-adoption Technical Profiles 能力图、开发计划 §3 图一致（P0→P1 分支 P/Q/D、P1→P2）；Quality manifest 不依赖 mrp/production；Quick Start 4 preset 表与质量映射表原样保留（Business UX）。 |
| 18 | System Invariants / UI / configuration-matrix / MVP surface 未改 | PASS | git status 无 system-invariants.md / UI 目录 / configuration-matrix.md；22 个 MVP surface 无新增。 |
| 19 | 无业务代码修改；仅架构/治理/证据文档 | PASS | 变更文件 = docs/decisions（ADR-006/007/README）、docs/factory_os（addon-dependency-map/configuration-schema/configuration-dependency-graph/progressive-adoption/native-behavior-audit/technical-risks）、开发计划、docs/governance/governance-audit.md；无 odoo-19/ 业务代码、无 scripts 实现改动。 |
| 20 | profile↔manifest dependency-closure（v1.0.3 REGISTERED → 本版 PASS） | PASS | ADR-007 Accepted 目标落地：supply/delivery/dashboard/quality 行已无越级引擎（见 #4–#7）；闭包矩阵 8 行 PASS（#3）。 |
| 21 | **Technical Installation Profile manifest closure（新永久检查，PROFILE_CONTRACTS）** | PASS | 契约落盘 addon-dependency-map §7 + ADR-007 §8 + progressive-adoption 约束：P0 forbidden={stock,mrp,sale_stock,sale_mrp,purchase,purchase_stock,purchase_mrp}、P1 forbidden={mrp,sale_mrp,purchase_mrp}、P2 forbidden=∅；direct+transitive+auto_install 闭包复检 8 addon 目标全部满足；任何 addon 依赖变更强制复检（Phase 1 profile installer / audit tooling 共用同一契约，本轮只写合同不实现）。 |
| 22 | 链接/引用可解析 + git diff --check 干净 | PASS | 相对链接全部指向存在文件；diff 无空白错误；Verification grep 清单（§§ 下方）全部通过。 |
| 23 | **b74a6e4 角色属主落地 = core（角色身份 ≠ 业务 ACL）；可选引擎字段归属与 ADR-007 一致** | PASS | `configuration-schema.md` 权限映射全部角色改为 `factory_os_core.group_*`；`addons/factory_os_core/security/factory_os_security.xml` 13 组（user/manager/admin/owner + 9 functional）全定义于 core；core `models/` 无任何 `stock.*`/`mrp.*`/`product.*` 关系字段（grep 零命中）；「Optional-engine field ownership」规则落地为 core 仅拥有 identity/role identity/capability truth/audit/consistency。 |
| 24 | **core manifest 保持 P0-safe；无 stock/mrp 关系字段；ADR-007 manifest/profile 边界不变** | PASS | `__manifest__.py` depends=[base,mail,web,contacts,product]，无 sale/stock/purchase/mrp（grep 零命中）；8-addon 架构与 PROFILE_CONTRACTS 未改；Phase 1A core kernel 未引入任何可选引擎依赖或业务实现。 |
| 25 | **SETTINGS-AUDIT-01 登记为 Phase 1B 延后验证（实现验证项，非治理矛盾）** | PASS（延后） | core-only profile 有意不存在「既可写、又能通过模块/profile 校验并成功生成 Settings 来源 audit row」的能力（Safe Minimal 语义）。`test_settings_write_reaches_company_validation` 已证明真实 Settings related-field 路径进入 `res.company.write` 且被拒事务不伪造 audit；成功路径断言延后到 Phase 1B（契约登记于 `scripts/audit/phase1/README.md`）。不置 Gate BLOCKED。 |

## Reported contradictions（resolution 更新）

1. **治理级（v1.0.0 已解决）**：reading order 与 precedence 分离；不变量置顶。未回归。
2. **产品-技术映射级（v1.0.1 已解决，ADR-002 澄清）**：平行库存排除。未回归。
3. **能力/引擎架构级（v1.0.2 已解决，ADR-006 Accepted）**：progressive-adoption L10 绝对规则 vs Safe Minimal——经 STOP A/B + E–H 实证，映射为 Technical Installation Profile（单调安装、不卸载/降级、无假关闭）。未回归。
4. **执行面闭包级（v1.0.3 登记 → **v1.0.4 已解决**，ADR-007 Accepted）**：ADR-006 profile 契约 vs 计划 8-addon manifest 闭包（supply→mrp、delivery/dashboard 偏高、purchasing 单调与 Inventory-only substrate 冲突）——经用户 Accept with final architecture 裁决：8-addon 精确 manifest 合同落盘（§2/§6 转正）、purchasing=Workflow、quality=Factory-addon-backed monotonic（独立于 MRP）、Phase 3/4 重划线、PROFILE_CONTRACTS 永久闭包检查。未静默改写，全程 ADR + 审计载体。

## Verification greps（本 commit 执行，全部通过）

```text
supply 目标依赖无 mrp / delivery 无 production·quality·delivery / dashboard 无 supply·production·quality·delivery·stock·mrp
quality 无 mrp / orders 无 stock·sale_stock / purchasing_enabled 非 engine-backed / purchasing requires inventory
quality_enabled 不 requires mrp / process_inspection_enabled requires mrp / Phase 1 无 Supply / Phase 3 无 BOM-MRP 退出 / Phase 4 拥有 BOM-driven shortage
core manifest 无 sale·stock·purchase·mrp / core models 无 stock.*·mrp.*·product.* 关系字段 / 13 角色组全归 factory_os_core
git diff --check 无输出；相对链接全部解析
```

## Gate decision

**Governance Gate: COMPLETE（v1.0.5 re-audit；25 项全部 PASS，无 REGISTERED-OPEN；1 项延后验证 SETTINGS-AUDIT-01 → Phase 1B）。**

- v1.0.4 COMPLETE →（b74a6e4 GOVERNED authority modification）→ STALE →（本 full re-audit v1.0.5）→ **COMPLETE**。
- **Phase 1A: PASS**（create 防线 / audit restrict / 完整安全矩阵 / Settings 真实写路径证明 / 4 探针全 PASS / 40 tests 0 failed 0 error）。Phase 1 overall: IN PROGRESS。**Phase 1B: eligible for authorization（未启动）**。
- 延后验证项 **SETTINGS-AUDIT-01 → Phase 1B**：属实现验证事项（Safe Minimal 语义的自然结果），非治理矛盾，不影响 Gate。
- 不授权任何业务实现；Phase 1B 启动等待用户单独授权。System Invariants 与 UI 权威未改。
