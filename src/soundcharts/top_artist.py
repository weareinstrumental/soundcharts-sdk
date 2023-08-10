import logging
from typing import Dict, Iterator

from soundcharts.client import Client
from soundcharts.platform import SocialPlatform

logger = logging.getLogger(__name__)


class TopArtist(Client):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._prefix = "/api/v2/top-artist"

    def artists_by_platform_metric(
        self,
        platform: SocialPlatform,
        metric_type: str,
        sort_by: str = "total",
        period: str = "week",
        limit: int = None,
        max_limit: int = None,
        min_value: int = None,
        max_value: int = None,
        min_change: int = None,
        max_change: int = None,
    ) -> Iterator[Dict]:
        """Yield artists that match the given criteria for the given platform and metric type

        Args:
            platform (str): [description]
            metric_type (str): [description]
            sort_by (str, optional): [description]. Defaults to "total".
            period (str, optional): [description]. Defaults to "week".
            limit (int, optional): [description]. Defaults to None.
            max_limit (int, optional): [description]. Defaults to None.
            min_value (int, optional): [description]. Defaults to None.
            max_value (int, optional): [description]. Defaults to None.
            min_change (int, optional): [description]. Defaults to None.
            max_change (int, optional): [description]. Defaults to None.

        Returns:
            [type]: [description]
        """
        params = {
            "sortBy": sort_by,
            "period": period,
        }
        if limit:
            params["limit"] = limit

        if min_value and max_value:
            params["minValue"] = min_value
            params["maxValue"] = max_value
        elif min_value:
            params["minValue"] = min_value
            params["maxValue"] = min_value * 100
        elif max_value:
            params["minValue"] = 0
            params["maxValue"] = max_value

        # API requires both params to be set if one is
        if min_change and max_change:
            params["minChange"] = min_change
            params["maxChange"] = max_change
        elif min_change:
            params["minChange"] = min_change
            params["maxChange"] = min_change * 100
        elif max_change:
            params["minChange"] = 1
            params["maxChange"] = max_change

        url = "/{platform}/{metric_type}".format(platform=platform.value, metric_type=metric_type)
        yield from self._get_paginated(url, params=params, max_limit=max_limit)
