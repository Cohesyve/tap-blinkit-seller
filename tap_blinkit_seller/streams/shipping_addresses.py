from tap_blinkit_seller.streams.base import BaseStream

import singer
import json

LOGGER = singer.get_logger()  # noqa


class ShippingAddressStream(BaseStream):
    API_METHOD = 'GET'
    TABLE = 'shipping_addresses'
    KEY_PROPERTIES = ['id']
    CACHE = True

    @property
    def api_path(self):
        return '/api/sellers/shipping-address'

    def get_stream_data(self, result):
        return [
            self.transform_record(record)
            for record in result['data']
        ]
