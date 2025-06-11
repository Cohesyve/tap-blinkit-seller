from tap_blinkit_seller.streams.base import BaseStream

import singer
import json

LOGGER = singer.get_logger()  # noqa


class InvoicesStream(BaseStream):
    API_METHOD = 'GET'
    TABLE = 'invoices'
    KEY_PROPERTIES = ['order_id']
    CACHE = True

    @property
    def api_path(self):
        return '/api/billing/invoices'

    def get_stream_data(self, result):
        return [
            self.transform_record(record)
            for record in result['invoices']
        ]
