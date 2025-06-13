from tap_blinkit_seller.streams.base import BaseStream

import singer
import json

LOGGER = singer.get_logger()  # noqa


class BlinkitLocationStateStream(BaseStream):
    API_METHOD = 'GET'
    TABLE = 'blinkit_location_states'
    KEY_PROPERTIES = ['state_code']
    CACHE = True

    @property
    def api_path(self):
        return '/api/apob/details'

    def get_stream_data(self, result):
        return [
            self.transform_record(record)
            for record in result['data']['states']
        ]
