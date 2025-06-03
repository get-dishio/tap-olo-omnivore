"""REST client handling, including OloOmnivoreStream base class."""

from __future__ import annotations
from datetime import datetime

import decimal
import json
import typing as t
from importlib import resources
from urllib.parse import parse_qsl, urlparse

import backoff
import requests
from singer_sdk.authenticators import APIKeyAuthenticator
from singer_sdk.exceptions import RetriableAPIError
from singer_sdk.helpers.jsonpath import extract_jsonpath
from singer_sdk.helpers.types import Context
from singer_sdk.streams import RESTStream

from tap_olo_omnivore.pagination import CustomHATEOASPaginator

# Reference local JSON schema files.
SCHEMAS_DIR = resources.files(__package__) / "schemas"

def extract_id_from_href(href: str) -> str:
    """
    Extracts the last non-empty segment from the given URL's path.
    For example, if href is 'https://api.omnivore.io/1.0/locations/T6EaXqEc/employees/200/',
    this function returns '200'.
    """
    parsed = urlparse(href)
    segments = [seg for seg in parsed.path.split('/') if seg]
    return segments[-1] if segments else ""

def flatten_nested_objects(data, parent_key='', sep='_'):
    """
        Recursively flattens a nested dictionary or list of dictionaries.
        This function traverses the input data, flattening nested dictionaries and lists
        into a single-level dictionary. Keys of nested dictionaries are combined with
        their parent keys using the specified separator (default '_'). Lists of dictionaries
        are flattened by appending the index of each item to the parent key.
        Excludes '_links', '_embedded', and 'self' keys from flattening.
        """
    items = []
    for k, v in data.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict) and k not in ("_links", "_embedded", "self"):
            items.extend(flatten_nested_objects(v, new_key, sep=sep).items())
        elif isinstance(v, list) and k not in ("_links", "_embedded", "self"):
            for i, item in enumerate(v):
                if isinstance(item, dict):
                    items.extend(flatten_nested_objects(item, f"{new_key}{sep}{i}", sep=sep).items())
                else:
                    items.append((f"{new_key}{sep}{i}", item))
        else:
            items.append((new_key, v))
    return dict(items)

def convert_to_timestamp(value):
    # If the value is already an integer (Unix timestamp)
    if isinstance(value, int):
        return value
    # If the value is a string that can be converted to an integer (Unix timestamp in string form)
    elif isinstance(value, str):
        # Try converting the string to an integer (it might be a Unix timestamp in string form)
        try:
            return int(value)
        except ValueError:
            # If it's not an integer string, try parsing it as an ISO 8601 datetime string
            try:
                dt = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
                return int(dt.timestamp())
            except ValueError:
                raise ValueError("The starting value is not valid ISO 8601 or Unix timestamp")
    else:
        raise ValueError("The starting value is neither an integer nor a valid string.")

class OloOmnivoreStream(RESTStream):
    """Omnivore stream base class for accessing the Omnivore API.

    This class handles:
      - URL construction based on a configurable base URL.
      - API key authentication via the "Api-Key" header.
      - Pagination by extracting the next page URL from the HAL+JSON _links.next.href.
      - Parsing of responses, expecting data under the _embedded property.
    """

    # Fallback JSONPath for records if _embedded is not used.
    records_jsonpath = "$[*]"

    @property
    def url_base(self) -> str:
        """Return the API URL root from the configuration."""
        return self.config.get("base_url", "https://api.omnivore.io/1.0")

    @property
    def authenticator(self) -> APIKeyAuthenticator:
        """Return an APIKeyAuthenticator for the Omnivore API.

        Uses the configuration property "api_key" to set the "Api-Key" header.
        """
        return APIKeyAuthenticator.create_for_stream(
            self,
            key="Api-Key",
            value=self.config.get("api_key", ""),
            location="header",
        )

    @property
    def schema(self) -> dict:
        schema_path = SCHEMAS_DIR / f"{self.name}.json"
        with schema_path.open("r", encoding="utf-8") as schema_file:
            return json.load(schema_file)

    @property
    def http_headers(self) -> dict:
        """Return any additional HTTP headers needed for the request."""
        headers: dict[str, str] = {}
        if self.config.get("user_agent"):
            headers["User-Agent"] = self.config["user_agent"]
        return headers

    def get_new_paginator(self) -> CustomHATEOASPaginator:
        """Return a new paginator instance using the custom pagination behavior."""
        return CustomHATEOASPaginator()

    def get_url_params(
        self,
        context: Context | None,
        next_page_token: t.Any | None,
    ) -> dict[str, t.Any]:
        """Return URL parameters for the API request.

        For Omnivore, if a next page token (which is the full URL) is provided, it will
        override URL parameterization. Otherwise, if a replication key is set, parameters for
        sorting may be added.
        """
        params: dict[str, t.Any] = {}
        if next_page_token:
            params.update(dict(parse_qsl(next_page_token.query)))
        starting_timestamp = self.get_starting_replication_key_value(context)
        if self.replication_key and starting_timestamp:
            starting_timestamp = convert_to_timestamp(starting_timestamp)
            params["where"] = f"gte({self.replication_key},{starting_timestamp})"
        return params

    def request_decorator(self, func: t.Callable) -> t.Callable:
        """Return a decorator that retries the function call on certain exceptions.

        The decorator retries on specific exceptions like:
        - RetriableAPIError
        - ReadTimeout
        - ConnectionError
        - RequestException
        - ConnectionRefusedError

        It uses exponential backoff with a maximum of 7 attempts and a factor of 2.
        """
        decorator: t.Callable = backoff.on_exception(
            backoff.expo,
            (
                RetriableAPIError,
                requests.exceptions.ReadTimeout,
                requests.exceptions.ConnectionError,
                requests.exceptions.RequestException,
                ConnectionRefusedError,
            ),
            max_tries=7,
            factor=2,
        )(func)
        return decorator

    def prepare_request_payload(
        self,
        context: Context | None,
        next_page_token: t.Any | None,
    ) -> dict | None:
        """Prepare the request payload.

        Omnivore API GET endpoints typically do not require a payload.
        """
        return None

    def parse_response(self, response: requests.Response) -> t.Iterable[dict]:
        """Parse the API response and yield individual records.

        Omnivore returns data in HAL+JSON format. Data is typically nested under the "_embedded"
        property. If a key matching the stream's name exists within _embedded, that will be used;
        otherwise, the first key found will be used. If _embedded is missing, a fallback JSONPath
        is used.
        """
        try:
            json_response = response.json(parse_float=decimal.Decimal)
        except requests.exceptions.JSONDecodeError as e:
            self.logger.error("Failed to decode JSON response: %s", e)
            return iter([])

        embedded = json_response.get("_embedded")
        if embedded:
            if self.name in embedded:
                records = embedded[self.name]
            else:
                records = next(iter(embedded.values()), [])
        else:
            records = extract_jsonpath(self.records_jsonpath, input=json_response)
        yield from records

    def post_process(
        self, row: dict, context: Context | None = None
    ) -> dict | None:
        """Perform post-processing on each record before output.

        This method first validates that primary and replication keys are present.
        Then, it extracts reference IDs from singular _links. Using a generic rule,
        it skips any link key that ends with "s" or is "self" and for the
        remaining keys, it appends '_id' to the key and assigns the last segment of the URL.
        Finally, it flattens nested objects.
        """
        # Validate primary keys
        if self.primary_keys:
            for pk in self.primary_keys:
                pk_value_in_row = row.get(pk)
                if pk_value_in_row is None:
                    # Primary key not in row or is None, check context
                    if context and context.get(pk) is not None:
                        # Found in context, add it to the row
                        row[pk] = context[pk]
                    else:
                        # Not in row and not in context (or context is None)
                        self.logger.warning(
                            f"Stream '{self.name}': Skipping record because primary key '{pk}' is missing or None in both row and context. Record: {row}"
                        )
                        return None

        # Validate replication key
        if self.replication_key:
            rk_value_in_row = row.get(self.replication_key)
            if rk_value_in_row is None:
                # Replication key not in row or is None, check context
                if context and context.get(self.replication_key) is not None:
                    # Found in context, add it to the row
                    row[self.replication_key] = context[self.replication_key]
                else:
                    # Not in row and not in context (or context is None)
                    self.logger.warning(
                        f"Stream '{self.name}': Skipping record because replication key '{self.replication_key}' is missing or None in both row and context. Record: {row}"
                    )
                    return None

        links = row.get("_links", {})
        for key, link_obj in links.items():
            # Skip keys that are plural or are exactly "self".
            if key == "self" or key.endswith("s"):
                continue
            if isinstance(link_obj, dict) and "href" in link_obj:
                ref_id = extract_id_from_href(link_obj["href"])
                new_key = f"{key}_id"
                row[new_key] = ref_id
        row = flatten_nested_objects(row)
        return row

    def validate_response(self, response: requests.Response) -> None:
        """Validate the response from the API.

        If the status code indicates success (200-299), the response is validated by
        the parent class. Otherwise, a warning is logged for unexpected status codes.
        """
        status_code = response.status_code
        if 200 <= status_code < 300:
            super().validate_response(response)
        else:
            self.logger.warning(
                "Received unexpected response status code: %s", status_code
            )
