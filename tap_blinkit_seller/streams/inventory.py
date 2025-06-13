from tap_blinkit_seller.streams.base import ChildStream
from tap_blinkit_seller.cache import stream_cache

import singer
import json

LOGGER = singer.get_logger()  # noqa

class InventoryStream(ChildStream):
    API_METHOD = 'GET'
    TABLE = 'inventory'
    KEY_PROPERTIES = ['item_id', 'facility_id']
    REPLICATION_METHOD = 'FULL_TABLE'
    warehouse_id = None

    def sync_data(self):
        for warehouse in stream_cache['warehouse']:

            url = self.get_url(f"/api/inventories/warehouse/{warehouse['facility_id']}/items")
            self.warehouse_id = warehouse['facility_id']

            self.sync_child_data(url=url)

    def get_stream_data(self, result):
        results = []

        LOGGER.info(f"Processing inventory data for warehouse: {self.warehouse_id}")

        for item in result["data"]['item_inventory']:
            transformed_record = self.transform_record(item)
            transformed_record['facility_id'] = self.warehouse_id
            LOGGER.info(f"Transformed record: {transformed_record}")
            results.append(transformed_record)

        return results