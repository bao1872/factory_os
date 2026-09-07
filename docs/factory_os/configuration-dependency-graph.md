# Factory OS Configuration Dependency Graph v1.0

状态：**Development Authority**。本文件定义设置可见性、启停顺序和已有数据保护策略。

## 统一变更策略

- `BLOCK`：变更会破坏正确性、绕过 Gate 或使已有业务数据失去有效处理路径。事务回滚，界面显示具体阻塞记录数量及处理入口，不静默级联。
- `AUTO_DISABLE`：仅影响 UI 或可选能力，允许自动关闭/恢复安全默认值；父项与所有从属项在同一事务写入审计。
- `HIDE_KEEP`：父能力关闭时隐藏从属配置但保留其值；再次启用恢复原值，期间不消费该值。
- `ENABLE_REQUIRED`：启用父能力时自动启用其基础依赖并在确认页列出；用户取消则整个事务不保存。

所有依赖检查由 `factory_os_core.configuration_service` 执行，设置页、初始化向导、导入和 RPC 必须调用同一服务。

## Graph

```text
production_enabled
  requires ENABLE_REQUIRED: inventory_enabled, product/BOM capability
  controls AUTO_DISABLE: mobile_operator_enabled, operations_enabled, reporting_mode
  blocks disable when: active MO/workorder exists

delivery_enabled
  requires ENABLE_REQUIRED: inventory_enabled
  controls HIDE_KEEP: shipment_mode, packaging_fields, delivery_confirmation_mode
  blocks disable when: open outbound picking exists

quality_enabled
  controls: incoming_inspection_enabled, process_inspection_enabled,
            final_inspection_enabled, incoming_qc_gate, final_qc_gate,
            ncr_creation_policy, reject_inventory_disposition
  blocks disable when: open inspection, open NCR, quarantined/rework quantity exists

incoming_qc_gate
  requires: quality_enabled, purchasing_enabled, incoming_inspection_enabled
  blocks disable when: receipt is waiting for inspection disposition

final_qc_gate
  requires: quality_enabled, production_enabled, final_inspection_enabled
  blocks disable when: quantity is waiting for final inspection or shipment release

purchase_request_mode
  visible_if: purchasing_enabled
  controls AUTO_DISABLE: purchase_approval_mode, purchase_approver_id/group_id
  blocks parent disable when: open purchase request exists

operations_enabled, reporting_mode, mobile_operator_enabled
  visible_if: production_enabled

mobile_warehouse_enabled
  requires: inventory_enabled

mobile_quality_enabled
  requires: quality_enabled

barcode_requirement_warehouse
  visible_if: inventory_enabled AND mobile_warehouse_enabled

barcode_requirement_operator
  visible_if: production_enabled AND mobile_operator_enabled

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
| `production_enabled` | `inventory_enabled`, product/BOM capability | always | — | BLOCK with active MO/workorder; otherwise AUTO_DISABLE children |
| `delivery_enabled` | `inventory_enabled` | always | — | BLOCK with open outbound; otherwise HIDE_KEEP children |
| `incoming_inspection_enabled` | `quality_enabled`, `purchasing_enabled` | both parents | — | BLOCK with open inspection; otherwise AUTO_DISABLE |
| `process_inspection_enabled` | `quality_enabled`, `production_enabled` | both parents | — | BLOCK with open inspection; otherwise AUTO_DISABLE |
| `final_inspection_enabled` | `quality_enabled`, `production_enabled` | both parents | — | BLOCK while final gate or open inspection exists |
| `incoming_qc_gate` | `quality_enabled`, `incoming_inspection_enabled`, `purchasing_enabled` | all requirements | — | BLOCK with gated receipts; otherwise AUTO_DISABLE |
| `final_qc_gate` | `quality_enabled`, `final_inspection_enabled`, `production_enabled` | all requirements | — | BLOCK with unreleased finished goods; otherwise AUTO_DISABLE |
| `purchase_request_mode` | `purchasing_enabled` | purchasing | — | BLOCK with open PR; otherwise set `off` |
| `purchase_approval_mode` | `purchasing_enabled` | PR=`approval_required` | `none` when approval required | set `none`, clear approver |
| `operations_enabled` | `production_enabled` | production | — | BLOCK with active workorder; otherwise false |
| `reporting_mode` | `production_enabled` | production | — | set `manager` |
| `mobile_operator_enabled` | `production_enabled` | production | — | false |
| `mobile_warehouse_enabled` | `inventory_enabled` | inventory | — | false |
| `mobile_quality_enabled` | `quality_enabled` | quality | — | false |
| `barcode_requirement_operator` | production + mobile operator | both | — | set `none` |
| `barcode_requirement_warehouse` | inventory + mobile warehouse | both | — | set `none` |
| `reject_inventory_disposition=return_supplier` | purchasing + inventory + quality | requirements | purchasing off | BLOCK while return disposition records open |
| `reject_inventory_disposition=rework` | production + inventory + quality | requirements | production off | BLOCK while rework records open |
| `delivery_confirmation_mode=tracking` | delivery | delivery | MVP v0.1 | value visible but disabled with “Post-MVP” |
| `report_module_keys[]` | corresponding module | reports + module | disabled module | AUTO_DISABLE key |
| `connector_enabled` | endpoint + workspace + credential + allowlist | integration settings | missing requirement | BLOCK activation |

## Error contract

阻止变更时返回业务错误，格式固定：`无法关闭{模块}：仍有{count}条{record_type}依赖此能力。请先完成或取消这些记录。` 同时提供过滤后的 Odoo action。自动级联时，保存确认页列出全部将改变的字段；确认后写一条父审计记录和逐字段明细。
