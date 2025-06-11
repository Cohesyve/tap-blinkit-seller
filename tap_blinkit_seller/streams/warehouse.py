from tap_blinkit_seller.streams.base import BaseStream

import singer
import json

LOGGER = singer.get_logger()  # noqa


class WarehouseStream(BaseStream):
    API_METHOD = 'GET'
    TABLE = 'warehouse'
    KEY_PROPERTIES = ['facility_id']
    CACHE = True

    @property
    def api_path(self):
        return '/api/inventories/warehouses'

    def get_stream_data(self, result):
        return [
            self.transform_record(record)
            for record in result
        ]
