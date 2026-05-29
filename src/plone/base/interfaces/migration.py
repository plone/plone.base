from zope.interface import Attribute
from zope.interface import Interface


class IAddonList(Interface):
    """Utility providing a list of add-ons managed by the migration tool.

    * addon_list is the list of add-ons that are upgraded at the end
      of the migration
    * pre_addon_list is the list of add-ons that are upgraded at the start
      of the migration.

    The pre_addon_list is optional.  If you have a Plone distribution with an
    own base profile, you may want to add the default Plone profile here,
    so the core of Plone is updated first:

    pre_addon_list = AddonList([Addon(profile_id="Products.CMFPlone:plone")])

    Maybe add a part of the standard ADDON_LIST from
    Products.CMFPlone.MigrationTool as well.
    But if you find yourself adding *all* of them, then your distribution
    probably doesn't need its own base profile and add-on list.
    """

    addon_list = Attribute("add-ons upgraded at end of migration.")
    pre_addon_list = Attribute("add-ons upgraded at start of migration.")


class IMigrationTool(Interface):
    """Handles migrations between Plone releases."""

    def getInstanceVersion():
        """The version this instance of Plone is on."""

    def setInstanceVersion(version):
        """The version this instance of Plone is on."""

    def getFileSystemVersion():
        """The version the filesystem code of Plone is on."""

    def needUpgrading():
        """Need upgrading?"""

    def coreVersions():
        """Useful core version information."""

    def coreVersionsList():
        """Useful core version information."""

    def needUpdateRole():
        """Do roles need to be updated?"""

    def needRecatalog():
        """Does this thing now need recataloging?"""

    def upgrade(REQUEST=None, dry_run=None, swallow_errors=1):
        """Perform the upgrade."""
