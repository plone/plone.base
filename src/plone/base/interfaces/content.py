from zope import schema
from zope.interface import Interface


class INameFromTitle(Interface):
    """An object that supports getting its name (id) from its title."""

    title = schema.TextLine(
        title="Title",
        description="A title, which will be converted to a name",
        required=True,
    )
