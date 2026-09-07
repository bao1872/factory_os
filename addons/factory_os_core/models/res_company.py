from odoo import _, fields, models
from odoo.exceptions import ValidationError


class ResCompany(models.Model):
    _inherit = "res.company"

    factory_setup_complete = fields.Boolean(
        string="Factory OS Setup Complete",
        default=False,
        copy=False,
        groups="factory_os_core.group_factory_os_admin",
    )

    # Order Core is permanently available. This is NOT a user capability toggle.
    factory_sales_enabled = fields.Boolean(
        string="Order Core Enabled",
        default=True,
        copy=False,
        groups="factory_os_core.group_factory_os_admin",
    )

    factory_inventory_enabled = fields.Boolean(
        string="Inventory Capability",
        default=False,
        copy=False,
        groups="factory_os_core.group_factory_os_admin",
    )

    factory_mrp_production_enabled = fields.Boolean(
        string="Formal MRP Capability",
        default=False,
        copy=False,
        groups="factory_os_core.group_factory_os_admin",
    )

    factory_quality_enabled = fields.Boolean(
        string="Quality Capability",
        default=False,
        copy=False,
        groups="factory_os_core.group_factory_os_admin",
    )

    factory_purchasing_enabled = fields.Boolean(
        string="Purchasing Workflow",
        default=False,
        copy=False,
        groups="factory_os_core.group_factory_os_admin",
    )

    factory_delivery_enabled = fields.Boolean(
        string="Delivery Workflow",
        default=False,
        copy=False,
        groups="factory_os_core.group_factory_os_admin",
    )

    factory_reports_enabled = fields.Boolean(
        string="Reports",
        default=False,
        copy=False,
        groups="factory_os_core.group_factory_os_admin",
    )

    factory_connector_enabled = fields.Boolean(
        string="Central Connector",
        default=False,
        copy=False,
        groups="factory_os_core.group_factory_os_admin",
    )

    def _factory_audited_fields(self):
        return {
            "factory_setup_complete",
            "factory_sales_enabled",
            "factory_inventory_enabled",
            "factory_mrp_production_enabled",
            "factory_quality_enabled",
            "factory_purchasing_enabled",
            "factory_delivery_enabled",
            "factory_reports_enabled",
            "factory_connector_enabled",
        }

    def _factory_validate_write(self, vals):
        service = self.env["factory.os.profile.service"]

        for company in self:
            if (
                "factory_sales_enabled" in vals
                and not vals["factory_sales_enabled"]
            ):
                raise ValidationError(
                    _("Factory OS Order Core cannot be disabled.")
                )

            for field_name in (
                "factory_inventory_enabled",
                "factory_mrp_production_enabled",
                "factory_quality_enabled",
            ):
                if (
                    field_name in vals
                    and not vals[field_name]
                    and company[field_name]
                ):
                    raise ValidationError(
                        _(
                            "%(field)s is monotonic in Factory OS v0.1 "
                            "and cannot be disabled.",
                            field=field_name,
                        )
                    )

            service._validate_requested_values(company, vals)

            if vals.get("factory_setup_complete"):
                # Evaluate prospective values, not only cached pre-write
                # company values: issue logic reads override first.
                issues = service._consistency_issues(company, overrides=vals)
                if issues:
                    raise ValidationError(
                        _(
                            "Factory OS setup cannot be completed while "
                            "profile consistency issues exist: %(issues)s",
                            issues="; ".join(
                                issue["code"] for issue in issues
                            ),
                        )
                    )

    def write(self, vals):
        self._factory_validate_write(vals)

        tracked = self._factory_audited_fields().intersection(vals)
        before = {
            company.id: {
                field_name: company[field_name]
                for field_name in tracked
            }
            for company in self
        }

        result = super().write(vals)

        source = self.env.context.get("factory_audit_source", "system")
        allowed_sources = {
            "settings",
            "setup_wizard",
            "profile_service",
            "system",
        }
        if source not in allowed_sources:
            source = "system"

        audit_vals = []

        for company in self:
            for field_name in tracked:
                old_value = before[company.id][field_name]
                new_value = company[field_name]

                if old_value == new_value:
                    continue

                audit_vals.append({
                    "company_id": company.id,
                    "user_id": self.env.user.id,
                    "setting_key": field_name,
                    "old_value": repr(old_value),
                    "new_value": repr(new_value),
                    "source": source,
                })

        if audit_vals:
            # Narrow sudo is intentional and must remain isolated here.
            # Users cannot create/fabricate audit rows directly.
            self.env["factory.config.audit"].sudo().create(audit_vals)

        return result
