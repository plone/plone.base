""" Unit tests for utils module. """

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
