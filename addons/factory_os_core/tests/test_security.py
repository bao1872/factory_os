# -*- coding: utf-8 -*-
from odoo.exceptions import AccessError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestSecurity(TransactionCase):

    def setUp(self):
        super().setUp()
        self.audit_model = self.env["factory.config.audit"]

    def _role(self, xml_id):
        return self.env.ref("factory_os_core.%s" % xml_id)

    def test_all_role_xml_ids_exist(self):
        roles = [
            "group_factory_os_user",
            "group_factory_os_manager",
            "group_factory_os_admin",
            "group_factory_os_owner",
            "group_factory_sales_manager",
            "group_factory_purchase_manager",
            "group_factory_inventory_manager",
            "group_factory_product_manager",
            "group_factory_production_manager",
            "group_factory_operator",
            "group_factory_quality_manager",
            "group_factory_delivery_manager",
            "group_factory_integration_admin",
        ]
        for role in roles:
            self.assertTrue(
                self.env.ref("factory_os_core.%s" % role),
                "missing role: %s" % role,
            )

    def _implied(self, group):
        return set(group.all_implied_ids.ids)

    def test_owner_implies_all_roles(self):
        owner = self._role("group_factory_os_owner")
        implied = self._implied(owner)
        for role in [
            "group_factory_os_admin",
            "group_factory_sales_manager",
            "group_factory_purchase_manager",
            "group_factory_inventory_manager",
            "group_factory_product_manager",
            "group_factory_production_manager",
            "group_factory_operator",
            "group_factory_quality_manager",
            "group_factory_delivery_manager",
            "group_factory_integration_admin",
        ]:
            self.assertIn(self._role(role).id, implied)

    def test_admin_implies_manager(self):
        admin = self._role("group_factory_os_admin")
        self.assertIn(
            self._role("group_factory_os_manager").id,
            self._implied(admin),
        )

    def test_manager_implies_user(self):
        manager = self._role("group_factory_os_manager")
        self.assertIn(
            self._role("group_factory_os_user").id,
            self._implied(manager),
        )

    def test_normal_user_cannot_read_audit(self):
        user = self._create_user_for_company(
            "factory_normal_user",
            self.env.company,
            "group_factory_os_user",
        )
        Audit = self.audit_model.with_user(user)
        # No read ACL for group_factory_os_user -> search raises AccessError.
        with self.assertRaises(AccessError):
            Audit.search([])

    def test_manager_can_read_but_cannot_mutate_audit(self):
        manager = self._create_user_for_company(
            "factory_manager_security",
            self.env.company,
            "group_factory_os_manager",
        )

        row = self._create_audit_row(self.env.company)

        Audit = self.audit_model.with_user(manager)

        self.assertEqual(
            Audit.search([("id", "=", row.id)]),
            row,
        )

        with self.assertRaises(AccessError):
            row.with_user(manager).write({
                "setting_key": "tampered",
            })

        with self.assertRaises(AccessError):
            row.with_user(manager).unlink()

        with self.assertRaises(AccessError):
            Audit.create({
                "company_id": self.env.company.id,
                "setting_key": "forged",
                "old_value": "x",
                "new_value": "y",
                "source": "system",
            })

    def test_admin_can_read_but_cannot_mutate_audit(self):
        admin = self._create_user_for_company(
            "factory_admin_security",
            self.env.company,
            "group_factory_os_admin",
        )

        row = self._create_audit_row(self.env.company)

        Audit = self.audit_model.with_user(admin)

        self.assertEqual(
            Audit.search([("id", "=", row.id)]),
            row,
        )

        with self.assertRaises(AccessError):
            row.with_user(admin).write({
                "setting_key": "tampered",
            })

        with self.assertRaises(AccessError):
            row.with_user(admin).unlink()

        with self.assertRaises(AccessError):
            Audit.create({
                "company_id": self.env.company.id,
                "setting_key": "forged",
                "old_value": "x",
                "new_value": "y",
                "source": "system",
            })

    def test_cross_company_visibility(self):
        company_a = self.env.company
        company_b = self.env["res.company"].create({
            "name": "Factory Test Company B",
        })

        row_a = self._create_audit_row(company_a)
        row_b = self._create_audit_row(company_b)

        manager = self._create_user_for_company(
            "factory_cross_company_manager",
            company_a,
            "group_factory_os_manager",
            allowed_companies=company_a,
        )
        Audit = self.audit_model.with_user(manager)

        visible_ids = Audit.search([]).ids

        self.assertIn(row_a.id, visible_ids)
        self.assertNotIn(row_b.id, visible_ids)

        # Grant both companies -> both rows become visible.
        manager.write({
            "company_ids": [(6, 0, (company_a | company_b).ids)],
        })

        visible_ids = Audit.search([]).ids

        self.assertIn(row_a.id, visible_ids)
        self.assertIn(row_b.id, visible_ids)

    def test_multi_role_user_keeps_all_roles(self):
        sales = self._role("group_factory_sales_manager")
        quality = self._role("group_factory_quality_manager")

        user = self.env["res.users"].create({
            "name": "Factory Multi Role",
            "login": "factory_multi_role",
            "company_id": self.env.company.id,
            "company_ids": [(4, self.env.company.id)],
            "group_ids": [(6, 0, [sales.id, quality.id])],
        })

        user_group_ids = set(user.group_ids.ids)
        self.assertIn(sales.id, user_group_ids)
        self.assertIn(quality.id, user_group_ids)

    def _create_user_for_company(
        self,
        login,
        company,
        role_xml_id,
        allowed_companies=None,
    ):
        group = self._role(role_xml_id)

        allowed_companies = (
            allowed_companies
            if allowed_companies is not None
            else company
        )

        return self.env["res.users"].create({
            "name": login,
            "login": login,
            "company_id": company.id,
            "company_ids": [(6, 0, allowed_companies.ids)],
            "group_ids": [(4, group.id)],
        })

    def _create_audit_row(self, company):
        return self.audit_model.sudo().create({
            "company_id": company.id,
            "user_id": self.env.user.id,
            "setting_key": "security_test",
            "old_value": "False",
            "new_value": "True",
            "source": "system",
        })
