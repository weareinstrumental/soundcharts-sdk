import functools
import inspect
import json
import logging
import os
import requests
from urllib.parse import urlparse, parse_qs
from typing import Iterator

from soundcharts.errors import ConnectionError, IncorrectReponseType

logger = logging.getLogger(__name__)


def setprefix(prefix: str):
    """Sets the prefix to something other than default for this method, then resets it"""

    def decorator(func):
        # check if the function is a generator before wrapping it, otherwise it will behave differently
        if inspect.isgeneratorfunction(func):

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                obj = args[0]
                try:
                    orig_prefix = obj._prefix
                    obj._prefix = prefix
                    yield from func(*args, **kwargs)
                finally:
                    obj._prefix = orig_prefix

            return wrapper
        else:

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                obj = args[0]
                try:
                    orig_prefix = obj._prefix
                    obj._prefix = prefix
                    return func(*args, **kwargs)
                finally:
                    obj._prefix = orig_prefix

            return wrapper

    return decorator


class Client:
    def __init__(self, prefix=None, log_response=False):
        self._auth_headers = {
            "x-app-id": os.getenv("SOUNDCHARTS_APP_ID"),
            "x-api-key": os.getenv("SOUNDCHARTS_API_KEY"),
        }
        self._endpoint = os.getenv("SOUNDCHARTS_API_ENDPOINT", "https://customer.api.soundcharts.com")
        self._build_session()
        self._prefix = prefix
        self.language = None
        self.requests_timeout = 5
        self.log_response = log_response

    @property
    def auth_headers(self):
        return self._auth_headers

    def _build_session(self):
        self._session = requests.Session()

    def __del__(self):
        """Close session is currently connected"""
        if isinstance(self._session, requests.Session):
            self._session.close()

    def _internal_call(self, method: str, url: str, payload: dict, params: dict):
        args = dict(params=params)
        if self._prefix:
            url = self._prefix + url
        url = self._endpoint + url

        headers = self.auth_headers

        headers["Content-Type"] = "application/json"
        if payload:
            args["data"] = json.dumps(payload)

        if self.language is not None:
            headers["Accept-Language"] = self.language

        logger.debug(
            "Sending %s to %s with params: %s, headers: %s and body: %r ",
            method,
            url,
            args.get("params"),
            headers,
            args.get("data"),
        )

        try:
            response = self._session.request(method, url, headers=headers, timeout=self.requests_timeout, **args)

            if "x-quota-remaining" in response.headers:
                logger.info("Quota remaining: %s", response.headers["x-quota-remaining"])

            response.raise_for_status()
            results = response.json()

            if self.log_response:
                print(f"Response from API for url: {response.url}")
                print(json.dumps(results))
        except requests.exceptions.HTTPError as http_error:
            response = http_error.response

            try:
                errors = response.json()["errors"]
            except (ValueError, KeyError):
                errors = []

            raise ConnectionError(response.url, response.status_code, errors)
        except ValueError:
            if self.log_response:
                print(f"Response from API for url: {url}")
                print(json.dumps(response))

            results = None

        return results

    def _get(self, url: str, params: dict = None, payload: dict = None, **kwargs):
        if params:
            kwargs.update(params)

        return self._internal_call("GET", url=url, payload=payload, params=params)

    def _post(self, url: str, params: dict = None, payload: dict = None, **kwargs):
        if params:
            kwargs.update(params)

        return self._internal_call("POST", url=url, payload=payload, params=params)

    def _get_paginated(
        self, url: str, params: dict = {}, listing_key: str = "items", max_limit: int = None
    ) -> Iterator[dict]:
        page = 0
        item_count = 0
        while True:
            response = self._get(url, params=params)

            for item in response.get(listing_key):
                yield item
                item_count += 1

                if max_limit and item_count >= max_limit:
                    logger.info("Stopping API calls having reached max limit %d", item_count)
                    return

            page += 1
            logger.info("Received page %d, %d total items", page, response["page"]["total"])

            # continue if there were items on this page and a next page is indicated
            if response["page"]["next"] and response.get(listing_key):
                parts = urlparse(response["page"]["next"])
                pagination_params = {k: v[0] for k, v in parse_qs(parts.query).items()}
                params = {**params, **pagination_params}
            else:
                return

    def _get_single_object(self, url: str, params: dict = None, payload: dict = None, obj_type: str = None) -> dict:
        """helper function to get a single object from the API.

        Args:
            url (str): _description_
            params (dict, optional): _description_. Defaults to None.
            payload (dict, optional): _description_. Defaults to None.
            obj_type (str, optional): Optionally indicate the expected type, to be checked before anything returned.
            Defaults to None.

        Raises:
            IncorrectReponseType: _description_

        Returns:
            dict: _description_
        """
        response = self._get(url, params=params, payload=payload)

        if obj_type and response.get("type") != obj_type:
            raise IncorrectReponseType("Expected type {}, received {}".format(obj_type, response.get("type")))
        return response.get("object")
