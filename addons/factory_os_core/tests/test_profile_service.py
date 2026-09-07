# -*- coding: utf-8 -*-
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestProfileService(TransactionCase):

    def setUp(self):
        super().setUp()
        self.service = self.env["factory.os.profile.service"]
        self.company = self.env.company

    def test_core_only_module_states(self):
        # Native engine modules exist in the addons path but are not
        # installed on a core-only DB.
        self.assertEqual(
            self.service._module_state("stock"),
            "uninstalled",
        )
        self.assertEqual(
            self.service._module_state("mrp"),
            "uninstalled",
        )
        # Factory OS business addons are not yet created -> absent record.
        self.assertEqual(
            self.service._module_state("factory_os_supply"),
            "absent",
        )
        self.assertEqual(
            self.service._module_state("factory_os_production"),
            "absent",
        )

    def test_core_only_consistency_none_for_default_company(self):
        issues = self.service._consistency_issues(self.company)
        self.assertEqual(issues, [])

    def test_default_flags_false(self):
        self.assertFalse(self.company.factory_inventory_enabled)
        self.assertFalse(self.company.factory_mrp_production_enabled)

    def test_sales_enabled_default_true(self):
        self.assertTrue(self.company.factory_sales_enabled)

    def test_missing_modules(self):
        missing = self.service._missing_modules(
            {"stock", "factory_os_supply", "mrp"}
        )
        self.assertEqual(
            set(missing),
            {"stock", "factory_os_supply", "mrp"},
        )

    def test_module_installed_absent(self):
        self.assertFalse(self.service._module_installed("stock"))
