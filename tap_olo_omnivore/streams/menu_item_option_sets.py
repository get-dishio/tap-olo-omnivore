from __future__ import annotations

from tap_olo_omnivore.client import OloOmnivoreStream
from tap_olo_omnivore.streams.menu_items import MenuItemsStream


class MenuItemOptionSetsStream(OloOmnivoreStream):
    """Child stream for retrieving option sets for a given menu item from the Omnivore API."""

    name = "menu_item_option_sets"
    primary_keys = ["id"]
    replication_key = None
    parent_stream_type = MenuItemsStream

    @property
    def path(self) -> str:
        """Construct the URL path using location_id from config and menu_item_id from the parent context."""
        location_id = self.context.get("location_id")
        menu_item_id = self.context.get("menu_item_id")
        return f"/locations/{location_id}/menu/items/{menu_item_id}/option_sets"
