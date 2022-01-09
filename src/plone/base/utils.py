from Acquisition import aq_get
from urllib.parse import urlparse
from zope.component import getMultiAdapter
from zope.component.hooks import getSite
from zope.component.interfaces import ISite
from zope.deferredimport.deferredmodule import deprecated


SIZE_CONST = {"KB": 1024, "MB": 1024 * 1024, "GB": 1024 * 1024 * 1024}
SIZE_ORDER = ("GB", "MB", "KB")


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


def safeToInt(value, default=0):
    """Convert value to integer or just return 0 if we can't

    >>> safeToInt(45)
    45

    >>> safeToInt("42")
    42

    >>> safeToInt("spam")
    0

    >>> safeToInt([])
    0

    >>> safeToInt(None)
    0

    >>> safeToInt(None, default=-1)
    -1
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_text(value, encoding="utf-8") -> str:
    """Converts a value to text, even it is already a text string.

    >>> from Products.CMFPlone.utils import safe_unicode
    >>> test_bytes = u'\u01b5'.encode('utf-8')
    >>> safe_unicode('spam') == u'spam'
    True
    >>> safe_unicode(b'spam') == u'spam'
    True
    >>> safe_unicode(u'spam') == u'spam'
    True
    >>> safe_unicode(u'spam'.encode('utf-8')) == u'spam'
    True
    >>> safe_unicode(test_bytes) == u'\u01b5'
    True
    >>> safe_unicode(u'\xc6\xb5'.encode('iso-8859-1')) == u'\u01b5'
    True
    >>> safe_unicode(test_bytes, encoding='ascii') == u'\u01b5'
    True
    >>> safe_unicode(1) == 1
    True
    >>> print(safe_unicode(None))
    None
    """
    if isinstance(value, bytes):
        try:
            value = str(value, encoding)
        except (UnicodeDecodeError):
            value = value.decode("utf-8", "replace")
    return value


def safe_bytes(value, encoding="utf-8") -> bytes:
    """Convert text to bytes of the specified encoding."""
    if isinstance(value, str):
        value = value.encode(encoding)
    return value


def get_installer(context, request=None):
    if request is None:
        request = aq_get(context, "REQUEST", None)
    view = getMultiAdapter((context, request), name="installer")
    return view


def get_top_request(request):
    """Get highest request from a subrequest."""

    def _top_request(req):
        parent_request = req.get("PARENT_REQUEST", None)
        return _top_request(parent_request) if parent_request else req

    return _top_request(request)


def get_top_site_from_url(context, request):
    """Find the top-most site, which is still in the url path.

    If the current context is within a subsite within a PloneSiteRoot and no
    virtual hosting is in place, the PloneSiteRoot is returned.
    When at the same context but in a virtual hosting environment with the
    virtual host root pointing to the subsite, it returns the subsite instead
    the PloneSiteRoot.

    For this given content structure:

    /Plone/Subsite

    It should return the following in these cases:

    - No virtual hosting, URL path: /Plone, Returns: Plone Site
    - No virtual hosting, URL path: /Plone/Subsite, Returns: Plone
    - Virtual hosting roots to Subsite, URL path: /, Returns: Subsite
    """
    site = getSite()
    try:
        url_path = urlparse(context.absolute_url()).path.split("/")
        for idx in range(len(url_path)):
            _path = "/".join(url_path[: idx + 1]) or "/"
            site_path = "/".join(request.physicalPathFromURL(_path)) or "/"
            _site = context.restrictedTraverse(site_path)
            if ISite.providedBy(_site):
                break
        if _site:
            site = _site
    except (ValueError, AttributeError):
        # On error, just return getSite.
        # Refs: https://github.com/plone/plone.app.content/issues/103
        # Also, TestRequest doesn't have physicalPathFromURL
        pass
    return site
