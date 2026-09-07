from odoo import _, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    factory_setup_complete = fields.Boolean(
        related="company_id.factory_setup_complete",
        readonly=True,
    )

    factory_sales_enabled = fields.Boolean(
        related="company_id.factory_sales_enabled",
        readonly=True,
    )

    factory_inventory_enabled = fields.Boolean(
        related="company_id.factory_inventory_enabled",
        readonly=True,
    )

    factory_mrp_production_enabled = fields.Boolean(
        related="company_id.factory_mrp_production_enabled",
        readonly=True,
    )

    factory_quality_enabled = fields.Boolean(
        related="company_id.factory_quality_enabled",
        readonly=True,
    )

    factory_purchasing_enabled = fields.Boolean(
        related="company_id.factory_purchasing_enabled",
        readonly=False,
    )

    factory_delivery_enabled = fields.Boolean(
        related="company_id.factory_delivery_enabled",
        readonly=False,
    )

    factory_reports_enabled = fields.Boolean(
        related="company_id.factory_reports_enabled",
        readonly=False,
    )

    factory_connector_enabled = fields.Boolean(
        related="company_id.factory_connector_enabled",
        readonly=False,
    )

    def write(self, vals):
        settings = self.with_context(
            factory_audit_source="settings"
        )

        return super(
            ResConfigSettings,
            settings,
        ).write(vals)

    def action_factory_check_profile_consistency(self):
        self.ensure_one()

        if not self.env.user.has_group(
            "factory_os_core.group_factory_os_admin"
        ):
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "type": "danger",
                    "title": _("Access denied"),
                    "message": _("Factory OS Admin permission is required."),
                    "sticky": False,
                },
            }

        issues = self.env[
            "factory.os.profile.service"
        ]._consistency_issues(self.company_id)

        if issues:
            message = "\n".join(
                f"{issue['code']}: {issue['message']}"
                for issue in issues
            )
            notification_type = "warning"
            title = _("Profile inconsistency detected")
        else:
            message = _("Factory OS capability state matches installed engines.")
            notification_type = "success"
            title = _("Profile consistency PASS")

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "type": notification_type,
                "title": title,
                "message": message,
                "sticky": bool(issues),
            },
        }
