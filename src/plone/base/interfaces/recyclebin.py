"""Interfaces for the Plone Recycle Bin functionality."""

from plone.base import PloneMessageFactory as _
from zope import schema
from zope.interface import Interface


class IRecycleBinControlPanelSettings(Interface):
    """Interface for recycle bin settings"""

    recycling_enabled = schema.Bool(
        title=_("Enable the recycle bin"),
        description=_("Enable or disable the recycle bin feature."),
        default=False,
        required=False,
    )

    retention_period = schema.Int(
        title=_("Retention period"),
        description=_(
            "Number of days to keep deleted items in the recycle bin. Set to '0' to disable automatic purging."
        ),
        default=30,
        min=0,
    )

    restore_to_initial_state = schema.Bool(
        title=_("Restore to initial workflow state"),
        description=_(
            "When enabled, restored content will be set to its initial workflow state (usually 'draft') instead of the workflow state it was in when deleted."
        ),
        default=False,
        required=False,
    )


class IRecycleBin(Interface):
    """Interface for the recycle bin functionality"""

    def add_item(obj, original_container, original_path):
        """Add deleted item to recycle bin

        Args:
            obj: The object being deleted
            original_container: The parent container before deletion
            original_path: The full path to the object before deletion

        Returns:
            The ID of the item in the recycle bin
        """

    def get_items():
        """Return all items in recycle bin

        Returns:
            A list of dictionaries with information about deleted items
        """

    def get_item(item_id):
        """Get a specific deleted item by ID

        Args:
            item_id: The ID of the deleted item in the recycle bin

        Returns:
            Dictionary with item information or None if not found
        """

    def restore_item(item_id, target_container=None):
        """Restore item to original location or specified container

        Args:
            item_id: The ID of the item in the recycle bin
            target_container: Optional target container to restore to
                              (defaults to original container)

        Returns:
            The restored object or None if restore failed
        """

    def restore_child_item(item_id, child_path, target_container):
        """Restore a specific child from a recycled folder item.

        Args:
            item_id: The recycle bin ID of the parent item.
            child_path: The original path of the child (unique at any depth).
            target_container: The container object where the child will be restored.

        Returns:
            The restored object on success, or a dict with ``success: False``
            and an ``error`` key on failure.
        """

    def purge_item(item_id):
        """Permanently delete an item

        Args:
            item_id: The ID of the item in the recycle bin

        Returns:
            Boolean indicating success
        """

    def purge_expired_items():
        """Purge items that exceed the retention period

        Returns:
            Number of items purged
        """

    def search(
        title=None,
        path=None,
        portal_type=None,
        date_from=None,
        date_to=None,
        deleted_by=None,
        has_subitems=None,
        language=None,
        review_state=None,
        sort_on="deletion_date",
        sort_order="descending",
    ):
        """Return filtered and sorted items from the recycle bin.

        All parameters are optional; omitting them returns all items.

        Args:
            title: Case-insensitive substring to match against item title (str)
            path: Case-insensitive substring to match against item path (str)
            portal_type: Exact portal_type to filter by (str)
            date_from: Earliest deletion date, inclusive (datetime.date)
            date_to: Latest deletion date, inclusive (datetime.date)
            deleted_by: User ID who deleted the item (str)
            has_subitems: True → only items with children; False → only without (bool or None)
            language: Language code to filter by (str)
            review_state: Workflow state to filter by (str)
            sort_on: Field to sort by — one of title, portal_type, path, size,
                     deletion_date (default), review_state (str)
            sort_order: "ascending" or "descending" (default) (str)

        Returns:
            Filtered and sorted list of item dicts (same shape as get_items())
        """

    def is_enabled():
        """Check if recycle bin is enabled in the registry settings

        Returns:
            Boolean indicating whether recycle bin is enabled
        """
