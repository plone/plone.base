from AccessControl.SecurityManagement import newSecurityManager
from plone.base.navigationroot import get_navigation_root_object
from Products.CMFCore.interfaces import ITypesTool
from Products.CMFCore.PortalFolder import PortalFolder
from Products.CMFCore.PortalFolder import PortalFolderFactory
from Products.CMFCore.testing import TraversingEventZCMLLayer
from Products.CMFCore.tests.base.dummy import DummySite
from Products.CMFCore.tests.base.dummy import DummyUserFolder
from Products.CMFCore.tests.base.testcase import SecurityTest
from Products.CMFCore.tests.base.tidata import FTIDATA_DUMMY
from Products.CMFCore.TypesTool import FactoryTypeInformation
from Products.CMFCore.TypesTool import TypesTool
from zope.component import getSiteManager
from zope.component.interfaces import IFactory


class PortalFolderFactoryTests(SecurityTest):
    layer = TraversingEventZCMLLayer
    _PORTAL_TYPE = "Test Folder"

    def setUp(self):
        # simple dummy site
        # setUp see Products.CMFCore.tests.test_PortalFolder.py
        SecurityTest.setUp(self)
        self.portal = DummySite("site").__of__(self.app)
        acl_users = self.portal._setObject("acl_users", DummyUserFolder())
        newSecurityManager(None, acl_users.all_powerful_Oz)

        self.ttool = ttool = TypesTool()
        ttool._setObject(
            self._PORTAL_TYPE,
            FactoryTypeInformation(
                id=self._PORTAL_TYPE,
                title="Folder or Directory",
                meta_type=PortalFolder.meta_type,
                factory="cmf.folder",
                filter_content_types=0,
            ),
        )
        ttool._setObject(
            "Dummy Content", FactoryTypeInformation(**FTIDATA_DUMMY[0].copy())
        )
        sm = getSiteManager()
        sm.registerUtility(ttool, ITypesTool)
        sm.registerUtility(PortalFolderFactory, IFactory, "cmf.folder")

        self.f = self.portal._setObject("container", PortalFolder("container"))
        self.f._setPortalTypeName(self._PORTAL_TYPE)

    def test_get_navigation_root_object_no_context(self):
        """
        If you don't know the context then you also don't know what the
        navigation root is.
        """
        self.assertEqual(None, get_navigation_root_object(None, self.portal))
