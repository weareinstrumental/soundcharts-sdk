import json
import logging
import os
import requests
from urllib.parse import urlparse, parse_qs
from typing import Iterator

from soundcharts.errors import ConnectionError, IncorrectReponseType

logger = logging.getLogger(__name__)


class Client:
    def __init__(self, prefix=None):
        self._auth_headers = {
            "x-app-id": os.getenv("SOUNDCHARTS_APP_ID"),
            "x-api-key": os.getenv("SOUNDCHARTS_API_KEY"),
        }
        self._endpoint = os.getenv("SOUNDCHARTS_API_ENDPOINT", "https://customer.api.soundcharts.com")
        self._build_session()
        self._prefix = prefix
        self.language = None
        self.requests_timeout = 5

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
        except requests.exceptions.HTTPError as http_error:
            response = http_error.response

            try:
                errors = response.json()["errors"]
            except (ValueError, KeyError):
                errors = []

            raise ConnectionError(response.url, response.status_code, errors)
        except ValueError:
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

    def _get_paginated(self, url: str, params: dict = {}, listing_key: str = "items", max_limit: int = None) -> Iterator[dict]:
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
            # print(json.dumps(response))
            if response["page"]["next"]:
                parts = urlparse(response["page"]["next"])
                pagination_params = {k: v[0] for k, v in parse_qs(parts.query).items()}
                params = {**params, **pagination_params}
            else:
                return

    def _get_single_object(self, url: str, params: dict = None, payload: dict = None, obj_type: str = None):
        response = self._get(url, params=params, payload=payload)
        if obj_type and response.get("type") != obj_type:
            raise IncorrectReponseType("Expected type {}, received {}".format(obj_type, response.get("type")))
        return response.get("object")
