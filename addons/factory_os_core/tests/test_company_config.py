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

    def _company_vals(self, suffix):
        return {
            "name": f"Factory Test {suffix}",
        }

    def test_create_default_safe_minimal_company(self):
        company = self.env["res.company"].create(
            self._company_vals("Safe Minimal")
        )

        self.assertTrue(company.factory_sales_enabled)
        self.assertFalse(company.factory_inventory_enabled)
        self.assertFalse(company.factory_mrp_production_enabled)
        self.assertFalse(company.factory_quality_enabled)
        self.assertFalse(company.factory_purchasing_enabled)
        self.assertFalse(company.factory_setup_complete)

    def test_create_rejects_disabled_order_core(self):
        vals = self._company_vals("Order Off")
        vals["factory_sales_enabled"] = False

        with self.assertRaises(ValidationError):
            self.env["res.company"].create(vals)

    def test_create_rejects_purchasing_without_inventory(self):
        vals = self._company_vals("Purchase Invalid")
        vals["factory_purchasing_enabled"] = True

        with self.assertRaises(ValidationError):
            self.env["res.company"].create(vals)

    def test_create_rejects_mrp_without_inventory(self):
        vals = self._company_vals("MRP Invalid")
        vals["factory_mrp_production_enabled"] = True

        with self.assertRaises(ValidationError):
            self.env["res.company"].create(vals)

    def test_create_rejects_quality_without_inventory(self):
        vals = self._company_vals("Quality Invalid")
        vals["factory_quality_enabled"] = True

        with self.assertRaises(ValidationError):
            self.env["res.company"].create(vals)

    def test_create_rejects_inventory_without_profile(self):
        vals = self._company_vals("Inventory Invalid")
        vals["factory_inventory_enabled"] = True

        with self.assertRaises(ValidationError):
            self.env["res.company"].create(vals)

    def test_create_rejects_setup_complete(self):
        vals = self._company_vals("Fake Setup")
        vals["factory_setup_complete"] = True

        with self.assertRaises(ValidationError):
            self.env["res.company"].create(vals)
