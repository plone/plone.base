"""Unit tests for controlpanel schema."""

from plone.base.interfaces import IFilterSchema
from zope.schema import getFields

import unittest


class FilterSchemaTests(unittest.TestCase):
    def test_area_tag_in_valid_tags_default(self):
        """Verify that 'area' is in the default valid_tags list."""
        fields = getFields(IFilterSchema)
        valid_tags_field = fields["valid_tags"]
        self.assertIn("area", valid_tags_field.default)


class MailSchemaTests(unittest.TestCase):
    def validate(self, port, implicit_tls):
        from plone.base.interfaces import IMailSchema
        from types import SimpleNamespace

        data = SimpleNamespace(smtp_port=port, smtp_implicit_tls=implicit_tls)
        IMailSchema.validateInvariants(data)

    def test_implicit_tls_on_port_465(self):
        self.validate(465, True)

    def test_implicit_tls_on_other_port(self):
        self.validate(2465, True)

    def test_implicit_tls_off(self):
        self.validate(25, False)
        self.validate(587, False)

    def test_implicit_tls_on_starttls_port(self):
        from zope.interface import Invalid

        for port in (25, 587):
            with self.assertRaises(Invalid):
                self.validate(port, True)
