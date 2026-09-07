# -*- coding: utf-8 -*-
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
        user = self._create_user("group_factory_os_user")
        Audit = self.audit_model.with_user(user)
        # No read ACL for group_factory_os_user -> search raises AccessError.
        from odoo.exceptions import AccessError
        with self.assertRaises(AccessError):
            Audit.search([])

    def _create_user(self, group_xml_id):
        group = self._role(group_xml_id)
        user = self.env["res.users"].create({
            "name": "Factory Test User",
            "login": "factory_test_user",
            "company_id": self.env.company.id,
            "company_ids": [(4, self.env.company.id)],
            "group_ids": [(4, group.id)],
        })
        return user
