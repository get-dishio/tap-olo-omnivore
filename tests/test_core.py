"""Tests standard tap features using the built-in SDK tests library."""

from singer_sdk.testing import get_tap_test_class

from tap_olo_omnivore.tap import TapOloOmnivore

SAMPLE_CONFIG = {
    "api_key": "xxxxxxxxxxxxxxxxxxxxxxxx",
    "base_url": "https://api.omnivore.io/1.0",
}


# Run standard built-in tap tests from the SDK:
TestTapOloOmnivore = get_tap_test_class(
    tap_class=TapOloOmnivore,
    config=SAMPLE_CONFIG,
)
