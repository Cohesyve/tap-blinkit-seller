from tap_blinkit_seller.streams.base import PaginatedStream

import singer
import json

LOGGER = singer.get_logger()  # noqa


class ShipmentStream(PaginatedStream):
    API_METHOD = 'GET'
    TABLE = 'invoices'
    KEY_PROPERTIES = ['sto_number']
    CACHE = True

    @property
    def api_path(self):
        return '/api/inventories/shipment-view'
    
    def get_params(self):
        return { "filter_type":"all"}
    
    def get_paginated_url(self, skip=0, count=10):
        base_url = self.get_url(self.api_path)
        url = f"{base_url}&offset={int(skip)}&limit={int(count)}"
        return url


    def get_stream_data(self, result):
        return [
            self.transform_record(record)
            for record in result['current_shipment_details']
        ]
