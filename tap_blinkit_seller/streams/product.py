from tap_blinkit_seller.streams.base import PaginatedStream

import singer
import json

LOGGER = singer.get_logger()  # noqa


class ProductStream(PaginatedStream):
    API_METHOD = 'GET'
    TABLE = 'products'
    KEY_PROPERTIES = ['id']
    CACHE = True

    @property
    def api_path(self):
        return '/api/catalog/dashboard-products?sort_by=RELEVANCE&filtering_enabled=true'
    
    def get_params(self):
        return {
            "sort_by": "RELEVANCE",
            "filtering_enabled": "true"
        }
    
    def get_paginated_url(self, skip=0, count=10):
        base_url = self.get_url(self.api_path)
        url = f"{base_url}&page={int(skip)}"
        return url

    def get_stream_data(self, result):
        return [
            self.transform_record(record)
            for record in result['results']
        ]
