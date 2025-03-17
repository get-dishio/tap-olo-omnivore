from __future__ import annotations

from tap_olo_omnivore.client import OloOmnivoreStream
from tap_olo_omnivore.streams.menu_items import MenuItemsStream


class MenuItemCategoriesStream(OloOmnivoreStream):
    """Child stream for retrieving categories for a given menu item from the Omnivore API."""

    name = "menu_item_categories"
    primary_keys = ["id", "location_id"]
    replication_key = None
    parent_stream_type = MenuItemsStream

    @property
    def path(self) -> str:
        """Construct the URL path using the location id from config and the menu_item_id from the parent context."""
        location_id = self.context.get("location_id")
        menu_item_id = self.context.get("menu_item_id")
        return f"/locations/{location_id}/menu/items/{menu_item_id}/categories"
