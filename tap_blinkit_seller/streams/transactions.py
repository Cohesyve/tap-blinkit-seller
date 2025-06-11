from tap_blinkit_seller.streams.base import BaseStream

import singer
import json

LOGGER = singer.get_logger()  # noqa


class TransactionStream(BaseStream):
    API_METHOD = 'GET'
    TABLE = 'transactions'
    KEY_PROPERTIES = ['transaction_data']
    CACHE = True

    @property
    def api_path(self):
        return '/api/cart/transactions'

    def get_stream_data(self, result):
        return [
            self.transform_record(record)
            for record in result['payment_details']
        ]
