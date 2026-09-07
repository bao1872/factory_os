# Factory OS Progressive Adoption v1.0

状态：**Product and Development Authority**。目标用户是 5–20 人、流程尚未标准化的小作坊和轻管理工厂。Factory OS 必须允许其从最小订单看板开始，在不重写历史、不迁移到平行模型的前提下逐步增加采购、库存、正式 MRP、质量和追溯。

## 永久原则

- 工作方式模板只在初始化向导中把答案展开为原子配置；保存后不存储 `management_level`、`maturity_level` 或任何运行时等级。
- 裸安装为 Safe Minimal；Product、Customer、Sales Order、订单级执行状态、Committed Delivery Date、Chatter/Attachments 始终可用。
- 高级能力启用后只对适用的新动作增加 Just-in-Time Gate；不得要求重建旧订单、伪造历史库存或批量创建虚假 MO/QC。
- capability flags 控制 Factory OS 菜单、UI 和流程，不动态安装或卸载 Odoo addons。
- 简单订单执行属于 `factory_os_orders`；正式 MO/BOM 属于 `factory_os_production`，两者不得混为同一业务对象。

## Safe Minimal raw defaults

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

Preset 只是向导答案的快捷填充；确认保存时仅写入下表原子配置，运行时不存在 preset 字段。

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
