from plone.app.layout.navigation.interfaces import INavigationRoot
from Products.CMFCore.interfaces import ISiteRoot
from zope.interface import Interface


class IPloneSiteRoot(ISiteRoot, INavigationRoot):
    """
    Marker interface for the object which serves as the root of a
    Plone site.
    """


class IMigratingPloneSiteRoot(Interface):
    """
    Marker interface used for migration GenericSetup profiles.
    """


class ITestCasePloneSiteRoot(Interface):
    """
    Marker interface used for test fixture GenericSetup profiles.
    """
