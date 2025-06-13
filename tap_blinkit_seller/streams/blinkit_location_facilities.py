from tap_blinkit_seller.streams.base import ChildStream
from tap_blinkit_seller.cache import stream_cache

import singer
import json

LOGGER = singer.get_logger()  # noqa

class BlinkitLocationFacilityStream(ChildStream):
    API_METHOD = 'GET'
    TABLE = 'blinkit_location_facilities'
    KEY_PROPERTIES = ['facility_id']
    REPLICATION_METHOD = 'FULL_TABLE'

    def sync_data(self):
        for state in stream_cache['blinkit_location_states']:

            url = self.get_url(f"/api/apob/details")
            if state['status'] != "ACTIVE":
                LOGGER.info(f"Skipping state {state['name']} as it is {state['status']}.")
                continue

            params = {
                "state_code": state['state_code']
            }
            self.sync_child_data(url=url, params=params)

    def get_stream_data(self, result):
        results = []

        state_details = result["data"]["apob_details"]["header"]

        for tab in result["data"]["apob_details"]["location"]["tabs"]:
            if tab["tab_name"] == "Inactive locations":
                for facility in tab["facilities"]:
                    transformed_record = self.transform_record(facility)
                    transformed_record['is_active'] = False
                    transformed_record['state_code'] = state_details['state_code']
                    transformed_record['state_name'] = state_details['name']
                    LOGGER.info(f"Transformed record: {transformed_record}")
                    results.append(transformed_record)
            elif tab["tab_name"] == "Active locations":
                for facility in tab["facilities"]:
                    transformed_record = self.transform_record(facility)
                    transformed_record['is_active'] = True
                    transformed_record['state_code'] = state_details['state_code']
                    transformed_record['state_name'] = state_details['name']
                    LOGGER.info(f"Transformed record: {transformed_record}")
                    results.append(transformed_record)

        return results