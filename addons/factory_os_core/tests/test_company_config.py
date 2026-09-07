# -*- coding: utf-8 -*-
from odoo.exceptions import ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestCompanyConfig(TransactionCase):

    def test_order_core_cannot_be_disabled(self):
        company = self.env.company
        with self.assertRaises(ValidationError):
            company.write({"factory_sales_enabled": False})

    def test_purchasing_requires_inventory(self):
        company = self.env.company
        with self.assertRaises(ValidationError):
            company.write({
                "factory_purchasing_enabled": True,
                "factory_inventory_enabled": False,
            })

    def test_delivery_requires_inventory(self):
        company = self.env.company
        with self.assertRaises(ValidationError):
            company.write({"factory_delivery_enabled": True})

    def test_mrp_requires_inventory(self):
        company = self.env.company
        with self.assertRaises(ValidationError):
            company.write({"factory_mrp_production_enabled": True})

    def test_quality_requires_inventory(self):
        company = self.env.company
        with self.assertRaises(ValidationError):
            company.write({"factory_quality_enabled": True})

    def test_inventory_requires_stock_and_supply(self):
        company = self.env.company
        with self.assertRaises(ValidationError):
            # On a core-only DB, stock and factory_os_supply are absent.
            company.write({"factory_inventory_enabled": True})

    def test_mrp_requires_mrp_and_production(self):
        company = self.env.company
        with self.assertRaises(ValidationError):
            company.write({
                "factory_inventory_enabled": True,
                "factory_mrp_production_enabled": True,
            })

    def test_quality_requires_quality_addon(self):
        company = self.env.company
        with self.assertRaises(ValidationError):
            company.write({
                "factory_inventory_enabled": True,
                "factory_quality_enabled": True,
            })
