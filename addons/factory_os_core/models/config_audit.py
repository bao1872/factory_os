from odoo import api, fields, models
from odoo.exceptions import AccessError


class FactoryConfigAudit(models.Model):
    _name = "factory.config.audit"
    _description = "Factory OS Configuration Audit"
    _order = "create_date desc, id desc"
    _rec_name = "setting_key"

    company_id = fields.Many2one(
        "res.company",
        required=True,
        index=True,
        ondelete="cascade",
    )

    user_id = fields.Many2one(
        "res.users",
        required=False,
        index=True,
        ondelete="set null",
    )

    setting_key = fields.Char(
        required=True,
        index=True,
    )

    old_value = fields.Text(
        readonly=True,
    )

    new_value = fields.Text(
        readonly=True,
    )

    source = fields.Selection(
        [
            ("settings", "Settings"),
            ("setup_wizard", "Setup Wizard"),
            ("profile_service", "Profile Service"),
            ("system", "System"),
        ],
        required=True,
        default="system",
        readonly=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.is_superuser():
            raise AccessError(
                "Factory configuration audit records are system-created only."
            )
        return super().create(vals_list)

    def write(self, vals):
        raise AccessError(
            "Factory configuration audit records are immutable."
        )

    def unlink(self):
        raise AccessError(
            "Factory configuration audit records are immutable."
        )
