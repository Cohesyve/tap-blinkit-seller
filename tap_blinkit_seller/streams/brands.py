from tap_blinkit_seller.streams.base import BaseStream

import singer
import json

LOGGER = singer.get_logger()  # noqa


class BrandsStream(BaseStream):
    API_METHOD = 'GET'
    TABLE = 'brands'
    KEY_PROPERTIES = ['id']
    CACHE = True

    @property
    def api_path(self):
        return '/api/sellers/brand-details' 

    def get_stream_data(self, result):
        return [
            self.transform_record(record)
            for record in result['data']
        ]
