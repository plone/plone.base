from zope.interface import Interface


class IImageScalesAdapter(Interface):
    """Return a list of image scales for the given context."""

    def __init__(context, request):
        """Adapts context and the request."""

    def __call__():
        """Call IImageScalesFieldAdapter on all fields."""


class IImageScalesFieldAdapter(Interface):
    """Adapter from field to image_scales.

    This is called by an IImageScalesAdapter.
    Default expectation is that there will be adapters for image fields
    and not for others.  But adapters for text fields or relation fields
    are imaginable.
    """

    def __init__(field, context, request):
        """Adapts field, context and request."""

    def __call__():
        """Returns JSON compatible python data."""
