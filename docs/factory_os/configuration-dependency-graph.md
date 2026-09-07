# Factory OS Configuration Dependency Graph v1.0

状态：**Development Authority**。本文件定义设置可见性、启停顺序和已有数据保护策略。

## 统一变更策略

- `BLOCK`：变更会破坏正确性、绕过 Gate 或使已有业务数据失去有效处理路径。事务回滚，界面显示具体阻塞记录数量及处理入口，不静默级联。
- `AUTO_DISABLE`：仅影响 UI 或可选能力，允许自动关闭/恢复安全默认值；父项与所有从属项在同一事务写入审计。
- `HIDE_KEEP`：父能力关闭时隐藏从属配置但保留其值；再次启用恢复原值，期间不消费该值。
- `ENABLE_REQUIRED`：启用父能力时自动启用其基础依赖并在确认页列出；用户取消则整个事务不保存。

所有依赖检查由 `factory_os_core.configuration_service` 执行，设置页、初始化向导、导入和 RPC 必须调用同一服务。

`factory_execution_state`、`factory_manual_progress`、`factory_estimated_completion_date` 与订单 Chatter/Attachments 属于基础订单能力，不依赖 `mrp_production_enabled`。关闭正式 MRP 不得隐藏或删除这些字段。

## Graph

```text
inventory_enabled                      <- engine-backed monotonic (ADR-006 Accepted)
  requires ENABLE_REQUIRED: native Inventory profile (stock engine 安装)
  monotonic: 进入后 ON->OFF 不支持 (BLOCK disable)；禁止"引擎在而 flag 关"的假关闭状态

purchasing_enabled                     <- engine-backed monotonic (ADR-006 Accepted)
  requires ENABLE_REQUIRED: inventory_enabled (v0.1 无 Purchase-only；Inventory ON + Purchasing OFF 允许)
  monotonic: 进入后 ON->OFF 不支持 (BLOCK disable)
  被 PR/来料检验引用；block parent disable when: open PR / open incoming inspection exists

mrp_production_enabled                 <- engine-backed monotonic (ADR-006 Accepted)
  requires ENABLE_REQUIRED: inventory_enabled, product/BOM capability, native MRP profile (mrp engine 安装)
  monotonic: 进入后 ON->OFF 不支持 (BLOCK disable)
  controls AUTO_DISABLE(workflow 子项): mobile_operator_enabled, operations_enabled, reporting_mode
  blocks disable when: active MO/workorder exists
  MTO 语义: MRP profile 下 MTO+Manufacture 产品 SO 确认自动建 MO (Test E/H3)，属受控能力，非 flag 可关

delivery_enabled                       <- 业务层能力，可 ON<->OFF (ADR-006 Accepted)
  requires ENABLE_REQUIRED: inventory_enabled (操作 stock.picking)
  does NOT require/install Odoo delivery addon (carrier/运费 optional, Post-MVP)
  controls HIDE_KEEP: shipment_mode, packaging_fields, delivery_confirmation_mode
  blocks disable when: open outbound picking exists

quality_enabled                        <- monotonic once Profile 3 installed (ADR-006 Accepted)
  requires ENABLE_REQUIRED: inventory_enabled
  engine = factory_os_quality 薄模型 (Community 无原生 quality，不引入 Enterprise 依赖)
  controls: incoming_inspection_enabled, process_inspection_enabled,
            final_inspection_enabled, incoming_qc_gate, final_qc_gate,
            ncr_creation_policy, reject_inventory_disposition
  blocks disable when: open inspection, open NCR, quarantined/rework quantity exists

incoming_qc_gate
  requires: quality_enabled, purchasing_enabled, incoming_inspection_enabled
  blocks disable when: receipt is waiting for inspection disposition

final_qc_gate
  requires: quality_enabled, final_inspection_enabled
  blocks disable when: quantity is waiting for final inspection or shipment release

purchase_request_mode
  visible_if: purchasing_enabled
  controls AUTO_DISABLE: purchase_approval_mode, purchase_approver_id/group_id
  blocks parent disable when: open purchase request exists

operations_enabled, reporting_mode, mobile_operator_enabled
  visible_if: mrp_production_enabled

mobile_warehouse_enabled
  requires: inventory_enabled

mobile_quality_enabled
  requires: quality_enabled

barcode_requirement_warehouse
  visible_if: inventory_enabled AND mobile_warehouse_enabled

barcode_requirement_operator
  visible_if: mrp_production_enabled AND mobile_operator_enabled

reports_enabled
  controls AUTO_DISABLE: report_module_keys
  each report key visible_if: corresponding business module enabled

connector_enabled
  requires before activation: connector_endpoint, connector_workspace_key,
                              connector_credential, nonempty shared-field allowlist
  controls HIDE_KEEP: connector field policy
```

## Machine-readable rule table

| key | requires | visible_if | incompatible_with | parent disabled behavior |
|---|---|---|---|---|
| `inventory_enabled` | native Inventory profile（stock） | always | engine-installed-but-flag-off | **monotonic BLOCK disable（engine-backed，ADR-006）**；无 ON→OFF |
| `purchasing_enabled` | `inventory_enabled` | always | engine-installed-but-flag-off | **monotonic BLOCK disable（engine-backed）**；BLOCK while open PR / open incoming inspection |
| `mrp_production_enabled` | `inventory_enabled`, product/BOM, native MRP profile | always | engine-installed-but-flag-off | **monotonic BLOCK disable（engine-backed）**；workflow 子项 AUTO_DISABLE；BLOCK while active MO/workorder |
| `delivery_enabled` | `inventory_enabled`（stock.picking） | always | — | 业务层可 ON↔OFF：BLOCK with open outbound; otherwise HIDE_KEEP children；不安装 Odoo delivery addon |
| `quality_enabled` | `inventory_enabled`（factory_os_quality 薄模型） | always | engine-installed-but-flag-off | **monotonic BLOCK disable once Profile 3 installed**；BLOCK while open inspection/NCR/disposition |
| `incoming_inspection_enabled` | `quality_enabled`, `purchasing_enabled` | both parents | — | BLOCK with open inspection; otherwise AUTO_DISABLE |
| `process_inspection_enabled` | `quality_enabled`, `mrp_production_enabled` | both parents | — | BLOCK with open inspection; otherwise AUTO_DISABLE |
| `final_inspection_enabled` | `quality_enabled` | quality | — | BLOCK while final gate or open inspection exists |
| `incoming_qc_gate` | `quality_enabled`, `incoming_inspection_enabled`, `purchasing_enabled` | all requirements | — | BLOCK with gated receipts; otherwise AUTO_DISABLE |
| `final_qc_gate` | `quality_enabled`, `final_inspection_enabled` | all requirements | — | BLOCK with unreleased finished goods; otherwise AUTO_DISABLE |
| `purchase_request_mode` | `purchasing_enabled` | purchasing | — | BLOCK with open PR; otherwise set `off` |
| `purchase_approval_mode` | `purchasing_enabled` | PR=`approval_required` | `none` when approval required | set `none`, clear approver |
| `operations_enabled` | `mrp_production_enabled` | formal MRP | — | BLOCK with active workorder; otherwise false |
| `reporting_mode` | `mrp_production_enabled` | formal MRP | — | set `manager` |
| `mobile_operator_enabled` | `mrp_production_enabled` | formal MRP | — | false |
| `mobile_warehouse_enabled` | `inventory_enabled` | inventory | — | false |
| `mobile_quality_enabled` | `quality_enabled` | quality | — | false |
| `barcode_requirement_operator` | formal MRP + mobile operator | both | — | set `none` |
| `barcode_requirement_warehouse` | inventory + mobile warehouse | both | — | set `none` |
| `reject_inventory_disposition=return_supplier` | purchasing + inventory + quality | requirements | purchasing off | BLOCK while return disposition records open |
| `reject_inventory_disposition=rework` | formal MRP + inventory + quality | requirements | MRP off | BLOCK while rework records open |
| `delivery_confirmation_mode=tracking` | delivery | delivery | MVP v0.1 | value visible but disabled with “Post-MVP” |
| `report_module_keys[]` | corresponding module | reports + module | disabled module | AUTO_DISABLE key |
| `connector_enabled` | endpoint + workspace + credential + allowlist | integration settings | missing requirement | BLOCK activation |

## Error contract

阻止变更时返回业务错误，格式固定：`无法关闭{模块}：仍有{count}条{record_type}依赖此能力。请先完成或取消这些记录。` 同时提供过滤后的 Odoo action。自动级联时，保存确认页列出全部将改变的字段；确认后写一条父审计记录和逐字段明细。
