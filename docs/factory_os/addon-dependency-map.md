# Factory OS — Addon Dependency Map（Odoo 19 Community Reality）

Date: 2026-09-07（Phase 0 r2；ADR-007 **Accepted** 转正）
Authorities: 开发计划 §3（addon 结构）、§39/§40；ADR-007（Accepted，8-addon 精确 manifest 合同 = Development Authority）；本文件把"manifest 目标合同"与"Community 原生可用性"对照，供 manifest 实现与 Phase 1 验收使用。

## 0. Gate Status（2026-09-07 ADR-007 Accepted 转正）

```
Phase 0 Gate: PASS — awaiting user authorization for Phase 1
原因：ADR-007（docs/decisions/ADR-007-*.md）Accepted——8-addon manifest 目标合同锁定
  （§2 表已转正），dependency-closure 与 ADR-006/Technical Installation Profiles 一致；
  PROFILE_CONTRACTS 闭包契约成为永久架构验证（§7）。
历史：dependency-closure STOP → BLOCKED（2973bb4）→ 用户 Accept ADR-007 with final architecture → 转正。
```

## 1. 审计实例事实（Evidence）

- 代码库 `odoo-19/addons`：638 个 addon；`odoo/release.py:15` = 19.0 FINAL；无 enterprise。
- 审计数据库 `factory_phase0_r2` 安装 72 模块（`sale_management,stock,purchase,mrp` 初始安装后依赖自动带入）。关键原生模块实测可用：

```
sale sale_management sale_stock sale_mrp sale_purchase sale_purchase_stock
purchase purchase_stock purchase_mrp mrp mrp_account stock stock_account
stock_delivery delivery sales_team product contacts（可用，未装）mail base web
```

- 实测 **不存在**：`quality`、`quality_control`、`quality_mrp`、`mrp_workorder`（已并入 mrp）、`procurement`（procurement.group 移除）。

## 2. 8 个 Factory OS addon manifest 目标合同（ADR-007 Accepted = Development Authority）→ 原生可用性

> 以下依赖列为**精确目标**（写入 `__manifest__.py` 的最终依赖），非建议。禁止 IDE 重新设计；禁止任何 addon 在目标之外增删业务引擎依赖。闭包校验见 §6/§7。

| Factory OS addon | 目标 manifest 依赖（ADR-007 §3） | 硬依赖禁项（ADR-007 §3） | 原生状态（实测） | 结论 |
|---|---|---|---|---|
| factory_os_core | base/mail/web/contacts/product | sale/purchase/stock/mrp | 全部存在（contacts 在 addons/，未被审计库安装但可装） | PASS |
| factory_os_orders | factory_os_core + sale | sale_stock/stock/purchase/mrp | sale_stock 存在（引擎级库已装）；orders 只含基础订单执行（Profile 0 真实安装面=仅 sale，Test G）；route/库存联动由 supply 扩展 sale.order、delivery 扩展 stock.picking 提供 | PASS |
| factory_os_supply | factory_os_core + factory_os_orders + stock + purchase + **sale_stock** + **purchase_stock** | **mrp / sale_mrp / purchase_mrp** | 全部存在；sale_stock/purchase_stock 为显式 bridge API 依赖（非新增 profile 层级：P1 substrate 本含 sale+stock+purchase，Odoo 自动装桥；显式声明锁定加载顺序与 API 契约） | PASS（CONFLICT 已解） |
| factory_os_production | factory_os_core + factory_os_orders + factory_os_supply + stock + mrp + sale_mrp + purchase_mrp | —（自身属主） | mrp 为 Community 模块，含 mrp.bom/production/workorder/workcenter（实测 EXIST） | PASS |
| factory_os_quality | factory_os_core + factory_os_orders + stock | **mrp / factory_os_production / factory_os_supply / purchase / quality / quality_control / quality_mrp** | 无原生 quality 可依赖（实测 False）→ 两薄模型 factory.quality.inspection/ncr；Process inspection 仅 `mrp.production in registry` 时条件开放 | PASS（PENDING 已解：显式无 mrp，Incoming/Final 不强制 MRP） |
| factory_os_delivery | factory_os_core + factory_os_orders + stock | **factory_os_production / factory_os_quality / mrp / delivery** | delivery 与 stock_delivery 存在（未装）；真相对象 stock.picking；production/quality 集成仅条件读取（registry 守卫） | PASS（CONFLICT 已解） |
| factory_os_dashboard | factory_os_core + factory_os_orders | **factory_os_supply / factory_os_production / factory_os_quality / factory_os_delivery / stock / mrp** | 不引原生业务模块；可选瓦片 registry 守卫（`stock.picking`/`mrp.production`/`factory.quality.inspection` in registry） | PASS（CONFLICT 已解） |
| factory_os_connector | factory_os_core + factory_os_orders（最低） | 静态依赖 Supply/MRP/Quality/Delivery | 复用 mail/bus/web 基础设施；Phase 8 仅按 connector 设计加纯技术依赖 | PASS |

## 3. Community 现实缺口（影响建模）

| 原计划假设 | Community 19 实测 | 对 Factory OS 的影响 |
|---|---|---|
| 扩展 `quality.*`（PRD §36 复用清单含 quality.*；开发计划 §20 第一路径） | 无任何 quality addon（Enterprise-only） | QC 映射冻结为 THIN CUSTOM（model-mapping.md #14/#15）；成品质检 Gate（不变量 #6）须建在自建 inspection 模型之上 |
| 复用"补货 procurement 组"思路 | `procurement.group` 模型移除 | 原生补货仍经 stock.rule/orderpoint 工作（测试 C3）；Factory OS 缺料/追溯为 DERIVED，不依赖旧 procurement API |
| workorder 独立模块 | `mrp_workorder` 并入 `mrp`，模型仍为 mrp.workorder | operations_enabled 依赖仍成立；manifest 不需列 mrp_workorder |
| 持久盘点单（stock.inventory 风格） | 无 stock.inventory/stock.count 模型；盘点改为 stock.quant + 向导（stock.request_count / stock.inventory.adjustment.name 等，stock/wizard/） | 盘点入口按原生 19 向导设计；不写平行盘点表 |
| 产品 type='product' | 枚举仅 consu/service/combo（product_template.py:54-65）；"可存储物" = consu + `is_storable`（stock/models/product.py:829） | 配置/导入/UI 全部改用 is_storable 语义（已同步 configuration 权威无需改——配置文档未用 type='product'） |

## 4. 桥接模块自动安装效应（必须知情）

审计库同时安装了 sale+mrp+purchase+stock 后，以下桥接模块自动带入并**立即生效**：

- `sale_stock`：SO 确认→ `_action_launch_stock_rule`（sale_order.py:213-215）→ 生成 delivery picking/stock.move（测试 A）。
- `purchase_stock`：PO 确认→ incoming picking/stock.move（测试 B）。
- `purchase_mrp` / `sale_mrp`：产品带 Manufacture/Buy 路线时补货可生成 MO（测试 C）；仓库默认含 Manufacture、Buy 两条路线（实测 ALL_ROUTES）。

**含义（ADR-006 + ADR-007 Accepted 更新）**：能力开关与原生引擎的关系 = **Technical Installation Profile**（能力图，progressive-adoption v1.2）——引擎型能力（库存/正式 MRP）执行受控、可审计、单调的原生 addon profile 安装（含 auto_install 桥接）；`quality`=Factory-addon-backed monotonic（requires inventory、NOT requires mrp）；`purchasing`/`delivery`=Workflow capability（requires inventory、ON↔OFF、不宣称原生 addon 存在）。v0.1 无正常 ON→OFF（workflow 除外）、无原生引擎卸载/降级；workflow/UI 子能力只控 Factory OS UI/流程/字段可见性。Safe Minimal（Profile 0）物理上不装这些引擎与桥接（Test G：模型不存在），因此不存在"已装引擎而 flag 关"的假关闭状态；引擎若绕过 Factory OS 被安装，Phase 1 一致性检查负责探测并阻止矛盾配置（详见 configuration-dependency-graph / configuration-schema）。

## 5. manifest 设计约束（ADR-006 + ADR-007 Accepted 后生效）

1. **保持 8-addon 架构**：不新增任何第 9 个 Factory OS bridge addon（`factory_os_orders_stock` 之类被裁决否决）。
2. 8 个 addon 的 manifest 依赖 = **ADR-007 §3 精确目标**（§2 表），不允许 IDE 重新设计模块边界/依赖列表。
3. `factory_os_quality` 不得在 manifest 声明不存在的 quality* 依赖；保持两薄模型（factory.quality.inspection/ncr）；**硬依赖禁 mrp**，Process inspection 仅 registry 守卫条件开放。
4. `factory_os_delivery`：最低依赖 `stock` + core + orders；**不依赖也不主动安装 Odoo `delivery` addon**（carrier/运费能力 optional，Post-MVP）；硬依赖禁 production/quality/mrp。
5. `factory_os_dashboard`：最低 core + orders；registry 守卫可选瓦片，base code 不得静态引用可选模块模型。
6. `factory_os_supply`：显式声明 sale_stock/purchase_stock 为 bridge API 依赖；**禁 mrp/sale_mrp/purchase_mrp**。
7. 安装由向导按 Technical Installation Profile（progressive-adoption v1.2 能力图）映射原生引擎与 factory addon：Inventory/MRP 引擎型单调（进入后不卸载/不降级），升级只增；`purchasing` = Workflow capability（requires inventory，ON↔OFF）；`quality` = Factory-addon-backed monotonic（requires inventory，NOT requires mrp）。v0.1 无 Purchase-only。
8. 若未来工厂启用 Enterprise quality addon，需新增映射版本（本 Phase 0 冻结 Community）。

## 6. Dependency-Closure Matrix（ADR-007 Accepted 转正）

闭包法则（原生 manifest 源码级）：每行 = 按 **ADR-007 §3 目标依赖**逐层解析 `depends` + 自动挂载 `auto_install` 桥（sale_stock/stock_account/purchase_stock/sale_mrp/mrp_account/purchase_mrp/sale_purchase）。判定不变量：**属于 Profile N 的 addon 安装不得强制带入只属于 Profile N+1 的原生引擎**（Quality/Delivery/Dashboard/Connector 为 P1 substrate 上的独立扩展，不构成新 profile 层级）。

| Factory addon | 直接 Factory 依赖 | 直接原生依赖（目标） | 传递闭包后原生引擎面（含自动桥） | 允许最低 Technical Profile | forbidden 检查（PROFILE_CONTRACTS） | 判定 |
|---|---|---|---|---|---|---|
| factory_os_core | — | base/product/mail/web/contacts | 无 stock/purchase/mrp | Profile 0 | P0 forbidden={stock,purchase,mrp,…}：无泄漏 | PASS |
| factory_os_orders | core | sale | sale→account；无 stock（无 sale_stock） | Profile 0 | P0：无泄漏 | PASS |
| factory_os_supply | core+orders | stock+purchase+sale_stock+purchase_stock | {stock, purchase, account} + sale_stock/stock_account/purchase_stock/sale_purchase（显式） | Profile 1 | P1 forbidden={mrp,sale_mrp,purchase_mrp}：闭包无 mrp | PASS |
| factory_os_production | core+orders+supply | stock+mrp+sale_mrp+purchase_mrp | {stock, purchase, mrp, account} + 全部自动桥 | Profile 2 | P2 forbidden=∅ | PASS |
| factory_os_quality | core+orders | stock | {stock}（+barcodes/digest 支持模块）；无 mrp/purchase | Profile 1 substrate（独立扩展，非 MRP 必经层） | 无 mrp/sale_mrp/purchase_mrp 硬依赖 | PASS |
| factory_os_delivery | core+orders | stock | {stock}；无 production/quality/mrp/delivery | Profile 1 substrate（独立扩展） | 无高 profile 泄漏 | PASS |
| factory_os_dashboard | core+orders | — | 无引擎 | Profile 0 起可用 | 不静态依赖任何业务 addon | PASS |
| factory_os_connector | core+orders | mail/bus/web（技术） | 无引擎 | 兼容全部 | Phase 8 按设计加纯技术依赖 | PASS |

**结论**：8 行全部 PASS。原 CONFLICT（supply→mrp / delivery→production+quality+delivery / dashboard→全内部 / quality 含糊 / purchasing 单调分类）在 ADR-007 §3/§4/§5 目标下全部闭合。purchase substrate 常驻 Inventory-only 库是**有意契约**（`purchasing_enabled`=Workflow，不宣称 addon 存在；普通用户不获原生 purchase groups/菜单，Phase 1 安全收紧）。

## 7. Profile Dependency-Closure Permanent Contract（ADR-007 §8，Development Authority）

此契约对**每个 addon 依赖变更**强制生效：direct + transitive + auto_install bridges 不得包含所属 profile forbidden 的业务引擎。规范化契约（Phase 1 profile installer / audit tooling 与 governance-audit 永久检查共用同一契约；本轮只写合同，不实现）：

```python
def verify_profile_closure(profile_contract, installed_modules):
    forbidden = (
        set(installed_modules)
        & set(profile_contract["forbidden_engines"])
    )
    assert not forbidden, (
        f"Profile {profile_contract['name']} leaked "
        f"forbidden engines: {sorted(forbidden)}"
    )

PROFILE_CONTRACTS = {
    "P0": {
        "required_engines": {"sale"},
        "forbidden_engines": {
            "stock", "mrp", "sale_stock", "sale_mrp",
            "purchase", "purchase_stock", "purchase_mrp",
        },
    },
    "P1": {
        "required_engines": {
            "sale", "stock", "purchase",
            "sale_stock", "purchase_stock",
        },
        "forbidden_engines": {
            "mrp", "sale_mrp", "purchase_mrp",
        },
    },
    "P2": {
        "required_engines": {
            "sale", "stock", "purchase", "mrp",
            "sale_stock", "purchase_stock",
            "sale_mrp", "purchase_mrp",
        },
        "forbidden_engines": set(),
    },
}
```

允许适配：仅 Odoo 自动安装的**非业务引擎**会计/支持模块（`account`/`stock_account` 等，P1/P2 自动面本已含）。**禁止**因"Odoo 会自动装"删除 forbidden 业务引擎条目；若精确原生依赖使契约不可能：**STOP 并报告证据**。
