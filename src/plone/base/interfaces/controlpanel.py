from .basetool import IPloneBaseTool
from plone import schema
from plone.base import PloneMessageFactory as _
from Products.CMFCore.utils import getToolByName
from zope.component.hooks import getSite
from zope.interface import Attribute
from zope.interface import implementer
from zope.interface import Interface
from zope.interface import Invalid
from zope.interface import invariant
from zope.schema import ValidationError
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

import json


def dump_json_to_text(obj):
    """Encode an obj into a text"""
    text = json.dumps(obj, indent=4)
    if not isinstance(text, str):
        text = text.decode("utf8")
    return text


ROBOTS_TXT = """Sitemap: {portal_url}/sitemap.xml.gz

# Define access-restrictions for robots/spiders
# http://www.robotstxt.org/wc/norobots.html



# By default we allow robots to access all areas of our site
# already accessible to anonymous users

User-agent: *
Disallow:



# Add Googlebot-specific syntax extension to exclude forms
# that are repeated for each piece of content in the site
# the wildcard is only supported by Googlebot
# http://www.google.com/support/webmasters/bin/answer.py?answer=40367&ctx=sibling

User-Agent: Googlebot
Disallow: /*?
Disallow: /*atct_album_view$
Disallow: /*folder_factories$
Disallow: /*folder_summary_view$
Disallow: /*login_form$
Disallow: /*mail_password_form$
Disallow: /@@search
Disallow: /*search_rss$
Disallow: /*sendto_form$
Disallow: /*summary_view$
Disallow: /*thumbnail_view$
Disallow: /*view$
"""


def validate_json(value):
    try:
        json.loads(value)
    except ValueError as exc:

        class JSONError(ValidationError):
            __doc__ = _(
                "Must be empty or a valid JSON-formatted "
                "configuration – ${message}.",
                mapping={"message": str(exc)},
            )

        raise JSONError(value)

    return True


class IControlPanel(IPloneBaseTool):
    """Interface for the ControlPanel"""

    def registerConfiglet(
        id,
        name,
        action,
        condition="",
        permission="",
        category="Plone",
        visible=1,
        appId=None,
        imageUrl=None,
        description="",
        REQUEST=None,
    ):
        """Registration of a Configlet"""

    def unregisterConfiglet(id):
        """unregister Configlet"""

    def unregisterApplication(appId):
        """unregister Application with all configlets"""

    def getGroupIds():
        """list of the group ids"""

    def getGroups():
        """list of groups as dicts with id and title"""

    def enumConfiglets(group=None):
        """lists the Configlets of a group, returns them as dicts by
        calling .getAction() on each of them"""


class IEditingSchema(Interface):
    available_editors = schema.List(
        title=_("Available editors"),
        description=_("Available editors in the portal."),
        default=["TinyMCE", "None"],
        value_type=schema.TextLine(),
        missing_value=[],
        required=True,
    )

    default_editor = schema.Choice(
        title=_("Default editor"),
        description=_(
            "Select the default wysiwyg "
            "editor. Users will be able to choose their "
            "own or select to use the site default."
        ),
        default="TinyMCE",
        missing_value=set(),
        vocabulary="plone.app.vocabularies.AvailableEditors",
        required=True,
    )

    ext_editor = schema.Bool(
        title=_("Enable External Editor feature"),
        description=_(
            "Determines if the external editor "
            "feature is enabled. This feature requires a "
            "special client-side application installed. The "
            "users also have to enable this in their "
            "preferences."
        ),
        default=False,
        required=False,
    )

    enable_link_integrity_checks = schema.Bool(
        title=_("Enable link integrity checks"),
        description=_(
            "Determines if the users should get "
            "warnings when they delete or move content that "
            "is linked from inside the site."
        ),
        default=True,
        required=False,
    )

    lock_on_ttw_edit = schema.Bool(
        title=_("Enable locking for through-the-web edits"),
        description=_(
            "Disabling locking here will only "
            "affect users editing content through the "
            "Plone web UI.  Content edited via WebDAV "
            "clients will still be subject to locking."
        ),
        default=True,
        required=False,
    )

    subjects_of_navigation_root = schema.Bool(
        title=_("Limit tags/keywords to the current navigation root"),
        description=_(
            "Limit tags aka keywords vocabulary used for Tags field and "
            "in searches to the terms used inside the subtree of the current "
            "navigation root. This can be used together with Plone's "
            "multilingual extension plone.app.multilingual to only offer "
            "keywords of the current selected language. Other addons may "
            "utilize this feature for its specific purposes."
        ),
        default=False,
        required=False,
    )


class ITagAttrPair(Interface):
    tags = schema.TextLine(title="tags")
    attributes = schema.TextLine(title="attributes")


@implementer(ITagAttrPair)
class TagAttrPair:
    def __init__(self, tags="", attributes=""):
        self.tags = tags
        self.attributes = attributes


class IFilterSchema(Interface):
    """Combined schema for the adapter lookup."""

    # class IFilterTagsSchema(Interface):

    disable_filtering = schema.Bool(
        title=_("Disable HTML filtering"),
        description=_(
            "Warning: disabling this can be dangerous. "
            "Only disable if you know what you are doing."
        ),
        default=False,
        required=False,
    )

    nasty_tags = schema.List(
        title=_("Nasty tags"),
        description=_(
            "These tags and their content are completely blocked "
            "when a page is saved or rendered. They are only deleted"
            " if they are not marked as valid_tags"
        ),
        default=["style", "object", "embed", "applet", "script", "meta"],
        value_type=schema.TextLine(),
        missing_value=[],
        required=False,
    )

    valid_tags = schema.List(
        title=_("Valid tags"),
        description=_("A list of valid tags which will be not filtered out."),
        default=[
            "a",
            "abbr",
            "acronym",
            "address",
            "article",
            "aside",
            "audio",
            "b",
            "bdo",
            "big",
            "blockquote",
            "body",
            "br",
            "canvas",
            "caption",
            "cite",
            "code",
            "col",
            "colgroup",
            "command",
            "datalist",
            "dd",
            "del",
            "details",
            "dfn",
            "dialog",
            "div",
            "dl",
            "dt",
            "em",
            "figure",
            "figcaption",
            "footer",
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
            "head",
            "header",
            "hgroup",
            "hr",
            "html",
            "i",
            "iframe",
            "img",
            "ins",
            "kbd",
            "keygen",
            "li",
            "map",
            "mark",
            "meter",
            "nav",
            "ol",
            "output",
            "p",
            "pre",
            "picture",
            "progress",
            "q",
            "rp",
            "rt",
            "ruby",
            "samp",
            "section",
            "small",
            "source",
            "span",
            "strong",
            "sub",
            "summary",
            "sup",
            "table",
            "tbody",
            "td",
            "tfoot",
            "th",
            "thead",
            "time",
            "title",
            "tr",
            "tt",
            "u",
            "ul",
            "var",
            "video",
        ],
        value_type=schema.TextLine(),
        missing_value=[],
        required=False,
    )

    custom_attributes = schema.List(
        title=_("Custom attributes"),
        description=_("These attributes are additionally allowed."),
        default=[
            "style",
            "controls",
            "poster",
            "autoplay",
            "loading",
            "srcset",
            "sizes",
            "open",
        ],
        value_type=schema.TextLine(),
        missing_value=[],
        required=False,
    )


class ITinyMCELayoutSchema(Interface):
    """This interface defines the layout properties."""

    resizing = schema.Bool(
        title=_("Enable resizing the editor window."),
        description=_(
            "This option gives you the ability to enable/disable "
            "resizing the editor window. "
        ),
        default=True,
        required=False,
    )

    autoresize = schema.Bool(
        title=_("Enable auto resizing of the editor window."),
        description=_(
            "This option gives you the ability to enable/disable "
            "auto resizing the editor window depending "
            "on the content."
        ),
        default=False,
        required=False,
    )

    inline = schema.Bool(
        title=_("Run TinyMCE in inline mode."),
        description=_(
            "The inline editing mode is useful when creating user "
            "experiences where you want the editing view of the page "
            "to be merged with the reading view of the page."
        ),
        default=False,
        required=False,
    )

    # TODO: add validation to assert % and px in the value
    editor_width = schema.TextLine(
        title=_("Editor width"),
        description=_(
            "This option gives you the ability to specify the "
            "width of the editor (like 100% or 400px)."
        ),
        default=None,
        required=False,
    )

    # TODO: add validation to assert % and px in the value
    editor_height = schema.TextLine(
        title=_("Editor height"),
        description=_(
            "This option gives you the ability to specify the "
            "height of the editor in pixels. "
            "If auto resize is enabled this value is used "
            "as minimum height."
        ),
        default=None,
        required=False,
    )

    content_css = schema.List(
        title=_("Choose the CSS used in WYSIWYG Editor Area"),
        description=_(
            "This option enables you to specify CSS files "
            "that will be used within the the editable area of the editor "
            "(e.g. ++plone++mystyles/tinymce.css). "
            "These styles will also appear in the Format list of TinyMCE."
            "In addition to what is listed here, "
            "the CSS file defined under 'tinymce-content-css'"
            " in a theme manifest.cfg is also added."
        ),
        value_type=schema.TextLine(),
        missing_value=[],
        default=[],
        required=False,
    )

    header_styles = schema.List(
        title=_("Header styles"),
        description=_("Name|tag"),
        value_type=schema.TextLine(),
        missing_value=[],
        default=[
            "Header 1|h1",
            "Header 2|h2",
            "Header 3|h3",
            "Header 4|h4",
            "Header 5|h5",
            "Header 6|h6",
        ],
    )

    inline_styles = schema.List(
        title=_("Inline styles"),
        description=_("Name|format|icon"),
        value_type=schema.TextLine(),
        missing_value=[],
        default=[
            "Bold|bold|bold",
            "Italic|italic|italic",
            "Underline|underline|underline",
            "Strikethrough|strikethrough|strike-through",
            "Superscript|superscript|superscript",
            "Subscript|subscript|subscript",
            "Code|code|sourcecode",
            "Text in 2 columns|textcolumns2",
            "Text in 3 columns|textcolumns3",
        ],
    )

    block_styles = schema.List(
        title=_("Block styles"),
        description=_("Name|format"),
        value_type=schema.TextLine(),
        missing_value=[],
        default=["Paragraph|p", "Blockquote|blockquote", "Div|div", "Pre|pre"],
    )

    alignment_styles = schema.List(
        title=_("Alignment styles"),
        description=_("Name|format|icon"),
        value_type=schema.TextLine(),
        missing_value=[],
        default=[
            "Left|alignleft|align-left",
            "Center|aligncenter|align-center",
            "Right|alignright|align-right",
            "Justify|alignjustify|align-justify",
        ],
    )

    table_styles = schema.List(
        title=_("Table styles"),
        description=_("Name|class"),
        value_type=schema.TextLine(),
        missing_value=[],
        default=[
            "Listing|listing",
            "Listing compact|listing-compact",
            "Subdued grid|plain",
            "Invisible Grid|invisible-grid",
        ],
    )

    formats = schema.Text(
        title=_("Formats"),
        description=_(
            "Enter a JSON-formatted style format configuration. "
            "A format is for example the style that get applied when "
            "you press the bold button inside the editor. "
            "See https://www.tiny.cloud/docs/tinymce/latest/content-formatting/"
        ),
        constraint=validate_json,
        default=dump_json_to_text(
            {
                "discreet": {"inline": "span", "classes": "discreet"},
                "clearfix": {"block": "div", "classes": "clearfix"},
                "alignleft": {
                    "selector": "p,h1,h2,h3,h4,h5,h6,td,th,div,ul,ol,li,table",
                    "classes": "text-start",
                },
                "aligncenter": {
                    "selector": "p,h1,h2,h3,h4,h5,h6,td,th,div,ul,ol,li,table",
                    "classes": "text-center",
                },
                "alignright": {
                    "selector": "p,h1,h2,h3,h4,h5,h6,td,th,div,ul,ol,li,table",
                    "classes": "text-end",
                },
                "alignjustify": {
                    "selector": "p,h1,h2,h3,h4,h5,h6,td,th,div,ul,ol,li,table",
                    "classes": "text-justify",
                },
                "textcolumns2": {"selector": "p", "classes": "text-columns-2"},
                "textcolumns3": {"selector": "p", "classes": "text-columns-3"},
            }
        ),
        required=True,
    )


class ITinyMCEPluginSchema(Interface):
    """This interface defines the toolbar properties."""

    plugins = schema.List(
        title=_("label_tinymce_plugins", default="Editor plugins"),
        description=_(
            "help_tinymce_plugins", default=("Select plugins to include with tinymce")
        ),
        value_type=schema.Choice(
            vocabulary=SimpleVocabulary(
                [
                    SimpleTerm("accordion", "accordion", "accordion"),
                    SimpleTerm("advlist", "advlist", "advlist"),
                    SimpleTerm("anchor", "anchor", "anchor"),
                    SimpleTerm("autolink", "autolink", "autolink"),
                    SimpleTerm("autosave", "autosave", "autosave"),
                    SimpleTerm("charmap", "charmap", "charmap"),
                    SimpleTerm("code", "code", "code"),
                    SimpleTerm("colorpicker", "colorpicker", "colorpicker"),
                    SimpleTerm("contextmenu", "contextmenu", "contextmenu"),
                    SimpleTerm("directionality", "directionality", "directionality"),
                    SimpleTerm("emoticons", "emoticons", "emoticons"),
                    SimpleTerm("fullpage", "fullpage", "fullpage"),
                    SimpleTerm("fullscreen", "fullscreen", "fullscreen"),
                    SimpleTerm("help", "help", "help"),
                    SimpleTerm("hr", "hr", "hr"),
                    SimpleTerm("insertdatetime", "insertdatetime", "insertdatetime"),
                    SimpleTerm("layer", "layer", "layer"),
                    SimpleTerm("lists", "lists", "lists"),
                    SimpleTerm("media", "media", "media"),
                    SimpleTerm("nonbreaking", "nonbreaking", "nonbreaking"),
                    SimpleTerm("noneditable", "noneditable", "noneditable"),
                    SimpleTerm("pagebreak", "pagebreak", "pagebreak"),
                    SimpleTerm("paste", "paste", "paste"),
                    SimpleTerm("preview", "preview", "preview"),
                    SimpleTerm("print", "print", "print"),
                    # XXX disable save button since it is not implemented
                    # SimpleTerm('save', 'save', u'save'),
                    SimpleTerm("searchreplace", "searchreplace", "searchreplace"),
                    SimpleTerm("tabfocus", "tabfocus", "tabfocus"),
                    SimpleTerm("table", "table", "table"),
                    SimpleTerm("textcolor", "textcolor", "textcolor"),
                    SimpleTerm("textpattern", "textpattern", "textpattern"),
                    SimpleTerm("template", "template", "template"),
                    SimpleTerm("visualblocks", "visualblocks", "visualblocks"),
                    SimpleTerm("visualchars", "visualchars", "visualchars"),
                    SimpleTerm("wordcount", "wordcount", "wordcount"),
                ]
            )
        ),
        default=[
            "fullscreen",
            "hr",
            "lists",
            "media",
            "nonbreaking",
            "noneditable",
            "pagebreak",
            "paste",
            "preview",
            "print",
            "searchreplace",
            "tabfocus",
            "table",
            "visualchars",
            "wordcount",
            "code",
        ],
        missing_value=[],
        required=False,
    )

    # menubar changed to TextLine, because the tinymce api are changed
    menubar = schema.TextLine(
        title=_("label_tinymce_menubar", default="Menubar"),
        description=_(
            "help_tinymce_menubar",
            default=("Enter what items you would like in the menu bar."),
        ),
        required=True,
        default="edit table format tools view insert",
    )

    menu = schema.Text(
        title=_("label_tinymce_menu", "Menu"),
        description=_(
            "hint_tinymce_menu", default="JSON formatted Menu configuration."
        ),
        constraint=validate_json,
        default=dump_json_to_text(
            {
                "edit": {
                    "title": "Edit",
                    "items": "undo redo | cut copy paste pastetext | "
                    "searchreplace textpattern selectall | textcolor",
                },
                "insert": {"title": "Insert", "items": "link media | template hr"},
                "view": {
                    "title": "View",
                    "items": "visualaid visualchars visualblocks preview "
                    "fullpage fullscreen code",
                },
                "format": {
                    "title": "Format",
                    "items": "bold italic underline strikethrough "
                    "superscript subscript | formats | removeformat",
                },
                "table": {
                    "title": "Table",
                    "items": "inserttable tableprops deletetable | cell row column",
                },
                "tools": {
                    "title": "Tools",
                    "items": "spellchecker charmap emoticons insertdatetime layer",
                },
            }
        ),
    )

    templates = schema.Text(
        title=_("label_tinymce_templates", default="Templates"),
        description=_(
            "help_tinymce_templates",
            default=(
                "Enter the list of templates in json format "
                "https://www.tinymce.com/docs/plugins/template/"
            ),
        ),
        required=False,
        constraint=validate_json,
        default=dump_json_to_text({}),
    )

    toolbar = schema.Text(
        title=_("label_tinymce_toolbar", default="Toolbar"),
        description=_(
            "help_tinymce_toolbar",
            default=("Enter how you would like the toolbar items to list."),
        ),
        required=True,
        default="ltr rtl | undo redo | styleselect | bold italic | "
        "alignleft aligncenter alignright alignjustify | "
        "bullist numlist outdent indent | "
        "inserttable | unlink plonelink ploneimage",
    )

    custom_plugins = schema.List(
        title=_("Custom plugins"),
        description=_(
            "Enter a list of custom plugins which will be loaded "
            "in the editor. Format is "
            "pluginname|location, one per line."
        ),
        required=False,
        value_type=schema.TextLine(),
        missing_value=[],
        default=[],
    )

    custom_buttons = schema.List(
        title=_("Custom buttons"),
        description=_("Enter a list of custom buttons which will be added to toolbar"),
        required=False,
        value_type=schema.TextLine(),
        missing_value=[],
        default=[],
    )


ITinyMCELibrariesSchema = ITinyMCEPluginSchema  # bw compat


class ITinyMCEResourceTypesSchema(Interface):
    """This interface defines the resource types properties."""

    # XXX Not implemented in new tinymce version. Need to decide about this
    # rooted = schema.Bool(
    #    title=_(u"Rooted to current object"),
    #    description=_(u"When enabled the user will be rooted to the current "
    #                  "object and can't add links and images from other "
    #                  "parts of the site."),
    #    default=False,
    #    required=False)

    contains_objects = schema.List(
        title=_("Contains objects"),
        description=_(
            "Enter a list of content types which can contain other "
            "objects. Format is one contenttype per line."
        ),
        value_type=schema.TextLine(),
        default=["Folder", "Large Plone Folder", "Plone Site"],
        missing_value=[],
        required=False,
    )

    image_objects = schema.List(
        title=_("Image objects"),
        description=_(
            "Enter a list of content types which can be used as "
            "images. Format is one contenttype per line."
        ),
        default=["Image"],
        value_type=schema.TextLine(),
        missing_value=[],
        required=False,
    )

    entity_encoding = schema.Choice(
        title=_("Entity encoding"),
        description=_(
            "This option controls how entities/characters get processed. "
            "Named: Characters will be converted into named entities "
            "based on the entities option. "
            "Numeric: Characters will be converted into numeric entities. "
            "Raw: All characters will be stored in non-entity form "
            "except these XML default entities: amp lt gt quot"
        ),
        # missing_value=set(),
        vocabulary=SimpleVocabulary(
            [
                SimpleTerm("named", "named", _("Named")),
                SimpleTerm("numeric", "numeric", _("Numeric")),
                SimpleTerm("raw", "raw", _("Raw")),
            ]
        ),
        default="raw",
        required=False,
    )


class ITinyMCEAdvancedSchema(Interface):
    """This interface defines the resource types properties."""

    other_settings = schema.Text(
        title=_("label_tinymce_other_settings", "Other settings"),
        description=_(
            "hint_tinymce_other_settings",
            default="Other TinyMCE configuration formatted as JSON.",
        ),
        required=False,
        constraint=validate_json,
        default=dump_json_to_text({}),
    )


class ITinyMCESchema(
    ITinyMCELayoutSchema,
    ITinyMCEPluginSchema,
    ITinyMCEResourceTypesSchema,
    ITinyMCEAdvancedSchema,
):
    """TinyMCE Schema"""


class IMaintenanceSchema(Interface):
    days = schema.Int(
        title=_("Days of object history to keep after packing"),
        description=_(
            "You should pack your database regularly. This number "
            "indicates how many days of undo history you want to "
            "keep. It is unrelated to versioning, so even if you "
            "pack the database, the history of the content changes "
            "will be kept. Recommended value is 7 days."
        ),
        default=7,
        min=0,
        required=True,
    )


class INavigationSchema(Interface):
    navigation_depth = schema.Int(
        title=_("Navigation depth"),
        description=_("Number of folder levels to show in the navigation."),
        default=3,
        required=True,
    )

    generate_tabs = schema.Bool(
        title=_("Automatically generate tabs"),
        description=_(
            "By default, all items created at the root level will "
            "appear as tabs. You can turn this off if you prefer manually "
            "constructing this part of the navigation."
        ),
        default=True,
        required=False,
    )

    nonfolderish_tabs = schema.Bool(
        title=_("Generate tabs for items other than folders."),
        description=_(
            "By default, any content item in the root of the portal will "
            "appear as a tab. If you turn this option off, only folders "
            "will be shown. This only has an effect if 'automatically "
            "generate tabs' is enabled."
        ),
        default=True,
        required=False,
    )

    sort_tabs_on = schema.Choice(
        title=_("Sort tabs on"),
        description=_("Index used to sort the tabs"),
        required=True,
        default="getObjPositionInParent",
        vocabulary=SimpleVocabulary(
            [
                # there is no vocabulary of sortable indexes by now, so hard code
                # some options here
                SimpleTerm(
                    "getObjPositionInParent",
                    "getObjPositionInParent",
                    _("Position in Parent"),
                ),
                SimpleTerm("sortable_title", "sortable_title", _("Title")),
                SimpleTerm("getId", "getId", _("Short Name (ID)")),
            ]
        ),
    )
    sort_tabs_reversed = schema.Bool(
        title=_("Reversed sort order for tabs."),
        description=_("Sort tabs in descending."),
        default=False,
        required=False,
    )

    displayed_types = schema.Tuple(
        title=_("Displayed content types"),
        description=_(
            "The content types that should be shown in the navigation and site map."
        ),
        required=False,
        default=("Link", "News Item", "Folder", "Document", "Event", "Collection"),
        missing_value=(),
        value_type=schema.Choice(
            source="plone.app.vocabularies.ReallyUserFriendlyTypes"
        ),
    )

    filter_on_workflow = schema.Bool(
        title=_("Filter on workflow state"),
        description=_(
            "The workflow states that should be shown in the navigation "
            "and the site map."
        ),
        default=False,
        required=False,
    )

    workflow_states_to_show = schema.Tuple(
        required=False,
        default=(),
        missing_value=(),
        value_type=schema.Choice(source="plone.app.vocabularies.WorkflowStates"),
    )

    show_excluded_items = schema.Bool(
        title=_(
            "Show items normally excluded from navigation if viewing their children."
        ),
        description=_(
            "If an item has been excluded from navigation should it be "
            "shown in navigation when viewing content contained within it "
            "or within a subfolder."
        ),
        default=False,
        required=False,
    )

    root = schema.TextLine(
        title=_("Root"),
        description=_(
            "Path to be used as navigation root, relative to Plone site root."
            "Starts with '/'"
        ),
        default="/",
        required=True,
    )

    sitemap_depth = schema.Int(
        title=_("Sitemap depth"),
        description=_("Number of folder levels to show in the site map."),
        default=3,
        required=True,
    )

    parent_types_not_to_query = schema.List(
        title=_("Hide children of these types"),
        description=_("Hide content inside the following types in Navigation."),
        default=["TempFolder"],
        value_type=schema.TextLine(),
        missing_value=(),
        required=False,
    )


class ISearchSchema(Interface):
    enable_livesearch = schema.Bool(
        title=_("Enable LiveSearch"),
        description=_(
            "Enables the LiveSearch feature, which shows live "
            "results if the browser supports JavaScript."
        ),
        default=True,
        required=False,
    )

    types_not_searched = schema.Tuple(
        title=_("Select content types which should be excluded from search results"),
        description=_(
            "Select the content types that should be excluded from search results. "
            "Note that if new content types are installed, they "
            "will be enabled by default unless explicitly turned "
            "off here or by the relevant installer."
        ),
        required=False,
        # XXX: Actually, the Plone Site and TempFolder are not part of the vocabulary
        # and would be removed from the list of types not searched on first save in ControlPanel!
        # Both are used in many tests and kept for now.
        default=(
            "Plone Site",
            "TempFolder",
        ),
        missing_value=(),
        value_type=schema.Choice(source="plone.app.vocabularies.PortalTypes"),
    )

    search_results_description_length = schema.Int(
        title=_(
            "Crop the item description in search result listings "
            "after a number of characters."
        ),
        required=False,
        default=160,
    )

    sort_on = schema.Choice(
        title=_("label_sort_on", default="Sort on"),
        description=_("Sort the default search on this index"),
        vocabulary=SimpleVocabulary(
            [
                SimpleTerm("relevance", "relevance", _("relevance")),
                SimpleTerm("Date", "Date", _("date (newest first)")),
                SimpleTerm("sortable_title", "sortable_title", _("alphabetically")),
            ]
        ),
        default="relevance",
        required=True,
    )

    search_show_images = schema.Bool(
        title=_("Show images in results"),
        default=True,
        required=False,
    )

    search_image_scale = schema.Choice(
        title=_("Image scale for results"),
        default="mini",
        vocabulary="plone.app.vocabularies.ImagesScales",
        required=False,
    )


class ISecuritySchema(Interface):
    enable_self_reg = schema.Bool(
        title=_("Enable self-registration"),
        description=_(
            "Allows users to register themselves on the site. If "
            "not selected, only site managers can add new users."
        ),
        default=False,
        required=False,
    )

    enable_user_pwd_choice = schema.Bool(
        title=_("Let users select their own passwords"),
        description=_(
            "If not selected, a URL will be generated and "
            "e-mailed. Users are instructed to follow the link to "
            "reach a page where they can change their password and "
            "complete the registration process; this also verifies "
            "that they have entered a valid email address."
        ),
        default=False,
        required=False,
    )

    enable_user_folders = schema.Bool(
        title=_("Enable User Folders"),
        description=_(
            "If selected, home folders where users can create "
            "content will be created when they log in."
        ),
        default=False,
        required=False,
    )

    allow_anon_views_about = schema.Bool(
        title=_("Allow anyone to view 'about' information"),
        description=_(
            "If not selected only logged-in users will be able to "
            "view information about who created an item and when it "
            "was modified."
        ),
        default=False,
        required=False,
    )

    use_email_as_login = schema.Bool(
        title=_("Use email address as login name"),
        description=_(
            "Allows users to login with their email address instead "
            "of specifying a separate login name. This also updates "
            "the login name of existing users, which may take a "
            "while on large sites. The login name is saved as "
            "lower case, but to be userfriendly it does not matter "
            "which case you use to login. When duplicates are found, "
            "saving this form will fail. You can use the "
            "@@migrate-to-emaillogin page to show the duplicates."
        ),
        default=False,
        required=False,
    )

    use_uuid_as_userid = schema.Bool(
        title=_("Use UUID user ids"),
        description=_(
            "Use automatically generated UUIDs as user id for new users. "
            "When not turned on, the default is to use the same as the "
            "login name, or when using the email address as login name we "
            "generate a user id based on the fullname."
        ),
        default=False,
        required=False,
    )

    autologin_after_password_reset = schema.Bool(
        title=_("Login user after password reset"),
        description=_(
            "After successful password reset the user will be logged "
            "in automatically."
        ),
        default=True,
        required=False,
    )


class ISiteSchema(Interface):
    site_title = schema.TextLine(
        title=_("Site title"),
        description=_(
            "This shows up in the title bar of browsers and in syndication feeds."
        ),
        default="Plone site",
    )

    site_logo = schema.Bytes(
        title=_("Site Logo"),
        description=_("This shows a custom logo on your site."),
        required=False,
    )

    site_favicon_mimetype = schema.TextLine(
        title=_("MIME type of the site favicon"),
        description=_(
            "MIME type of the favicon (automatically set when a new favicon is uploaded)"
        ),
        required=False,
        default="image/vnd.microsoft.icon",
    )

    site_favicon = schema.Bytes(
        title=_("Site Favicon"),
        description=_("This shows a custom favicon on your site."),
        required=False,
    )

    exposeDCMetaTags = schema.Bool(
        title=_("Expose Dublin Core metadata"),
        description=_("Exposes the Dublin Core properties as metatags."),
        default=False,
        required=False,
    )

    enable_sitemap = schema.Bool(
        title=_("Expose sitemap.xml.gz"),
        description=_(
            "Exposes your content as a file "
            "according to the "
            "<a href='http://sitemaps.org'>sitemaps.org</a> "
            "standard. You "
            "can submit this to compliant search engines "
            "like Google, Yahoo and Microsoft. It allows "
            "these search engines to more intelligently "
            "crawl your site."
        ),
        default=False,
        required=False,
    )

    webstats_head_js = schema.SourceText(
        title=_("JavaScript integrations included in head section"),
        description=_(
            "For enabling third-party JavaScript integrations "
            "from external providers (e.g., Google "
            "Analytics), paste the provided code snippet here. "
            "It will be rendered as "
            "entered at the end of the head section of the page."
        ),
        default="",
        required=False,
    )

    webstats_js = schema.SourceText(
        title=_("JavaScript integrations included after the footer"),
        description=_(
            "For enabling third-party JavaScript integrations "
            "from external providers (e.g. Google "
            "Analytics). Paste the provided code snippet here. "
            "It will be rendered as "
            "entered near the end of the page."
        ),
        default="",
        required=False,
    )

    display_publication_date_in_byline = schema.Bool(
        title=_("Display publication date"),
        description=_("Show in the byline the date a content item was published."),
        default=False,
        required=False,
    )

    icon_visibility = schema.Choice(
        title=_("Icon visibility"),
        description=_("Show icons in listings"),
        default="enabled",
        vocabulary=SimpleVocabulary(
            [
                SimpleTerm("false", "false", _("Never")),
                SimpleTerm("enabled", "enabled", _("Always")),
                SimpleTerm(
                    "authenticated", "authenticated", _("For authenticated users only")
                ),
            ]
        ),
        required=True,
    )

    thumb_visibility = schema.Choice(
        title=_("Thumb visibility"),
        description=_("Show thumbnail images in listings"),
        default="enabled",
        vocabulary=SimpleVocabulary(
            [
                SimpleTerm("false", "false", _("Never")),
                SimpleTerm("enabled", "enabled", _("Always")),
                SimpleTerm(
                    "authenticated", "authenticated", _("For authenticated users only")
                ),
            ]
        ),
        required=True,
    )

    no_thumbs_portlet = schema.Bool(
        title=_("No Thumbs in portlets"),
        description=_(
            "Suppress thumbs in all portlets;"
            " this default can be overridden individually "
            "in selected portlets"
        ),
        default=False,
        required=False,
    )

    no_thumbs_lists = schema.Bool(
        title=_("No thumbs in list views"),
        description=_(
            "Suppress thumbs in all list views; "
            "this default can be overridden individually"
        ),
        default=False,
        required=False,
    )

    no_thumbs_summary = schema.Bool(
        title=_("No thumbs in summary views"),
        description=_(
            "Suppress thumbs in all summary views; "
            "this default can be overridden individually"
        ),
        default=False,
        required=False,
    )

    no_thumbs_tables = schema.Bool(
        title=_("No thumbs in table views"),
        description=_(
            "Suppress thumbs in all tableviews and in folder contents view; "
            "this default can be overridden individually"
        ),
        default=False,
        required=False,
    )

    thumb_scale_portlet = schema.Choice(
        title=_("Thumb scale for portlets"),
        description=_("This default can be overridden individually."),
        default="icon",
        vocabulary="plone.app.vocabularies.ImagesScales",
        required=True,
    )

    thumb_scale_listing = schema.Choice(
        title=_("Thumb scale for listings"),
        description=_(
            "E.g. standard view; This default can be overridden individually."
        ),
        default="thumb",
        vocabulary="plone.app.vocabularies.ImagesScales",
        required=True,
    )

    thumb_scale_table = schema.Choice(
        title=_("Thumb scale for tables"),
        description=_(
            "E.g., tabular view, folder content listing;"
            " This default can be overridden individually."
        ),
        default="tile",
        vocabulary="plone.app.vocabularies.ImagesScales",
        required=True,
    )

    thumb_scale_summary = schema.Choice(
        title=_("Thumb scale for summary view"),
        description=_("This default can be overridden individually."),
        default="mini",
        vocabulary="plone.app.vocabularies.ImagesScales",
        required=True,
    )

    toolbar_position = schema.Choice(
        title=_("Toolbar position"),
        description=_(
            "It can be on the side (vertical mode) or on the top (horizontal mode)"
        ),
        default="side",
        vocabulary=SimpleVocabulary(
            [SimpleTerm("side", "side", _("Side")), SimpleTerm("top", "top", _("Top"))]
        ),
        required=True,
    )

    toolbar_logo = schema.TextLine(
        title=_("Relative URL for the toolbar logo"),
        description=_(
            "This must be a URL relative to the site root. "
            "By default it is /++plone++static/plone-toolbarlogo.svg"
        ),
        default="/++plone++static/plone-toolbarlogo.svg",
        required=False,
    )

    robots_txt = schema.SourceText(
        title=_("robots.txt"),
        description=_(
            "help_robots_txt",
            default="robots.txt is read by search engines to "
            "determine how to index your site. "
            "For details see <a href='http://www.robotstxt.org'>"
            "http://www.robotstxt.org</a>. "
            "Use '{portal_url}' for the site URL.",
        ),
        default=ROBOTS_TXT,
        required=False,
    )

    default_page = schema.List(
        title=_("Default page IDs"),
        description=_(
            "Select which IDs (short names) can act as fallback "
            "default pages for a container."
        ),
        required=False,
        default=["index_html", "index.html", "index.htm", "FrontPage"],
        missing_value=[],
        value_type=schema.TextLine(),
    )

    roles_allowed_to_add_keywords = schema.List(
        title=_("Roles that can add keywords"),
        description=_(
            "help_allow_roles_to_add_keywords",
            default="Only the following roles can add new keywords ",
        ),
        required=False,
        default=[
            "Manager",
            "Site Administrator",
            "Reviewer",
        ],
        missing_value=[],
        value_type=schema.Choice(vocabulary="plone.app.vocabularies.Roles"),
    )


class IDateAndTimeSchema(Interface):
    """Controlpanel settings for date and time related settings."""

    portal_timezone = schema.Choice(
        title=_("Portal default timezone"),
        description=_(
            "help_portal_timezone",
            default="The timezone setting of the portal. Users can set "
            "their own timezone, if available timezones are "
            "defined.",
        ),
        required=True,
        default=None,
        vocabulary="plone.app.vocabularies.CommonTimezones",
    )

    available_timezones = schema.List(
        title=_("Available timezones"),
        description=_(
            "help_available_timezones",
            default="The timezones, which should be available for the "
            "portal. Can be set for users and events",
        ),
        required=False,
        default=[],
        missing_value=[],
        value_type=schema.Choice(vocabulary="plone.app.vocabularies.Timezones"),
    )

    first_weekday = schema.Choice(
        title=_("label_first_weekday", default="First weekday"),
        description=_("help_first_weekday", default="First day in the week."),
        required=True,
        default=None,
        vocabulary="plone.app.vocabularies.Weekdays",
    )


class ITypesSchema(Interface):
    """Controlpanel settings for the types settings."""

    types_use_view_action_in_listings = schema.List(
        title=_("Types which use the view action in listing views."),
        description=_(
            "help_types_use_view_action_in_listings",
            default="When clicking items in listing views, these "
            "types will use the 'view' action instead of using "
            "their default view.",
        ),
        required=False,
        default=["Image", "File"],
        missing_value=[],
        value_type=schema.TextLine(),
    )

    redirect_links = schema.Bool(
        title=_("Redirect links"),
        description=_(
            "help_redirect_links",
            default="When clicking on a Link type, should the user be "
            "taken to the default view or be redirected to the "
            "Link's URL?",
        ),
        required=False,
        default=True,
    )

    default_page_types = schema.List(
        title=_("Types that can be set as a default page"),
        description=_(
            "The content types that should be available for selection "
            "when setting a default page."
        ),
        required=False,
        missing_value=[],
        default=[
            "Document",
            "Event",
            "News Item",
            "Collection",
        ],
        value_type=schema.TextLine(),
    )


class IMailSchema(Interface):
    smtp_host = schema.TextLine(
        title=_("label_smtp_server", default="SMTP server"),
        description=_(
            "help_smtp_server",
            default="The address of your local "
            "SMTP (outgoing e-mail) server. Usually "
            "'localhost', unless you use an "
            "external server to send e-mail.",
        ),
        default="localhost",
        required=True,
    )

    smtp_port = schema.Int(
        title=_("label_smtp_port", default="SMTP port"),
        description=_(
            "help_smtp_port",
            default="The port of your local SMTP "
            "(outgoing e-mail) server. Usually '25'.",
        ),
        default=25,
        required=True,
    )

    smtp_userid = schema.TextLine(
        title=_("label_smtp_userid", default="ESMTP username"),
        description=_(
            "help_smtp_userid",
            default="Username for authentication "
            "to your e-mail server. Not required "
            "unless you are using ESMTP.",
        ),
        default=None,
        required=False,
    )

    smtp_pass = schema.Password(
        title=_("label_smtp_pass", default="ESMTP password"),
        description=_(
            "help_smtp_pass", default="The password for the ESMTP user account."
        ),
        default=None,
        required=False,
    )

    email_from_name = schema.TextLine(
        title=_("Site 'From' name"),
        description=_("Plone generates e-mail using this name as the e-mail sender."),
        default=None,
        required=True,
    )

    email_from_address = schema.ASCIILine(
        title=_("Site 'From' address"),
        description=_(
            "Plone generates e-mail using "
            "this address as the e-mail "
            "return address. It is also "
            "used as the destination "
            "address for the site-wide "
            "contact form and the 'Send test "
            "e-mail' feature."
        ),
        default=None,
        required=True,
    )

    email_charset = schema.ASCIILine(
        title=_("E-mail characterset"),
        description=_("Characterset to use when sending e-mails."),
        default="utf-8",
        required=True,
    )


class IMarkupSchema(Interface):
    default_type = schema.Choice(
        title=_("Default format"),
        description=_(
            "Select the default format of textfields for newly "
            "created content objects."
        ),
        default="text/html",
        vocabulary="plone.app.vocabularies.AllowableContentTypes",
        required=True,
    )

    allowed_types = schema.Tuple(
        title=_("Alternative formats"),
        description=_(
            "Select which formats are available for users as "
            "alternative to the default format. Note that if new "
            "formats are installed, they will be enabled for text "
            "fields by default unless explicitly turned off here "
            "or by the relevant installer."
        ),
        required=True,
        default=("text/html", "text/x-web-textile"),
        missing_value=(),
        value_type=schema.Choice(
            vocabulary="plone.app.vocabularies.AllowableContentTypes"
        ),
    )

    markdown_extensions = schema.List(
        default=[
            "markdown.extensions.fenced_code",
            "markdown.extensions.nl2br",
        ],
        description=_(
            "Look for available extensions at "
            "https://python-markdown.github.io/extensions/ or write your own."
        ),
        missing_value=(),
        required=False,
        title=_("Enabled markdown extensions"),
        value_type=schema.TextLine(),
    )


class IUserGroupsSettingsSchema(Interface):
    many_groups = schema.Bool(
        title=_("Many groups?"),
        description=_(
            "Determines if your Plone is optimized "
            "for small or large sites. In environments with a "
            "lot of groups it can be very slow or impossible "
            "to build a list all groups. This option tunes the "
            "user interface and behaviour of Plone for this "
            "case by allowing you to search for groups instead "
            "of listing all of them."
        ),
        default=False,
        required=False,
    )

    many_users = schema.Bool(
        title=_("Many users?"),
        description=_(
            "Determines if your Plone is optimized "
            "for small or large sites. In environments with a "
            "lot of users it can be very slow or impossible to "
            "build a list all users. This option tunes the user "
            "interface and behaviour of Plone for this case by "
            "allowing you to search for users instead of "
            "listing all of them."
        ),
        default=False,
        required=False,
    )


def validate_twitter_username(value):
    if value and value.startswith("@"):
        raise Invalid('Twitter username should not include the "@" prefix character.')
    return True


class ISocialMediaSchema(Interface):
    share_social_data = schema.Bool(
        title=_("Share social data"),
        description=_(
            "Include meta tags on pages to give hints to "
            "social media on how to better render your pages "
            "when shared"
        ),
        default=True,
        required=False,
    )

    twitter_username = schema.ASCIILine(
        title=_("Twitter username"),
        description=_(
            "To identify things like Twitter Cards. "
            'Do not include the "@" prefix character.'
        ),
        required=False,
        default="",
        constraint=validate_twitter_username,
    )

    facebook_app_id = schema.ASCIILine(
        title=_("Facebook App ID"),
        description=_("To be used with some integrations like Open Graph data"),
        required=False,
        default="",
    )

    facebook_username = schema.ASCIILine(
        title=_("Facebook username"),
        description=_("For linking Open Graph data to a Facebook account"),
        required=False,
        default="",
    )


class IImagingSchema(Interface):
    allowed_sizes = schema.List(
        title=_("Allowed image sizes"),
        description=_(
            "Specify all allowed maximum image dimensions, one per line. The "
            "required format is &lt;name&gt; &lt;width&gt;:&lt;height&gt;."
        ),
        value_type=schema.TextLine(),
        default=[
            "huge 1600:65536",
            "great 1200:65536",
            "larger 1000:65536",
            "large 800:65536",
            "teaser 600:65536",
            "preview 400:65536",
            "mini 200:65536",
            "thumb 128:128",
            "tile 64:64",
            "icon 32:32",
            "listing 16:16",
        ],
        missing_value=[],
        required=False,
    )

    quality = schema.Int(
        title=_("Scaled image quality"),
        description=_(
            "A value for the quality of scaled images, from 1 "
            "(lowest) to 95 (highest). A value of 0 will mean "
            "plone.scaling's default will be used, which is "
            "currently 88."
        ),
        min=0,
        max=95,
        default=88,
    )

    highpixeldensity_scales = schema.Choice(
        title=_("High pixel density mode"),
        description=_(""),
        default="disabled",
        vocabulary=SimpleVocabulary(
            [
                SimpleTerm("disabled", "disabled", "Disabled"),
                SimpleTerm("2x", "2x", "Enabled (2x)"),
                SimpleTerm("3x", "3x", "Enabled (2x, 3x)"),
            ]
        ),
    )

    quality_2x = schema.Int(
        title=_("Image quality at 2x"),
        description=_(
            "A value for the quality of 2x high pixel density images, from 1 "
            "(lowest) to 95 (highest). A value of 0 will mean "
            "plone.scaling's default will be used, which is "
            "currently 62."
        ),
        min=0,
        max=95,
        default=62,
    )

    quality_3x = schema.Int(
        title=_("Image quality at 3x"),
        description=_(
            "A value for the quality of 3x high pixel density images, from 1 "
            "(lowest) to 95 (highest). A value of 0 will mean "
            "plone.scaling's default will be used, which is "
            "currently 51."
        ),
        min=0,
        max=95,
        default=51,
    )

    picture_variants = schema.JSONField(
        title=_("Picture variants"),
        description=_("Enter a JSON-formatted picture variants configuration."),
        schema=json.dumps(
            {
                "title": "Image srcset definition",
                "type": "object",
                "additionalProperties": {"$ref": "#/$defs/srcset"},
                "$defs": {
                    "srcset": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                            },
                            "preview": {
                                "type": "string",
                            },
                            "hideInEditor": {
                                "type": "boolean",
                            },
                            "sourceset": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "scale": {
                                            "type": "string",
                                        },
                                        "media": {
                                            "type": "string",
                                        },
                                        "additionalScales": {
                                            "type": "array",
                                        },
                                    },
                                    "additionalProperties": False,
                                    "required": ["scale"],
                                },
                            },
                        },
                        "additionalProperties": False,
                        "required": ["title", "sourceset"],
                    },
                },
            }
        ),
        default={
            "large": {
                "title": "Large",
                "sourceset": [
                    {
                        "scale": "larger",
                        "additionalScales": [
                            "preview",
                            "teaser",
                            "large",
                            "great",
                            "huge",
                        ],
                    },
                ],
            },
            "medium": {
                "title": "Medium",
                "sourceset": [
                    {
                        "scale": "teaser",
                        "additionalScales": ["preview", "large", "larger", "great"],
                    },
                ],
            },
            "small": {
                "title": "Small",
                "sourceset": [
                    {
                        "scale": "preview",
                        "additionalScales": ["large", "larger"],
                    },
                ],
            },
        },
        required=True,
    )

    image_captioning = schema.Bool(
        title=_("image_captioning_title", "Enable image captioning"),
        description=_(
            "image_captioning_description",
            "Enable automatic image captioning for images set in the richtext editor based on the description of images.",
        ),
        default=True,
        required=False,
    )


class ILoginSchema(Interface):
    auth_cookie_length = schema.Int(
        title=_("Auth cookie length"), default=0, required=False
    )

    verify_login_name = schema.Bool(
        title=_("Verify login name"), default=True, required=False
    )

    allow_external_login_sites = schema.Tuple(
        title=_("Allow external login sites"),
        default=(),
        value_type=schema.ASCIILine(),
        required=False,
    )

    external_login_url = schema.ASCIILine(
        title=_("External login url"), default=None, required=False
    )

    external_logout_url = schema.ASCIILine(
        title=_("External logout url"), default=None, required=False
    )

    external_login_iframe = schema.Bool(
        title=_("External login iframe"), default=False, required=False
    )


class ILinkSchema(Interface):
    external_links_open_new_window = schema.Bool(
        title=_("Open external links in new a window"),
        description=_(""),
        default=False,
        required=False,
    )

    mark_special_links = schema.Bool(
        title=_("Mark special links"),
        description=_("Marks external or special protocol links with class."),
        default=False,
        required=False,
    )


def _check_tales_expression(value):
    from Products.PageTemplates.Expressions import getEngine

    try:
        getEngine().compile(value)
    except Exception:
        raise Invalid(
            _(
                'The expression "${value}" is invalid',
                mapping={"value": value},
            )
        )
    return True


class IActionSchema(Interface):
    category = schema.Choice(
        title=_("Category"),
        vocabulary="plone.app.vocabularies.PortalActionCategories",
        required=True,
    )

    title = schema.TextLine(title=_("Title"), required=True)

    description = schema.Text(title=_("Description"), required=False)

    i18n_domain = schema.TextLine(
        title=_("i18n_domain_heading", default="I18n domain"),
        default="plone",
        required=False,
    )

    url_expr = schema.ASCIILine(
        title=_("action_url_heading", default="Action URL"),
        description=_(
            "action_url_description",
            default="An expression producing the called URL. "
            "Example: string:${globals_view/navigationRootUrl}/page",
        ),
        required=True,
        constraint=_check_tales_expression,
    )

    available_expr = schema.ASCIILine(
        title=_("action_condition_heading", default="Condition"),
        description=_("action_condition_description", default="A boolean expression"),
        required=False,
    )

    permissions = schema.List(
        title=_("action_permissions_heading", default="Permissions"),
        required=True,
        default=["View"],
        missing_value=[],
        value_type=schema.Choice(vocabulary="plone.app.vocabularies.Permissions"),
    )

    visible = schema.Bool(
        title=_("action_visibility_heading", default="Visible?"),
        default=True,
        required=False,
    )

    position = schema.Int(
        title=_("action_position_heading", default="Position"),
        default=1,
        min=1,
        required=True,
    )

    modal = schema.Text(
        title=_("action_modal_settings", default="Settings for pat-plone-modal"),
        required=False,
        constraint=validate_json,
    )


class INewActionSchema(Interface):
    category = schema.Choice(
        title=_("Category"),
        vocabulary="plone.app.vocabularies.PortalActionCategories",
        required=True,
    )

    id = schema.ASCIILine(title=_("Id"), required=True)

    @invariant
    def validate_category_id(data):
        categoryid = data.category
        pa = getToolByName(getSite(), "portal_actions")
        category = pa.get(categoryid, {})
        actionid = data.id
        if actionid in category:
            raise Invalid(
                _(
                    'An action with the id "${actionid}" already exists',
                    mapping={"actionid": actionid},
                )
            )
        try:
            category._checkId(actionid)
        except Exception:
            raise Invalid(
                _(
                    'The id "${actionid}" is invalid',
                    mapping={"actionid": actionid},
                )
            )


class IPloneControlPanelView(Interface):
    """A marker interface for views showing a controlpanel."""


class IPloneControlPanelForm(IPloneControlPanelView):
    """Forms using plone.app.controlpanel"""

    def _on_save():
        """Callback method which can be implemented by control panels to
        react when the form is successfully saved. This avoids the need
        to re-define actions only to do some additional notification or
        configuration which cannot be handled by the normal schema adapter.

        By default, does nothing.
        """


class IConfigurationChangedEvent(Interface):
    """An event which is fired after a configuration setting has been changed."""

    context = Attribute("The configuration context which was changed.")

    data = Attribute("The configuration data which was changed.")
