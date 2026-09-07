# Factory OS 实现级配置 Schema v1.0

状态：**Development Authority**。本文件锁定字段名、存储、类型、合法值、默认值、约束、权限、依赖行为、审计和消费方。开发不得自行改名或扩充 selection；变更必须先更新本文件与配置矩阵。

约定：公司级字段存于 `res.company`，`res.config.settings` 只提供同名 related proxy（`readonly=False`）；产品级字段存于 `product.template`；角色和用户范围使用 Odoo group/record rule，不复制为布尔偏好。所有公司级配置由 `factory_os_core.group_factory_os_admin` 或表中更窄的经理组编辑，并写入 `factory.config.audit`。`selection` 的左侧英文值为数据库值，右侧中文仅为 UI 标签。

权限简称固定映射：Admin=`factory_os_core.group_factory_os_admin`，Factory OS Manager=`factory_os_core.group_factory_os_manager`，Sales Manager=`factory_os_orders.group_factory_sales_manager`，Purchase Manager=`factory_os_supply.group_factory_purchase_manager`，Inventory Manager=`factory_os_supply.group_factory_inventory_manager`，Product Manager=`factory_os_core.group_factory_product_manager`，Production Manager=`factory_os_production.group_factory_production_manager`，Quality Manager=`factory_os_quality.group_factory_quality_manager`，Delivery Manager=`factory_os_delivery.group_factory_delivery_manager`，Integration Admin=`factory_os_connector.group_factory_integration_admin`。consumer 中的 `orders/supply/production/quality/delivery/dashboard/connector/mobile/core` 分别指对应 `factory_os_*` addon 内的 service/model；实现文件路径在 Phase 0 model mapping 后冻结。

## 工厂与模块

| technical_key | Odoo storage | type / selection | exact default | constraints | group | dependency / disabled behavior | audit | consumer |
|---|---|---|---|---|---|---|---|---|
| `factory_name` | `res.company.name` | Char | 安装时现有公司名 | required | Admin | 无 | mail tracking + config audit | core/document reports |
| `factory_logo` | `res.company.logo` | Binary | 现有公司 Logo/空 | image size follows Odoo | Admin | 无 | config audit, store checksum only | core/report layout |
| `factory_address` | `res.company.partner_id` address fields | Native address | 现有公司地址/空 | Odoo partner constraints | Admin | 无 | mail tracking | core/delivery |
| `factory_region` | `res.company.country_id/state_id` | Many2one | `CN` when blank | valid country/state relation | Admin | 无 | config audit | core/localization |
| `factory_timezone` | `res.company.partner_id.tz` | Selection | `Asia/Shanghai` | valid Odoo timezone | Admin | 无 | config audit | all datetime services |
| `factory_language` | `res.company.partner_id.lang` | Selection | `zh_CN` | installed language only | Admin | 无 | config audit | UI/reports |
| `factory_currency_id` | `res.company.currency_id` | Many2one(`res.currency`) | `CNY` for new CN company | obey posted accounting constraints | Admin | 无；有过账数据时按 Odoo 阻止 | mail tracking | sales/purchase/reports |
| `weight_uom_id` | `res.company.factory_weight_uom_id` | Many2one(`uom.uom`) | kg | weight category only | Admin | 无 | config audit | product/delivery |
| `length_uom_id` | `res.company.factory_length_uom_id` | Many2one(`uom.uom`) | mm | length category only | Admin | 无 | config audit | product/packaging |
| `default_warehouse_id` | `res.company.factory_default_warehouse_id` | Many2one(`stock.warehouse`) | company first active warehouse | same company, active | Admin | inventory required；有活动单据时阻止删除引用 | config audit | supply/production/delivery |
| `warehouse_ids` / `location_ids` | native `stock.warehouse` / `stock.location` | Native records | one warehouse + standard locations | company consistency; valid hierarchy/usages | Inventory Manager | requires inventory；有库存/移动引用时按 Odoo 阻止删除 | mail tracking | stock.* |
| `sales_enabled` | `res.company.factory_sales_enabled` | Boolean | true | — | Admin | base capability | config audit | orders/menu service |
| `purchasing_enabled` | `res.company.factory_purchasing_enabled` | Boolean | true | — | Admin | 被 PR/来料检验引用；破坏性关闭时阻止 | config audit | supply/menu service |
| `inventory_enabled` | `res.company.factory_inventory_enabled` | Boolean | true | — | Admin | production/delivery/tracking requires；存在依赖时阻止关闭 | config audit | stock/menu service |
| `production_enabled` | `res.company.factory_production_enabled` | Boolean | true | — | Admin | requires inventory + product/BOM；启用时自动启用二者，关闭时自动关闭纯 UI 从属项 | config audit | production/menu service |
| `quality_enabled` | `res.company.factory_quality_enabled` | Boolean | true | — | Admin | gates/inspection/NCR requires；存在开放检验或隔离库存时阻止关闭 | config audit | quality/menu service |
| `delivery_enabled` | `res.company.factory_delivery_enabled` | Boolean | true | — | Admin | requires inventory；存在未完成发货时阻止关闭 | config audit | delivery/menu service |
| `reports_enabled` | `res.company.factory_reports_enabled` | Boolean | true | — | Admin | 关闭仅隐藏报表入口 | config audit | dashboard/report menu |
| `connector_enabled` | `res.company.factory_connector_enabled` | Boolean | false | credentials and endpoint required before activation | Integration Admin | 无；关闭停止新同步，不删除日志/凭据 | config audit | connector.sync_service |

## 订单与采购

| technical_key | Odoo storage | type / selection | exact default | constraints | group | dependency / disabled behavior | audit | consumer |
|---|---|---|---|---|---|---|---|---|
| `quotation_enabled` | `res.company.factory_quotation_enabled` | Boolean | true | — | Sales Manager | visible_if sales | config audit | orders.menu_service |
| `show_planned_completion_date` | `res.company.factory_show_planned_completion_date` | Boolean | true | only presentation | Admin | visible_if sales or production；父项关闭时自动 false | config audit | orders/views |
| `health_warning_days` | `res.company.factory_health_warning_days` | Integer | 7 | `>= 0` and `warning >= critical` | Factory OS Manager | visible_if sales | config audit | orders.health_service |
| `health_critical_days` | `res.company.factory_health_critical_days` | Integer | 3 | `>= 0` and `critical <= warning` | Factory OS Manager | visible_if sales | config audit | orders.health_service |
| `fulfillment_chain_display` | `res.company.factory_fulfillment_chain_display` | Selection: `risk_only`/仅风险, `always`/始终, `collapsed`/默认折叠 | `risk_only` | bounded enum | Factory OS Manager | visible_if sales | config audit | orders.form_controller |
| `purchase_request_mode` | `res.company.factory_purchase_request_mode` | Selection: `off`/关闭, `simple`/简易, `approval_required`/需审批 | `off` | bounded enum | Purchase Manager | requires purchasing；父项关闭时自动 `off`，已有开放 PR 时阻止关闭采购 | config audit | supply.purchase_request_service |
| `purchase_approval_mode` | `res.company.factory_purchase_approval_mode` | Selection: `none`/无, `single_user`/一人, `role`/指定角色 | `none` | no multilevel | Purchase Manager | visible_if purchasing；PR=`approval_required` 时不得为 `none` | config audit | supply.purchase_approval_service |
| `purchase_approver_id` | `res.company.factory_purchase_approver_id` | Many2one(`res.users`) | empty | active internal user, same company | Purchase Manager | required_if approval=`single_user`；模式变化自动清空 | config audit | supply.purchase_approval_service |
| `purchase_approver_group_id` | `res.company.factory_purchase_approver_group_id` | Many2one(`res.groups`) | Purchase Manager group | allowlisted Factory OS groups only | Admin | required_if approval=`role`；模式变化自动清空 | config audit | supply.purchase_approval_service |
| `po_late_grace_days` | `res.company.factory_po_late_grace_days` | Integer | 0 | `>= 0` | Purchase Manager | visible_if purchasing | config audit | supply.po_risk_service |
| `eta_warning_days` | `res.company.factory_eta_warning_days` | Integer | 0 | `>= 0`; 0 means warn on adverse ETA change | Purchase Manager | visible_if purchasing | config audit | supply.po_risk_service |

`sale.order.factory_requested_date` 与 `sale.order.factory_confirmed_date` 为 required Datetime 业务字段，不是配置项；计划完成日期不得代替二者。

## 库存与生产

| technical_key | Odoo storage | type / selection | exact default | constraints | group | dependency / disabled behavior | audit | consumer |
|---|---|---|---|---|---|---|---|---|
| `product_tracking` | `product.template.tracking` | Native Selection: `none`, `lot`, `serial` | `none` | Odoo native stock constraints | Product/Inventory Manager | product-level only；有库存移动后按 Odoo 安全规则限制变更 | mail tracking | stock/mrp/traceability |
| `reordering_min_qty` | `stock.warehouse.orderpoint.product_min_qty` | Float | 0 | `>= 0` | Inventory Manager | requires inventory | mail tracking | stock.replenishment |
| `reordering_max_qty` | `stock.warehouse.orderpoint.product_max_qty` | Float | 0 | `>= min_qty` | Inventory Manager | requires inventory | mail tracking | stock.replenishment |
| `safety_stock_qty` | `stock.warehouse.orderpoint.factory_safety_stock_qty` | Float | 0 | `>= 0` | Inventory Manager | requires inventory | mail tracking | supply.shortage_service |
| `inventory_count_mode` | `res.company.factory_inventory_count_mode` | Selection: `normal`, `blind` | `normal` | bounded enum | Inventory Manager | requires inventory；关闭库存时自动恢复 `normal` | config audit | stock.count_views |
| `operations_enabled` | `res.company.factory_operations_enabled` | Boolean | true | — | Production Manager | requires production；存在活动 workorder 时阻止关闭 | config audit | production.workorder_service |
| `reporting_mode` | `res.company.factory_reporting_mode` | Selection: `manager`, `operator`, `both` | `both` | bounded enum | Production Manager | visible_if production；关闭生产时自动 `manager` | config audit | production.reporting_service |
| `barcode_requirement_warehouse` | `res.company.factory_barcode_requirement_warehouse` | Selection: `required`, `optional`, `none` | `optional` | bounded enum | Admin | visible_if inventory/mobile warehouse；父项关闭时自动 `none` | config audit | mobile.stock_action_service |
| `barcode_requirement_operator` | `res.company.factory_barcode_requirement_operator` | Selection: `required`, `optional`, `none` | `optional` | bounded enum | Admin | visible_if production/mobile operator；父项关闭时自动 `none` | config audit | mobile.production_action_service |

## 质量

| technical_key | Odoo storage | type / selection | exact default | constraints | group | dependency / disabled behavior | audit | consumer |
|---|---|---|---|---|---|---|---|---|
| `incoming_inspection_enabled` | `res.company.factory_incoming_inspection_enabled` | Boolean | true | — | Quality Manager | requires quality+purchasing；父项关闭且无开放检验时自动 false，否则阻止 | config audit | quality.trigger_service |
| `process_inspection_enabled` | `res.company.factory_process_inspection_enabled` | Boolean | true | — | Quality Manager | requires quality+production；同上 | config audit | quality.trigger_service |
| `final_inspection_enabled` | `res.company.factory_final_inspection_enabled` | Boolean | true | — | Quality Manager | requires quality+production；final gate requires | config audit | quality.trigger_service |
| `incoming_qc_gate` | `res.company.factory_incoming_qc_gate` | Boolean | false | — | Quality Manager | requires quality+incoming inspection；有待处理收货时阻止破坏性关闭，否则自动 false | config audit | quality.incoming_gate_service |
| `final_qc_gate` | `res.company.factory_final_qc_gate` | Boolean | true when quality enabled | — | Quality Manager | requires quality+final inspection；有待发货/隔离品时阻止关闭 | config audit | quality.final_gate_service |
| `reject_inventory_disposition` | `res.company.factory_reject_inventory_disposition` | Selection: `quarantine`, `scrap`, `return_supplier`, `rework` | `quarantine` | **无 record_only**；rework requires production, return requires purchasing | Quality Manager | requires quality+inventory；不兼容选项隐藏且存量存在时阻止变更 | config audit | quality.disposition_service |
| `ncr_creation_policy` | `res.company.factory_ncr_creation_policy` | Selection: `manual`, `severity_threshold`, `every_failure` | `severity_threshold` | bounded enum | Quality Manager | requires quality；关闭质量且无开放 NCR 时自动 `manual` | config audit | quality.ncr_service |
| `ncr_threshold_severity` | `res.company.factory_ncr_threshold_severity` | Selection: `low`, `medium`, `high`, `critical` | `high` | fixed semantic order | Quality Manager | required/visible_if NCR policy=`severity_threshold` | config audit | quality.ncr_service |
| `severity_low_label` | `res.company.factory_severity_low_label` | Char | 低 | nonempty, label only | Quality Manager | requires quality | config audit | quality.display_service |
| `severity_medium_label` | `res.company.factory_severity_medium_label` | Char | 中 | nonempty, label only | Quality Manager | requires quality | config audit | quality.display_service |
| `severity_high_label` | `res.company.factory_severity_high_label` | Char | 高 | nonempty, label only | Quality Manager | requires quality | config audit | quality.display_service |
| `severity_critical_label` | `res.company.factory_severity_critical_label` | Char | 关键 | nonempty, label only | Quality Manager | requires quality | config audit | quality.display_service |
| `ncr_sla_low_days` | `res.company.factory_ncr_sla_low_days` | Integer | 7 | `>= 0` | Quality Manager | requires quality | config audit | quality.ncr_sla_service |
| `ncr_sla_medium_days` | `res.company.factory_ncr_sla_medium_days` | Integer | 5 | `0 <= medium <= low` | Quality Manager | requires quality | config audit | quality.ncr_sla_service |
| `ncr_sla_high_days` | `res.company.factory_ncr_sla_high_days` | Integer | 2 | `0 <= high <= medium` | Quality Manager | requires quality | config audit | quality.ncr_sla_service |
| `ncr_sla_critical_days` | `res.company.factory_ncr_sla_critical_days` | Integer | 1 | `0 <= critical <= high` | Quality Manager | requires quality | config audit | quality.ncr_sla_service |
| `inspection_sample_size` | `product.template.factory_inspection_sample_size` | Integer | 1 | `>= 1`; no AQL | Quality Manager | requires quality | mail tracking | quality.sampling_service |

FAIL/Reject 的库存处置与是否创建 NCR 是两个独立事务：先由 `quality.disposition_service` 建立受控库存动作，再由 `quality.ncr_service` 按策略决定是否创建 NCR。任何 NCR 策略都不能跳过库存处置。

## 交付、移动端、通知与报表

| technical_key | Odoo storage | type / selection | exact default | constraints | group | dependency / disabled behavior | audit | consumer |
|---|---|---|---|---|---|---|---|---|
| `packaging_fields` | `res.company.factory_packaging_fields` | Selection-set: `carton_count`, `weight`, `cbm`, `photos` | all four | allowlist only | Delivery Manager | visible_if delivery；父项关闭时保留值但隐藏 | config audit | delivery.packaging_views |
| `shipment_mode` | `res.company.factory_shipment_mode` | Selection: `domestic`, `export`, `both` | `both` | bounded enum | Delivery Manager | requires delivery | config audit | delivery.shipment_views |
| `delivery_confirmation_mode` | `res.company.factory_delivery_confirmation_mode` | Selection: `manual`, `pod_required`, `tracking` | `manual` | MVP only manual/pod; tracking value reserved and disabled | Delivery Manager | requires delivery | config audit | delivery.confirmation_service |
| `mobile_warehouse_enabled` | `res.company.factory_mobile_warehouse_enabled` | Boolean | true | — | Admin | requires inventory；父项关闭时自动 false | config audit | mobile.menu_service |
| `mobile_operator_enabled` | `res.company.factory_mobile_operator_enabled` | Boolean | true | — | Admin | requires production；父项关闭时自动 false | config audit | mobile.menu_service |
| `mobile_quality_enabled` | `res.company.factory_mobile_quality_enabled` | Boolean | true | — | Admin | requires quality；父项关闭时自动 false | config audit | mobile.menu_service |
| `operator_scope` | `res.company.factory_operator_scope` | Selection: `own`, `team`, `all` | `own` | record rule must enforce | Admin | visible_if production | config audit | security.operator_rules |
| `photo_requirement_exception` | `res.company.factory_photo_requirement_exception` | Selection: `required`, `optional`, `none` | `required` | bounded enum | Factory OS Manager | relevant module enabled | config audit | mobile.attachment_validator |
| `photo_requirement_qc_fail` | `res.company.factory_photo_requirement_qc_fail` | Selection: `required`, `optional`, `none` | `required` | cannot be `none` for critical fail | Quality Manager | requires quality | config audit | quality.attachment_validator |
| `photo_requirement_standard` | `res.company.factory_photo_requirement_standard` | Selection: `required`, `optional`, `none` | `optional` | bounded enum | Factory OS Manager | relevant module enabled | config audit | mobile.attachment_validator |
| `notification_lead_days` | `res.company.factory_notification_lead_days` | Integer | 3 | `>= 0` | Factory OS Manager | system Activity only in MVP | config audit | core.notification_service |
| `notification_type_keys` | `res.company.factory_notification_type_keys` | Selection-set allowlist | `order_risk`, `material_shortage`, `po_late`, `qc_high`, `ncr_overdue` | allowlist only; high/critical QC cannot be removed | Factory OS Manager | unavailable-module type auto removed | config audit | core.notification_service |
| `notification_role_group_ids` | `res.company.factory_notification_role_group_ids` | Many2many(`res.groups`) | manager groups | Factory OS allowlist | Admin | system Activity only in MVP | config audit | core.notification_service |
| `homepage_kpi_keys` | `res.company.factory_homepage_kpi_keys` | Selection-set allowlist | `risk_orders`, `material_shortages`, `late_production`, `open_ncr` | 4–6 unique keys | Factory OS Manager | unavailable-module KPI automatically hidden | config audit | dashboard.kpi_service |
| `report_module_keys` | `res.company.factory_report_module_keys` | Selection-set allowlist | enabled modules | only enabled business modules | Factory OS Manager | parent module off => auto remove key | config audit | dashboard.report_menu |

风险严重度映射使用固定代码表 `factory.risk.rule` 的有界规则，不允许把 `quality_fail_high` 或 `quality_fail_critical` 映射为 `normal` 或隐藏。该规则表只允许 Factory OS Manager 修改阈值/负责人，不允许新增健康度状态。

## 权限与 Connector

| technical_key | Odoo storage | type / selection | exact default | constraints | group | dependency / disabled behavior | audit | consumer |
|---|---|---|---|---|---|---|---|---|
| `user_factory_role_ids` | `res.users.groups_id` | Many2many(`res.groups`) | least privilege | allowlisted built-in roles | Admin | 移除角色立即收紧权限 | Odoo group audit + config audit | ACL/record rules |
| `user_warehouse_ids` | `res.users.factory_warehouse_ids` | Many2many(`stock.warehouse`) | empty | same allowed companies | Admin | requires corresponding role | config audit | security.warehouse_rules |
| `user_team_ids` | `res.users.factory_team_ids` | Many2many(`factory.team`) | empty | same company | Admin | requires operator/manager role | config audit | security.team_rules |
| `cost_visibility` | `res.groups.factory_cost_viewer` membership | Group membership | managers only | group + field ACL | Admin | no UI-only bypass | group audit | product/report views |
| `sales_price_visibility` | `res.groups.factory_sales_price_viewer` membership | Group membership | sales + managers | group + field ACL | Admin | no UI-only bypass | group audit | sales/product views |
| `margin_visibility` | `res.groups.factory_margin_viewer` membership | Group membership | managers only | group + field ACL | Admin | requires cost and sales price groups | group audit | dashboard/report views |
| `connector_endpoint` | `res.company.factory_connector_endpoint` | Char(URL) | empty | HTTPS except localhost test | Integration Admin | required_if connector enabled | config audit | connector.client |
| `connector_workspace_key` | `res.company.factory_connector_workspace_key` | Char | empty | unique, nonempty when enabled | Integration Admin | required_if connector enabled | config audit | connector.client |
| `connector_credential` | `factory.connector.credential.secret` | encrypted secret | empty | never readable after save | Integration Admin | required_if connector enabled；关闭不删除 | audit metadata only | connector.client |
| `connector_share_price` | `res.company.factory_connector_share_price` | Boolean | false | explicit authorization | Integration Admin | requires connector；关闭 connector keeps false | config audit | connector.payload_policy |
| `connector_shared_field_keys` | `res.company.factory_connector_shared_field_keys` | Selection-set allowlist | minimal order/status/quantity/dates | denylist always wins; no “all” value | Integration Admin | requires connector；父项关闭保留但不发送 | config audit | connector.payload_policy |

私有字段黑名单、租户隔离、库存事实源、追溯来源、健康度语义和强制审计属于 C 类不变量，没有 technical setting key、Settings proxy 或关闭路径。
