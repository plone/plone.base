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
