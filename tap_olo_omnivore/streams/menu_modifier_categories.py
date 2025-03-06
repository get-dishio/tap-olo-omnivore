from __future__ import annotations

from tap_olo_omnivore.client import OloOmnivoreStream
from tap_olo_omnivore.streams.menu_modifiers import MenuModifiersStream


class MenuModifierCategoriesStream(OloOmnivoreStream):
    """Child stream for retrieving categories for a given menu modifier from the Omnivore API."""

    name = "menu_modifier_categories"
    primary_keys = ["id"]
    replication_key = None
    parent_stream_type = MenuModifiersStream

    @property
    def path(self) -> str:
        """Construct the URL path using location_id from config and the modifier_id from the parent context."""
        location_id = self.context.get("location_id")
        menu_modifier_id = self.context.get("menu_modifier_id")
        return f"/locations/{location_id}/menu/modifiers/{menu_modifier_id}/categories"
