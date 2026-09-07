from odoo import _, api, models
from odoo.exceptions import ValidationError


class FactoryOSProfileService(models.AbstractModel):
    _name = "factory.os.profile.service"
    _description = "Factory OS Installation Profile Service"

    _CAPABILITY_REQUIREMENTS = {
        "factory_inventory_enabled": {
            "modules": {"stock", "factory_os_supply"},
        },
        "factory_mrp_production_enabled": {
            "modules": {"mrp", "factory_os_production"},
        },
        "factory_quality_enabled": {
            "modules": {"factory_os_quality"},
        },
        "factory_purchasing_enabled": {
            "modules": {"factory_os_supply"},
        },
        "factory_delivery_enabled": {
            "modules": {"factory_os_delivery"},
        },
        "factory_reports_enabled": {
            "modules": {"factory_os_dashboard"},
        },
        "factory_connector_enabled": {
            "modules": {"factory_os_connector"},
        },
    }

    @api.model
    def _module_state(self, module_name):
        # Narrow sudo is intentional:
        # module metadata is infrastructure truth and this method is private.
        module = self.env["ir.module.module"].sudo().search(
            [("name", "=", module_name)],
            limit=1,
        )
        return module.state if module else "absent"

    @api.model
    def _module_installed(self, module_name):
        return self._module_state(module_name) == "installed"

    @api.model
    def _missing_modules(self, module_names):
        return sorted(
            name for name in module_names
            if not self._module_installed(name)
        )

    @api.model
    def _validate_requested_values(self, company, vals):
        prospective = {
            "factory_sales_enabled": vals.get(
                "factory_sales_enabled",
                company.factory_sales_enabled,
            ),
            "factory_inventory_enabled": vals.get(
                "factory_inventory_enabled",
                company.factory_inventory_enabled,
            ),
            "factory_mrp_production_enabled": vals.get(
                "factory_mrp_production_enabled",
                company.factory_mrp_production_enabled,
            ),
            "factory_quality_enabled": vals.get(
                "factory_quality_enabled",
                company.factory_quality_enabled,
            ),
            "factory_purchasing_enabled": vals.get(
                "factory_purchasing_enabled",
                company.factory_purchasing_enabled,
            ),
            "factory_delivery_enabled": vals.get(
                "factory_delivery_enabled",
                company.factory_delivery_enabled,
            ),
            "factory_reports_enabled": vals.get(
                "factory_reports_enabled",
                company.factory_reports_enabled,
            ),
            "factory_connector_enabled": vals.get(
                "factory_connector_enabled",
                company.factory_connector_enabled,
            ),
        }

        if not prospective["factory_sales_enabled"]:
            raise ValidationError(_("Factory OS Order Core cannot be disabled."))

        inventory = prospective["factory_inventory_enabled"]

        if prospective["factory_purchasing_enabled"] and not inventory:
            raise ValidationError(
                _("Purchasing requires Inventory in Factory OS v0.1.")
            )

        if prospective["factory_delivery_enabled"] and not inventory:
            raise ValidationError(
                _("Delivery requires Inventory.")
            )

        if prospective["factory_mrp_production_enabled"] and not inventory:
            raise ValidationError(
                _("Formal MRP requires Inventory.")
            )

        if prospective["factory_quality_enabled"] and not inventory:
            raise ValidationError(
                _("Quality requires Inventory.")
            )

        for flag, requirement in self._CAPABILITY_REQUIREMENTS.items():
            if not prospective[flag]:
                continue

            missing = self._missing_modules(requirement["modules"])
            if missing:
                raise ValidationError(
                    _(
                        "Capability %(flag)s cannot be enabled because "
                        "required modules are not installed: %(modules)s",
                        flag=flag,
                        modules=", ".join(missing),
                    )
                )

    @api.model
    def _consistency_issues(self, company, overrides=None):
        overrides = overrides or {}
        issues = []

        def value(field_name):
            if field_name in overrides:
                return overrides[field_name]
            return company[field_name]

        inventory_enabled = value("factory_inventory_enabled")
        mrp_enabled = value("factory_mrp_production_enabled")
        quality_enabled = value("factory_quality_enabled")
        purchasing_enabled = value("factory_purchasing_enabled")
        delivery_enabled = value("factory_delivery_enabled")

        # Engine truth: native engines may not be silently hidden.
        stock_installed = self._module_installed("stock")
        mrp_installed = self._module_installed("mrp")
        quality_installed = self._module_installed("factory_os_quality")

        if stock_installed and not inventory_enabled:
            issues.append({
                "code": "STOCK_ENGINE_WITH_INVENTORY_OFF",
                "message": "stock is installed while Inventory capability is off",
            })

        if inventory_enabled:
            for module in ("stock", "factory_os_supply"):
                if not self._module_installed(module):
                    issues.append({
                        "code": "INVENTORY_PROFILE_INCOMPLETE",
                        "message": f"Inventory capability requires {module}",
                    })

        if mrp_installed and not mrp_enabled:
            issues.append({
                "code": "MRP_ENGINE_WITH_MRP_OFF",
                "message": "mrp is installed while Formal MRP capability is off",
            })

        if mrp_enabled:
            for module in ("mrp", "factory_os_production"):
                if not self._module_installed(module):
                    issues.append({
                        "code": "MRP_PROFILE_INCOMPLETE",
                        "message": f"Formal MRP capability requires {module}",
                    })

        if quality_installed and not quality_enabled:
            issues.append({
                "code": "QUALITY_ADDON_WITH_QUALITY_OFF",
                "message": (
                    "factory_os_quality is installed while Quality capability is off"
                ),
            })

        if quality_enabled and not quality_installed:
            issues.append({
                "code": "QUALITY_PROFILE_INCOMPLETE",
                "message": "Quality capability requires factory_os_quality",
            })

        if purchasing_enabled and not inventory_enabled:
            issues.append({
                "code": "PURCHASING_WITHOUT_INVENTORY",
                "message": "Purchasing requires Inventory",
            })

        if delivery_enabled and not inventory_enabled:
            issues.append({
                "code": "DELIVERY_WITHOUT_INVENTORY",
                "message": "Delivery requires Inventory",
            })

        return issues
