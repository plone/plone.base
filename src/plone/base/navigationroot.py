from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from plone.base.interfaces import INavigationRoot
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility
from zope.component.hooks import getSite


def get_navigation_root(context, relativeRoot=None):
    """Get the path to the root of the navigation tree.

    If a relativeRoot argument is provided, navigation root is computed from
    portal path and this relativeRoot.

    If no relativeRoot argument is provided, and there is a root value set in
    portal_properties, navigation root path is computed from
    portal path and this root value.

    IMPORTANT !!!
    Previous paragraphs imply relativeRoot is relative to the Plone portal.

    Else, a root must be computed: loop from the context to the portal,
    through parents, looking for an object implementing INavigationRoot.
    Return the path of that root.
    """
    try:
        # URLTool is a portal tool from CMFCore
        portal_url = getToolByName(context, "portal_url")
    except AttributeError:
        return "/".join(getSite().getPhysicalPath())

    if relativeRoot is None:
        # fetch from portal_properties
        registry = getUtility(IRegistry)
        relativeRoot = registry.get("plone.root", None)

    # if relativeRoot has a meaningful value,
    if relativeRoot and relativeRoot != "/":
        # use it

        # while taking care of case where
        # relativeRoot is not starting with a '/'
        if relativeRoot[0] != "/":
            relativeRoot = "/" + relativeRoot

        portalPath = portal_url.getPortalPath()
        return portalPath + relativeRoot

    # compute the root
    portal = portal_url.getPortalObject()
    root = get_navigation_root_object(context, portal)
    return "/".join(root.getPhysicalPath())


def get_navigation_root_object(context, portal):
    obj = context
    while not INavigationRoot.providedBy(obj) and aq_base(obj) is not aq_base(portal):
        parent = aq_parent(aq_inner(obj))
        if parent is None:
            return obj
        obj = parent
    return obj
