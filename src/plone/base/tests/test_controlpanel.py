"""Unit tests for controlpanel schema."""

from plone.base.interfaces import IFilterSchema
from plone.base.interfaces import IImagingSchema
from zope.schema import getFields

import unittest


class FilterSchemaTests(unittest.TestCase):
    def test_area_tag_in_valid_tags_default(self):
        """Verify that 'area' is in the default valid_tags list."""
        fields = getFields(IFilterSchema)
        valid_tags_field = fields["valid_tags"]
        self.assertIn("area", valid_tags_field.default)


class ImagingSchemaTests(unittest.TestCase):
    def test_avif_mode_defaults_to_avif_with_fallback(self):
        field = getFields(IImagingSchema)["avif_mode"]
        self.assertEqual(field.default, "avif_with_fallback")
        self.assertEqual(
            [term.value for term in field.vocabulary],
            ["disabled", "avif_with_fallback", "avif_only"],
        )

    def test_avif_quality_and_speed_ranges_and_defaults(self):
        fields = getFields(IImagingSchema)
        quality = fields["avif_quality"]
        speed = fields["avif_speed"]
        self.assertEqual((quality.min, quality.max, quality.default), (1, 100, 65))
        self.assertEqual((speed.min, speed.max, speed.default), (0, 10, 8))
