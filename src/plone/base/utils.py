from . import PloneMessageFactory as _
from .interfaces import ISearchSchema
from AccessControl import Unauthorized
from Acquisition import aq_base
from Acquisition import aq_get
from Acquisition import aq_parent
from DateTime import DateTime
from plone.registry.interfaces import IRegistry
from Products.CMFCore.interfaces import ITypesTool
from Products.CMFCore.utils import getToolByName
from urllib.parse import urlparse
from zExceptions import NotFound
from ZODB.POSException import ConflictError
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.component.interfaces import ISite
from zope.deprecation import deprecate
from zope.i18n import translate
from zope.publisher.interfaces.browser import IBrowserRequest

import logging
import transaction


logger = logging.getLogger("Plone")

SIZE_CONST = {
    "KB": 1024,
    "MB": 1024**2,
    "GB": 1024**3,
    "TB": 1024**4,
    "PB": 1024**5,
}
SIZE_ORDER = ("PB", "TB", "GB", "MB", "KB")

_marker = dict()


def human_readable_size(size):
    """Get a human readable size string."""
    smaller = SIZE_ORDER[-1]

    # if the size is a float, then make it an int
    # happens for large files
    try:
        size = int(size)
    except (ValueError, TypeError):
        pass

    if not size:
        return f"0 {smaller}"

    if not isinstance(size, int):
        return size

    if size < SIZE_CONST[smaller]:
        return f"1 {smaller}"

    for c in SIZE_ORDER:
        if size // SIZE_CONST[c] > 0:
            break
    return f"{float(size / float(SIZE_CONST[c])):.1f} {c}"


def safe_int(value, default=0):
    """Convert value to integer or just return 0 if we can't

    >>> safe_int(45)
    45

    >>> safe_int("42")
    42

    >>> safe_int("spam")
    0

    >>> safe_int([])
    0

    >>> safe_int(None)
    0

    >>> safe_int(None, default=-1)
    -1
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


@deprecate("Use plone.base.utils.safe_int instead (will be removed in Plone 7)")
def safeToInt(value, default=0):
    return safe_int(value, default)


def safe_text(value, encoding="utf-8") -> str:
    """Converts a value to text, even it is already a text string.

    >>> test_bytes = u'\u01b5'.encode('utf-8')
    >>> safe_text('spam') == u'spam'
    True
    >>> safe_text(b'spam') == u'spam'
    True
    >>> safe_text(u'spam') == u'spam'
    True
    >>> safe_text(u'spam'.encode('utf-8')) == u'spam'
    True
    >>> safe_text(test_bytes) == u'\u01b5'
    True
    >>> safe_text(u'\xc6\xb5'.encode('iso-8859-1')) == u'\u01b5'
    True
    >>> safe_text(test_bytes, encoding='ascii') == u'\u01b5'
    True
    >>> safe_text(1) == 1
    True
    >>> print(safe_text(None))
    None
    """
    if isinstance(value, bytes):
        try:
            value = str(value, encoding)
        except UnicodeDecodeError:
            value = value.decode("utf-8", "replace")
    return value


def safe_bytes(value, encoding="utf-8") -> bytes:
    """Convert text to bytes of the specified encoding."""
    if isinstance(value, str):
        value = value.encode(encoding)
    return value


def safe_hasattr(obj, name, _marker=object()):
    """Make sure we don't mask exceptions like hasattr().

    We don't want exceptions other than AttributeError to be masked,
    since that too often masks other programming errors.
    Three-argument getattr() doesn't mask those, so we use that to
    implement our own hasattr() replacement.
    """
    return getattr(obj, name, _marker) is not _marker


def base_hasattr(obj, name):
    """Like safe_hasattr, but also disables acquisition."""
    return safe_hasattr(aq_base(obj), name)


def safe_callable(obj):
    """Make sure our callable checks are ConflictError safe."""
    if safe_hasattr(obj, "__class__"):
        if safe_hasattr(obj, "__call__"):
            return True
        return isinstance(obj, type)
    return callable(obj)


def get_empty_title(context, translated=True):
    """Returns string to be used for objects with no title or id"""
    # The default is an extra fancy unicode ellipsis,
    empty = b"\x5b\xc2\xb7\xc2\xb7\xc2\xb7\x5d".decode("utf8")
    if translated:
        if context is not None:
            if not IBrowserRequest.providedBy(context):
                context = aq_get(context, "REQUEST", None)
        empty = translate("title_unset", domain="plone", context=context, default=empty)
    return empty


def pretty_title_or_id(context, obj, empty_value=_marker):
    """Return the best possible title or id of an item, regardless
    of whether obj is a catalog brain or an object, but returning an
    empty title marker if the id is not set (i.e. it's auto-generated).
    """
    title = None
    if base_hasattr(obj, "Title"):
        title = getattr(obj, "Title", None)
    if safe_callable(title):
        title = title()
    if title:
        return title
    item_id = getattr(obj, "getId", None)
    if safe_callable(item_id):
        item_id = item_id()
    if item_id is not None:
        return item_id
    if empty_value is _marker:
        empty_value = get_empty_title(context)
    return empty_value


def get_installer(context, request=None):
    if request is None:
        request = aq_get(context, "REQUEST", None)
    view = getMultiAdapter((context, request), name="installer")
    return view


def is_expired(content):
    """Find out if the object is expired (copied from skin script)"""

    expiry = None

    # NOTE: We also accept catalog brains as 'content' so that the
    # catalog-based folder_contents will work. It's a little magic, but
    # it works.

    # ExpirationDate should have an ISO date string, which we need to
    # convert to a DateTime

    # Try DC accessor first
    if base_hasattr(content, "ExpirationDate"):
        expiry = content.ExpirationDate

    # Try the direct way
    if not expiry and base_hasattr(content, "expires"):
        expiry = content.expires

    # See if we have a callable
    if safe_callable(expiry):
        expiry = expiry()

    # Convert to DateTime if necessary, ExpirationDate may return 'None'
    if expiry and expiry != "None" and isinstance(expiry, str):
        expiry = DateTime(expiry)

    if isinstance(expiry, DateTime) and expiry.isPast():
        return 1
    return 0


def get_top_request(request):
    """Get highest request from a subrequest."""

    def _top_request(req):
        parent_request = req.get("PARENT_REQUEST", None)
        return _top_request(parent_request) if parent_request else req

    return _top_request(request)


def get_top_site_from_url(context, request):
    """
    Find the first ISite object that appears in the pre-virtual-hosting URL
    path, falling back to the object pointed by the virtual hosting root.

    Use this method if you need a "root object" reference to generate URLs
    that will be used by, and will work correctly from the standpoint of,
    *browser* code (JavaScript / XML HTTP requests) after virtual hosting has
    been applied.  *Never* use this to get to a site root in Plone server code
    -- it is not appropriate for that use.

    If the current context is within a subsite within a PloneSiteRoot and no
    virtual hosting is in place, the PloneSiteRoot is returned.
    When at the same context but in a virtual hosting environment with the
    virtual host root pointing to the subsite, it returns the subsite instead
    the PloneSiteRoot.  Finally, if the virtual hosting environment points to
    a *child* of a site/subsite, that child returns instead of the site/subsite.

    For this given content structure:

    /Plone/Subsite:
      /file
      /en-US
        /folder
          /image

    It should return the following in these cases:

    - No virtual hosting
      URL path:              /Plone
      Object accessed:       /Plone
      Returns:               Plone

    - No virtual hosting
      URL path:              /Plone/Subsite
      Object accessed:       /Plone/Subsite
      Returns:               Plone

    - Virtual hosting root:  /Plone/Subsite
      URL path:              /
      Object accessed:       /Plone/Subsite
      Returns:               Subsite

    - Virtual hosting root:  /Plone/Subsite
      URL path:              /file
      Object accessd:        /Plone/Subsite/file
      Returns:               Subsite

    - Virtual hosting root:  /Plone/Subsite/en-US
      URL path:              /folder/image
      Object accessed:       /Plone/Subsite/en-US/folder/image
      Returns:               Subsite/en-US
      (in this last case -- common with p.a.multilingual and usually described
       as subdomain hosting for languages -- no Site object is visible TTW,
       so it must return the topmost visible container, since the callees
       need an object with a valid, TTW-visible URL to do their work.)
    """
    site = getSite()
    try:
        # This variable collects all sites found during the traversal that
        # takes place below, which only includes objects visible via VHM.
        subsites = []
        # This variable collect the topmost objects found during the
        # traversal below, as fallback in case there are no sites found
        # during the traversal.
        topmosts = []
        url_path = urlparse(context.absolute_url()).path.split("/")
        for idx in range(len(url_path)):
            _path = "/".join(url_path[: idx + 1]) or "/"
            site_path = "/".join(request.physicalPathFromURL(_path)) or "/"
            # The following line is fine.  We do a restrictedTraverse
            # below to resolve the actual object, so the user (technically,
            # the browser) cannot ever get a reference to an object it does
            # not have permission to.
            try:
                _site = context.unrestrictedTraverse(site_path)
            except NotFound:
                # Oh.  This path is not findable.  So we will not consider
                # it below as a thing we can return to stand in for ISite.
                continue
            if ISite.providedBy(_site):
                subsites.append(idx)
            else:
                topmosts.append(idx)
        # Pick the subsite to return.
        # If no subsite was found, return the top site.
        # If at some point a subsite was found, return the
        # rootmost of all subsites.
        # With VHM, sometimes the topmost site is not actually
        # in the client URL, so in that case we fall back to
        # the topmost accessible object within the client URL.
        try:
            _path_idx = subsites[0]
        except IndexError:
            _path_idx = topmosts[0]
        _path = "/".join(url_path[: _path_idx + 1]) or "/"
        site_path = "/".join(request.physicalPathFromURL(_path)) or "/"
        site = context.restrictedTraverse(site_path)
    except (ValueError, AttributeError):
        # On error, just return getSite.
        # Refs: https://github.com/plone/plone.app.content/issues/103
        # Also, TestRequest doesn't have physicalPathFromURL
        pass
    return site


def transaction_note(note):
    """Write human legible note"""
    T = transaction.get()
    if (len(T.description) + len(note)) >= 65533:
        logger.warn("Transaction note too large omitting %s" % str(note))
    else:
        T.note(safe_text(note))


def check_id(
    context, id=None, required=0, alternative_id=None, contained_by=None, **kwargs
):
    """Test an id to make sure it is valid.

    This used to be in Products/CMFPlone/skins/plone_scripts/check_id.py.

    Returns an error message if the id is bad or None if the id is good.
    Parameters are as follows:

        id - the id to check

        required - if False, id can be the empty string

        alternative_id - an alternative value to use for the id
        if the id is empty or autogenerated

    Accept keyword arguments for compatibility with the fallback
    in Products.validation.

    Note: The reason the id is included is to handle id error messages for
    such objects as files and images that supply an alternative id when an
    id is auto-generated.
    If you say "There is already an item with this name in this folder"
    for an image that has the Name field populated with an autogenerated id,
    it can cause some confusion; since the real problem is the name of
    the image file name, not in the name of the autogenerated id.
    """

    def xlate(message):
        ts = getToolByName(context, "translation_service", None)
        if ts is None:
            return message
        return ts.translate(message, context=context.REQUEST)

    # if an alternative id has been supplied, see if we need to use it
    if alternative_id and not id:
        id = alternative_id

    # make sure we have an id if one is required
    if not id:
        if required:
            return xlate(_("Please enter a name."))

        # Id is not required and no alternative was specified, so assume the
        # object's id will be context.getId(). We still should check to make
        # sure context.getId() is OK to handle the case of pre-created objects
        # constructed via portal_factory.  The main potential problem is an id
        # collision, e.g. if portal_factory autogenerates an id that already
        # exists.

        id = context.getId()

    #
    # do basic id validation
    #

    # check for reserved names
    if id in (
        "login",
        "layout",
        "plone",
        "zip",
        "properties",
    ):
        return xlate(_("${name} is reserved.", mapping={"name": id}))

    # check for bad characters
    plone_utils = getToolByName(context, "plone_utils", None)
    if plone_utils is not None:
        bad_chars = plone_utils.bad_chars(id)
        if len(bad_chars) > 0:
            bad_chars = "".join(bad_chars).decode("utf-8")
            decoded_id = id.decode("utf-8")
            return xlate(
                _(
                    "${name} is not a legal name. The following characters are "
                    "invalid: ${characters}",
                    mapping={"name": decoded_id, "characters": bad_chars},
                )
            )

    # check for a catalog index
    portal_catalog = getToolByName(context, "portal_catalog", None)
    if portal_catalog is not None:
        if id in list(portal_catalog.indexes()) + list(portal_catalog.schema()):
            return xlate(_("${name} is reserved.", mapping={"name": id}))

    # id is good; decide if we should check for id collisions
    if contained_by is not None:
        # Always check for collisions if a container was passed
        # via the contained_by parameter.
        checkForCollision = True
    else:
        # if we have an existing object, only check for collisions
        # if we are changing the id
        checkForCollision = context.getId() != id

    # check for id collisions
    if not checkForCollision:
        # We are done.
        return
    # handles two use cases:
    # 1. object has not yet been created and we don't know where it will be
    # 2. object has been created and checking validity of id within
    #    container
    if contained_by is None:
        try:
            contained_by = context.getParentNode()
        except Unauthorized:
            return  # nothing we can do
    try:
        result = _check_for_collision(contained_by, id, **kwargs)
    except Unauthorized:
        # There is a permission problem. Safe to assume we can't use this id.
        return xlate(_("${name} is reserved.", mapping={"name": id}))
    if result is not None:
        result = xlate(
            result,
        )
    return result


def _check_for_collision(contained_by, cid, **kwargs):
    """Check for collisions of an object id in a container.

    Accept keyword arguments for compatibility with the fallback
    in Products.validation.

    When this was still a Python skin script, some security checks
    would have been done automatically and caught by some
    'except Unauthorized' lines.  Now, in unrestricted Python
    code, we explicitly check.  But not all checks make sense.  If you don't
    have the 'Access contents information' permission, theoretically
    you should not be able to check for an existing conflicting id,
    but it seems silly to then pretend that there is no conflict.

    For safety, we let the check_id
    function do a try/except Unauthorized when calling us.
    """
    # Check for an existing object.
    if cid in contained_by:
        existing_obj = getattr(contained_by, cid, None)
        if getattr(aq_base(existing_obj), "portal_type", _marker) is not _marker:
            return _(
                "There is already an item named ${name} in this folder.",
                mapping={"name": cid},
            )

    # containers may have a field / attribute of the same name
    if base_hasattr(contained_by, cid):
        return _("${name} is reserved.", mapping={"name": cid})

    # containers may implement this hook to further restrict ids
    if getattr(aq_base(contained_by), "checkValidId", _marker) is not _marker:
        try:
            contained_by.checkValidId(cid)
        except ConflictError:
            raise
        except Exception:
            return _("${name} is reserved.", mapping={"name": cid})

    # make sure we don't collide with any parent method aliases
    types_tool = getToolByName(contained_by, "types_tool", None)
    if types_tool is not None:
        parentFti = types_tool.getTypeInfo(contained_by)
        if parentFti is not None:
            aliases = parentFti.getMethodAliases()
            if aliases is not None and cid in aliases.keys():
                return _("${name} is reserved.", mapping={"name": cid})

    # Lastly, we want to disallow the id of any of the tools in the portal
    # root, as well as any object that can be acquired via portal_skins.
    # However, we do want to allow overriding of *content* in the object's
    # parent path, including the portal root.

    if cid == "index_html":
        # always allow index_html
        return
    portal = getSite()
    if portal and cid in portal.contentIds():
        # Fine to use the same id as a *content* item from the root.
        return
    # It is allowed to give an object the same id as another
    # container in it's acquisition path as long as the
    # object is outside the portal.
    outsideportal = getattr(aq_parent(portal), cid, None)
    insideportal = getattr(portal, cid, None)
    if (
        insideportal is not None
        and outsideportal is not None
        and aq_base(outsideportal) == aq_base(insideportal)
    ):
        return
    # but not other things
    if getattr(portal, cid, None) is not None:
        return _("${name} is reserved.", mapping={"name": cid})


def get_user_friendly_types(types_list=None):
    """List of types which are considered "user friendly" for search and selection purposes.

    This is the list of types available in the portal, minus those defined in the
    `types_not_searched` property in registry, if it exists.

    If typesList is given, this is used as the base list;
    else all types from portal_types are used.
    """
    registry = getUtility(IRegistry)
    search_settings = registry.forInterface(ISearchSchema, prefix="plone")
    ttool = getUtility(ITypesTool)
    types = set(ttool.keys())
    if types_list:
        types = {t for t in types_list if t in types}
    friendly_types = types - set(search_settings.types_not_searched)
    return list(friendly_types)


def unrestricted_construct_instance(type_name, container, id, *args, **kw):
    """Create an object without performing security checks

    invokeFactory and fti.constructInstance perform some security checks
    before creating the object. Use this function instead if you need to
    skip these checks.

    This method uses
    CMFCore.TypesTool.FactoryTypeInformation._constructInstance
    to create the object without security checks.
    """
    id = str(id)
    typesTool = getToolByName(container, "portal_types")
    fti = typesTool.getTypeInfo(type_name)
    if not fti:
        raise ValueError("Invalid type %s" % type_name)

    return fti._constructInstance(container, id, *args, **kw)
