"""Unit tests for utils module."""

from plone.subrequest.interfaces import ISubRequest
from zope.interface import alsoProvides

import unittest

SITE_LOGO_BASE64 = (
    b"filenameb64:cGl4ZWwucG5n;datab64:iVBORw0KGgoAAAANSUhEUgA"
    b"AAAEAAAABCAIAAACQd1PeAAAADElEQVQI12P4z8AAAAMBAQAY3Y2wAAA"
    b"AAElFTkSuQmCC"
)


class DefaultUtilsTests(unittest.TestCase):
    def test_safe_bytes(self):
        """safe_bytes should always encode unicode to the specified encoding."""
        from plone.base.utils import safe_bytes

        self.assertEqual(safe_bytes("späm"), b"sp\xc3\xa4m")
        self.assertEqual(safe_bytes("späm", "utf-8"), b"sp\xc3\xa4m")
        self.assertEqual(safe_bytes("späm", encoding="latin-1"), b"sp\xe4m")

    def test_get_top_request(self):
        """If in a subrequest, ``get_top_request`` should always return the top
        most request.
        """
        from plone.base.utils import get_top_request

        class MockRequest:
            def __init__(self, parent_request=None):
                self._dict = {}
                if parent_request:
                    self._dict["PARENT_REQUEST"] = parent_request
                    alsoProvides(self, ISubRequest)

            def get(self, key, default=None):
                return self._dict.get(key, default)

        req0 = MockRequest()
        req1 = MockRequest(req0)
        req2 = MockRequest(req1)

        self.assertEqual(get_top_request(req0), req0)
        self.assertEqual(get_top_request(req1), req0)
        self.assertEqual(get_top_request(req2), req0)

    def test_get_top_site_from_url(self):
        """Unit test for ``get_top_site_from_url`` with context and request
        mocks.

        Test content structure:
        /approot/PloneSite/folder/SubSite/folder
        PloneSite and SubSite implement ISite
        """
        from plone.base.utils import get_top_site_from_url
        from urllib.parse import urlparse
        from zope.component.interfaces import ISite

        class MockContext:
            vh_url = "http://nohost"
            vh_root = ""

            def __init__(self, physical_path):
                self.physical_path = physical_path
                if self.physical_path.split("/")[-1] in (
                    "PloneSite",
                    "SubSite",
                ):
                    alsoProvides(self, ISite)

            @property
            def id(self):
                return self.physical_path.split("/")[-1]

            def absolute_url(self):
                return self.vh_url + self.physical_path[len(self.vh_root) :] or "/"

            def restrictedTraverse(self, path):
                return MockContext(self.vh_root + path)

            def unrestrictedTraverse(self, path):
                return self.restrictedTraverse(path)

        class MockRequest:
            vh_url = "http://nohost"
            vh_root = ""

            def physicalPathFromURL(self, url):
                # Return the physical path from a URL.
                # The outer right '/' is not part of the path.
                path = self.vh_root + urlparse(url).path.rstrip("/")
                return path.split("/")

        # NO VIRTUAL HOSTING

        req = MockRequest()

        # Case 1:
        ctx = MockContext("/approot/PloneSite")
        self.assertEqual(get_top_site_from_url(ctx, req).id, "PloneSite")

        # Case 2
        ctx = MockContext("/approot/PloneSite/folder")
        self.assertEqual(get_top_site_from_url(ctx, req).id, "PloneSite")

        # Case 3:
        ctx = MockContext("/approot/PloneSite/folder/SubSite/folder")
        self.assertEqual(get_top_site_from_url(ctx, req).id, "PloneSite")

        # Case 4, using unicode paths accidentally:
        ctx = MockContext("/approot/PloneSite/folder/SubSite/folder")
        self.assertEqual(get_top_site_from_url(ctx, req).id, "PloneSite")

        # VIRTUAL HOSTING ON SUBSITE

        req = MockRequest()
        req.vh_root = "/approot/PloneSite/folder/SubSite"

        # Case 4:
        ctx = MockContext("/approot/PloneSite/folder/SubSite")
        ctx.vh_root = "/approot/PloneSite/folder/SubSite"
        self.assertEqual(get_top_site_from_url(ctx, req).id, "SubSite")

        # Case 5:
        ctx = MockContext("/approot/PloneSite/folder/SubSite/folder")
        ctx.vh_root = "/approot/PloneSite/folder/SubSite"
        self.assertEqual(get_top_site_from_url(ctx, req).id, "SubSite")

        # Case 6 (VHM points to child of subsite, this bug existed 4 years):
        req = MockRequest()
        req.vh_root = "/approot/PloneSite/folder/SubSite/en"
        ctx = MockContext("/approot/PloneSite/folder/SubSite/en/archives")
        ctx.vh_root = "/approot/PloneSite/folder/SubSite/en"
        self.assertEqual(get_top_site_from_url(ctx, req).id, "en")

    def test_human_readable_size_int(self):
        from plone.base.utils import human_readable_size

        self.assertEqual(human_readable_size(0), "0 KB")
        self.assertEqual(human_readable_size(1), "1 KB")
        size = 1000
        self.assertEqual(human_readable_size(size), "1 KB")
        size += 24
        self.assertEqual(human_readable_size(size), "1.0 KB")
        size += 512
        self.assertEqual(human_readable_size(size), "1.5 KB")
        size *= 1024
        self.assertEqual(human_readable_size(size), "1.5 MB")
        size *= 1024
        self.assertEqual(human_readable_size(size), "1.5 GB")
        size *= 1024
        self.assertEqual(human_readable_size(size), "1.5 TB")
        size *= 1024
        self.assertEqual(human_readable_size(size), "1.5 PB")
        size *= 1024
        self.assertEqual(human_readable_size(size), "1536.0 PB")

    def test_human_readable_size_float(self):
        from plone.base.utils import human_readable_size

        self.assertEqual(human_readable_size(0.0), "0 KB")
        self.assertEqual(human_readable_size(1.0), "1 KB")
        size = 1000.0
        self.assertEqual(human_readable_size(size), "1 KB")
        size += 24.0
        self.assertEqual(human_readable_size(size), "1.0 KB")
        size += 512.0
        self.assertEqual(human_readable_size(size), "1.5 KB")
        size *= 1024.0
        self.assertEqual(human_readable_size(size), "1.5 MB")
        size *= 1024.0
        self.assertEqual(human_readable_size(size), "1.5 GB")
        size *= 1024.0
        self.assertEqual(human_readable_size(size), "1.5 TB")
        size *= 1024
        self.assertEqual(human_readable_size(size), "1.5 PB")
        size *= 1024
        self.assertEqual(human_readable_size(size), "1536.0 PB")

    def test_human_readable_size_special(self):
        from plone.base.utils import human_readable_size

        self.assertEqual(human_readable_size(None), "0 KB")
        self.assertEqual(human_readable_size(""), "0 KB")
        self.assertEqual(human_readable_size("barney"), "barney")

    def test_is_truthy(self):
        """Test the `is_truthy` utility function with different inputs."""
        from plone.base.utils import is_truthy

        self.assertTrue(is_truthy(True))
        self.assertTrue(is_truthy(1))
        self.assertTrue(is_truthy("1"))
        self.assertTrue(is_truthy("TRUE"))
        self.assertTrue(is_truthy("tRUE"))
        self.assertTrue(is_truthy("true"))
        self.assertTrue(is_truthy("y"))
        self.assertTrue(is_truthy("Y"))
        self.assertTrue(is_truthy("yEs"))
        self.assertTrue(is_truthy("yes"))
        self.assertTrue(is_truthy("active"))
        self.assertTrue(is_truthy("Active"))
        self.assertTrue(is_truthy("enAbled"))
        self.assertTrue(is_truthy("on"))
        self.assertTrue(is_truthy("t"))
        self.assertTrue(is_truthy("T"))

        self.assertFalse(is_truthy(None))
        self.assertFalse(is_truthy(False))
        self.assertFalse(is_truthy(0))
        self.assertFalse(is_truthy(2))
        self.assertFalse(is_truthy("0"))
        self.assertFalse(is_truthy("FALSE"))
        self.assertFalse(is_truthy("fALSE"))
        self.assertFalse(is_truthy("false"))
        self.assertFalse(is_truthy("n"))
        self.assertFalse(is_truthy("NO"))
        self.assertFalse(is_truthy("no"))
        self.assertFalse(is_truthy("foo"))

    def test_is_falsy(self):
        """Test the `is_falsy` utility function with different inputs."""
        from plone.base.utils import is_falsy

        self.assertTrue(is_falsy(False))
        self.assertTrue(is_falsy(0))
        self.assertTrue(is_falsy("0"))
        self.assertTrue(is_falsy("f"))
        self.assertTrue(is_falsy("F"))
        self.assertTrue(is_falsy("false"))
        self.assertTrue(is_falsy("FALSE"))
        self.assertTrue(is_falsy("fAlSe"))
        self.assertTrue(is_falsy("n"))
        self.assertTrue(is_falsy("N"))
        self.assertTrue(is_falsy("no"))
        self.assertTrue(is_falsy("NO"))
        self.assertTrue(is_falsy("nO"))
        self.assertTrue(is_falsy("inactive"))
        self.assertTrue(is_falsy("Inactive"))
        self.assertTrue(is_falsy("disabled"))
        self.assertTrue(is_falsy("Disabled"))
        self.assertTrue(is_falsy("off"))
        self.assertTrue(is_falsy("Off"))

        self.assertFalse(is_falsy(True))
        self.assertFalse(is_falsy(1))
        self.assertFalse(is_falsy(2))
        self.assertFalse(is_falsy(None))
        self.assertFalse(is_falsy("foo"))
        self.assertFalse(is_falsy("bar"))

    def test_boolean_value(self):
        """Test the `boolean_value` utility function with different inputs."""
        from plone.base.utils import boolean_value

        self.assertIs(boolean_value(True), True)
        self.assertIs(boolean_value(1), True)
        self.assertIs(boolean_value("yes"), True)
        self.assertIs(boolean_value("true"), True)
        self.assertIs(boolean_value("on"), True)
        self.assertIs(boolean_value("enabled"), True)

        self.assertIs(boolean_value(False), False)
        self.assertIs(boolean_value(0), False)
        self.assertIs(boolean_value("no"), False)
        self.assertIs(boolean_value("false"), False)
        self.assertIs(boolean_value("off"), False)
        self.assertIs(boolean_value("disabled"), False)

        # Unrecognised value with a default returns the default
        self.assertIs(boolean_value("foo", default=True), True)
        self.assertIs(boolean_value("foo", default=False), False)
        self.assertIs(boolean_value(None, default=True), True)

        # Unrecognised value with a non-boolean default raises ValueError
        with self.assertRaises(ValueError):
            boolean_value("foo", default="yes")

        # Unrecognised value without a default raises ValueError
        with self.assertRaises(ValueError):
            boolean_value("foo")
        with self.assertRaises(ValueError):
            boolean_value(None)

    def test_check_for_collision(self):
        """Test the collision for ids in containers.

        There are more complete tests which require a fully set-up Plone site
        in: `Products.CMFPlone.tests.testCheckId`
        """
        from plone.base.utils import _check_for_collision

        class Container(dict):
            def __getattribute__(self, name):
                if name in self:
                    return self[name]
                return object.__getattribute__(self, name)

            def portal_type(self):
                """Necessary to fulfill protocol."""

            def index_html(self):
                """Common attribute - content with id index_html should be
                addable."""

            def some_attr(self):
                """Random attribute - content with id some_attr should not be
                addable."""

        container = Container()
        container["test"] = Container()

        # "test" is already taken
        self.assertIn(
            "There is already an item named",
            _check_for_collision(container, "test"),
        )

        # "tiptop" is not yet taken
        self.assertEqual(
            _check_for_collision(container, "tiptop"),
            None,
        )

        # "index_html" is not yet taken
        self.assertEqual(
            _check_for_collision(container, "index_html"),
            None,
        )

        container["index_html"] = Container()

        # `False` as "index_html" is now taken
        self.assertIn(
            "There is already an item named",
            _check_for_collision(container, "index_html"),
        )

        # Content ids are not addable, if the id is an container attribute.
        self.assertIn(
            "is reserved",
            _check_for_collision(container, "some_attr"),
        )
