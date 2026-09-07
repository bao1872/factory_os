# -*- coding: utf-8 -*-
from odoo.exceptions import AccessError, ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestConfigAudit(TransactionCase):

    def setUp(self):
        super().setUp()
        self.company = self.env.company
        self.audit_model = self.env["factory.config.audit"]

    def _write_with_source(self, source="settings", **vals):
        self.company.with_context(
            factory_audit_source=source
        ).write(vals)

    def test_change_writes_exactly_one_audit_row(self):
        before = self.audit_model.search_count([])
        self._write_with_source(
            "settings",
            factory_setup_complete=True,
        )
        after = self.audit_model.search_count([])
        self.assertEqual(after - before, 1)

    def test_same_value_writes_zero_rows(self):
        self._write_with_source(
            "settings",
            factory_setup_complete=True,
        )
        before = self.audit_model.search_count([])
        # Same value again -> no delta -> no new row.
        self._write_with_source(
            "settings",
            factory_setup_complete=True,
        )
        after = self.audit_model.search_count([])
        self.assertEqual(after, before)

    def test_audit_old_new_value_correct(self):
        self.company.factory_setup_complete = False
        self._write_with_source(
            "settings",
            factory_setup_complete=True,
        )
        row = self.audit_model.search(
            [("setting_key", "=", "factory_setup_complete")],
            order="id desc",
            limit=1,
        )
        self.assertEqual(row.old_value, repr(False))
        self.assertEqual(row.new_value, repr(True))

    def test_audit_user_is_actual_actor(self):
        self._write_with_source(
            "settings",
            factory_setup_complete=True,
        )
        row = self.audit_model.search(
            [("setting_key", "=", "factory_setup_complete")],
            order="id desc",
            limit=1,
        )
        self.assertEqual(row.user_id, self.env.user)

    def test_audit_write_access_error(self):
        self._write_with_source(
            "settings",
            factory_setup_complete=True,
        )
        row = self.audit_model.search([], limit=1)
        with self.assertRaises(AccessError):
            row.write({"setting_key": "tampered"})

    def test_audit_unlink_access_error(self):
        self._write_with_source(
            "settings",
            factory_setup_complete=True,
        )
        row = self.audit_model.search([], limit=1)
        with self.assertRaises(AccessError):
            row.unlink()

    def test_normal_admin_cannot_manually_create(self):
        # A non-superuser user holding group_factory_os_admin must not be
        # able to fabricate audit rows: creation is superuser-only.
        admin_group = self.env.ref(
            "factory_os_core.group_factory_os_admin"
        )
        user = self.env["res.users"].create({
            "name": "Factory Admin (non-root)",
            "login": "factory_admin_nonroot",
            "company_id": self.company.id,
            "company_ids": [(4, self.company.id)],
            "group_ids": [(4, admin_group.id)],
        })
        with self.assertRaises(AccessError):
            self.audit_model.with_user(user).create({
                "company_id": self.company.id,
                "setting_key": "forged",
                "old_value": "x",
                "new_value": "y",
            })

    def test_settings_write_reaches_company_validation(self):
        # Phase 1A boundary: factory_setup_complete is intentionally
        # readonly in res.config.settings, so there is no writable + legally
        # writable capability on a core-only DB that can yield a successful
        # source="settings" audit row. The success-path assertion is deferred
        # to Phase 1B (SETTINGS-AUDIT-01). Here we prove the genuine
        # Settings related-field path reaches res.company validation and that
        # a rejected transaction does not fabricate audit history.
        settings = self.env["res.config.settings"].create({
            "company_id": self.company.id,
        })

        before = self.audit_model.search_count([])

        with self.assertRaises(ValidationError):
            settings.write({
                "factory_purchasing_enabled": True,
            })

        after = self.audit_model.search_count([])

        # Genuine Settings related-field path reached res.company validation,
        # but the rejected transaction must not fabricate an audit row.
        self.assertEqual(after, before)

    def test_audit_company_relation_is_restrict(self):
        field = self.audit_model._fields["company_id"]
        self.assertEqual(field.ondelete, "restrict")

    def test_audit_company_deletion_raises(self):
        # Deleting a company that still has audit rows must raise, since
        # ondelete="restrict" preserves audit history. The exact exception
        # class is recorded from runtime rather than guessed.
        company = self.env["res.company"].create({
            "name": "Disposable Company",
        })
        self.audit_model.sudo().create({
            "company_id": company.id,
            "user_id": self.env.user.id,
            "setting_key": "security_test",
            "old_value": "False",
            "new_value": "True",
            "source": "system",
        })

        from psycopg2 import IntegrityError
        with self.assertRaises(IntegrityError):
            company.unlink()
