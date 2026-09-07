# Factory OS Progressive Adoption v1.1

状态：**Product and Development Authority**。v1.1（2026-09-07，ADR-006 **Accepted**）修订：capability/addon 语义改为"受控单调引擎安装"、新增 Technical Installation Profiles、`purchasing→inventory`（v1.0 L10 绝对规则按 [ADR-006 Supersedes](../decisions/ADR-006-capability-engine-and-addon-installation.md) 范围失效）。目标用户是 5–20 人、流程尚未标准化的小作坊和轻管理工厂。Factory OS 必须允许其从最小订单看板开始，在不重写历史、不迁移到平行模型的前提下逐步增加采购、库存、正式 MRP、质量和追溯。

## 永久原则

- 工作方式模板只在初始化向导中把答案展开为原子配置；保存后不存储 `management_level`、`maturity_level` 或任何运行时等级。
- 裸安装为 Safe Minimal；Product、Customer、Sales Order、订单级执行状态、Committed Delivery Date、Chatter/Attachments 始终可用。
- 高级能力启用后只对适用的新动作增加 Just-in-Time Gate；不得要求重建旧订单、伪造历史库存或批量创建虚假 MO/QC。
- capability flags 与业务 preset **不假装抑制已安装的原生 Odoo 引擎**；启用引擎型能力可能执行一次受控、可审计、单调的所需原生 addon profile 安装（ADR-006 **Accepted**）。
- 引擎型能力（Inventory、Formal MRP，及进入对应 profile 的 Purchasing、Quality）一旦激活即**单调**：v0.1 不提供正常 `ON → OFF`，不宣称任何 Boolean 能抑制原生引擎。workflow/UI 子能力（operations、移动端、检验类型、QC gates、reports、notifications）仍可自由 `ON ↔ OFF`。
- 简单订单执行属于 `factory_os_orders`；正式 MO/BOM 属于 `factory_os_production`，两者不得混为同一业务对象。

## Technical Installation Profiles（ADR-006 Accepted，2026-09-07）

> Business Preset ≠ Technical Installation Profile。用户只看到 preset（见下 Quick Start）；向导把 `Business Preset → Installation Profile → Atomic Configuration → Role assignment` 逐级翻译。本表是**技术安装面**，不向普通工厂用户暴露 "install stock/mrp addon" 术语。Test G/H/E 是原生契约证据（native-behavior-audit §8）。

| Profile | 原生最小安装（+Odoo 自动桥） | Factory OS addon | capability（单调性） | 无库存/无 MRP 事务承诺 |
|---|---|---:|---|---|
| 0 Order Board / Safe Minimal | `sale` | core + orders | 基础订单执行（不单调） | **成立**（Test G：54 模块，引擎模型不存在，Goods SO 零物流） |
| 1 Inventory & Purchasing | + `stock`（+ `purchase` 当选采购）+ `sale_stock`/`purchase_stock`/`stock_account` 等自动桥 | + supply | `inventory` permanently；`purchasing`=if selected（requires inventory）；二者进入后单调 | 订单看板承诺在此 profile **终止**（A/B/H2） |
| 2 Formal Manufacturing | + `mrp` + `sale_mrp`/`purchase_mrp`/`mrp_account` 自动桥 | + production | `mrp_production` permanently true（单调）；MTO/Manufacture route 受控可用 | MO/RFQ 在 MTO 下 SO 确认即自动产生（E/H3），属正式生产 profile 受控能力 |
| 3 Quality | + factory_os_quality（薄模型，非原生 quality） | + quality | `quality`（requires inventory）单调 | FAIL 必须有受控库存处置 |

约束（v0.1）：

- `purchasing_enabled requires inventory_enabled` —— **无 Purchase-only 模式**（Deferred/Post-MVP）。Inventory ON + Purchasing OFF 允许；反向不允许。
- 升级 = 受控、可审计、单调的引擎安装；**原生引擎卸载/降级 v0.1 不支持**（降级=新建库重放，见 ADR-001）。
- `delivery_enabled` = Factory OS 业务/workflow capability：requires inventory、操作 `stock.picking`、可 `ON ↔ OFF`；**不绑定 Odoo `delivery` addon**（carrier/运费能力 optional，Post-MVP）。
- 引擎若在 Factory OS 管理之外被安装：Phase 1 一致性检查探测现实并阻止配置宣称矛盾状态（引擎在而 flag 关）。

## Safe Minimal raw defaults（Atomic Configuration 默认值）

> 下表面向 **Profile 0**；选中更高 Business Preset 时由向导按上表安装 profile 并把对应行翻 true（单调）。

| Atomic setting | Raw default |
|---|---|
| `sales_enabled` | true |
| `purchasing_enabled` | false |
| `inventory_enabled` | false |
| `mrp_production_enabled` | false |
| `quality_enabled` | false |
| `delivery_enabled` | false |
| `reports_enabled` | false |
| `connector_enabled` | false |
| `operations_enabled` | false |
| `incoming_inspection_enabled` | false |
| `process_inspection_enabled` | false |
| `final_inspection_enabled` | false |
| `incoming_qc_gate` / `final_qc_gate` | false / false |
| `mobile_warehouse_enabled` | false |
| `mobile_operator_enabled` | false |
| `mobile_quality_enabled` | false |

## Wizard：六个现实问题

| Step | 用户看到的问题与答案 | 原子配置映射 |
|---:|---|---|
| 1 | 现在主要想管什么？订单与交期必选；采购和缺料、库存、正式生产单/BOM、质量检验、批次追溯可选 | 分别写 `purchasing_enabled`、`inventory_enabled`、`mrp_production_enabled`、`quality_enabled`；质量通过依赖服务启用库存以保证不合格品受控处置；追溯只进入第 5 步产品提示，不写全局 tracking |
| 2 | 生产怎么记录？主管更新订单进度 / 正式生产单 / 每道工序记录 | manual => MRP false；MO => MRP true + operations false；每道工序 => MRP true + operations true |
| 3 | 库存怎么管？暂时不管 / 只看总库存 / 分仓库库位 | 不管 => inventory false；后两项 => inventory true；simple/advanced UI 优先按仓库与内部库位数量自动推断，不新增永久等级 |
| 4 | 质量怎么管？不单独记录 / 只做出货检查 / 来料+生产+出货 / 正式质量追溯 | 见质量映射表 |
| 5 | 哪些产品需要批次/序列号？现在不设置 / 稍后逐产品配置 | 不写 company flag；完成向导后进入可跳过的产品 tracking 待办 |
| 6 | 谁会使用系统？每个用户可勾订单、采购、库存、生产、质量、交付多个岗位 | 一个 `res.users` 映射到多个内置 `res.groups`；不要求一岗一人或完整部门 |

### 质量答案映射

| Answer | quality | incoming | process | final | final gate | NCR policy |
|---|---:|---:|---:|---:|---:|---|
| 不单独记录 | false | false | false | false | false | `manual` |
| 只做出货检查 | true | false | false | true | false（向导可选开启） | `manual` |
| 来料+生产+出货 | true | true | true | true | false（向导可选开启） | `severity_threshold` |
| 正式质量追溯 | true | true | true | true | true | `severity_threshold` |

“正式质量追溯”同时建议用户逐产品设置 `product.template.tracking`，但不得批量假定所有产品为 Lot。

## 四个 Quick Start preset

Preset 只是向导答案的快捷填充；确认保存时仅写入下表原子配置，运行时不存在 preset 字段。下表是 **Business UX**；向导按下表选中 preset 后先翻译成 [Technical Installation Profile](#technical-installation-profilesadr-006-accepted2026-09-07)（安装对应原生引擎与 Factory OS addon），再写原子配置与角色。质量 preset 一律隐含 `inventory=true`（FAIL 需受控处置）；"订单 + 进销存" 及更高 preset 中 `purchasing` 与 `inventory` 同开（v0.1 无 Purchase-only）。

| Atomic setting | 订单看板 | 订单 + 进销存 | 标准生产 | 质量追溯 |
|---|---:|---:|---:|---:|
| sales | on | on | on | on |
| purchasing | off | on | on | on |
| inventory | off | on | on | on |
| formal MRP | off | off | on | on |
| operations | off | off | off | on |
| quality | off | off | on | on |
| incoming/process/final inspection | off/off/off | off/off/off | off/off/on | on/on/on |
| incoming/final QC gate | off/off | off/off | off/off (final optional) | on/on |
| NCR policy | manual | manual | manual | severity_threshold |
| delivery | off | on | on | on |
| reports | off | off | off | on |
| mobile warehouse/operator/quality | off/off/off | on/off/off | on/on/off | on/on/on |
| product tracking | unchanged (`none` default) | unchanged | unchanged | prompt per product |

## Just-in-Time Validation

最小订单只要求客户、产品、数量；从 Draft 进入 Confirmed/Active Execution 时再要求 `factory_committed_date`。以下普通主数据不得无条件 `required=True`：Customer Code、Supplier Code、英文产品名、Barcode、Product Revision、Default Supplier、Packaging、Payment Terms、Contact Email、Website、Product Photo。

| Action | 当时才校验的必要条件 |
|---|---|
| 激活客户订单 | customer、product、quantity、Committed Delivery Date |
| 创建正式 MO | Odoo 19 Community 经 Phase 0 验证后的产品/BOM/仓库必要字段 |
| tracked product 收发 | 对应 Lot/Serial |
| 出口发货 | 当前出口模式要求的包装和物流字段 |
| Final QC Gate 放行 | Final Inspection PASS |

## 无数据迁移升级路径

```text
订单看板
  sale.order 手工 execution state/progress；无库存/MO/QC事务
      ↓ 开启采购/库存（旧订单不回填 stock.move）
订单 + 进销存
  新的收发动作使用 stock.*；旧订单保留原执行记录
      ↓ 开启正式 MRP（旧订单不生成 MO/BOM 消耗）
标准生产
  仅新建或人工选择转换的适用订单进入 mrp.production
      ↓ 逐产品开启 tracking + 开启质量 Gate
质量追溯
  新事务从真实 stock/mrp/QC 关系形成追溯；历史不伪造
```

升级确认页必须说明“从哪个日期/哪些新单开始执行更严格规则”。任何历史补录都必须是显式、有审计的业务动作，而不是后台迁移。
