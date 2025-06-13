from tap_blinkit_seller.streams.base import BaseStream
import io
import json
import time
from datetime import datetime, timedelta, date # Added date

import pandas as pd
import requests
import singer
from dateutil.parser import parse # Added parse

from tap_blinkit_seller.cache import stream_cache
# Updated import to include incorporate
from tap_blinkit_seller.state import (get_last_record_value_for_table,
                                   incorporate)

LOGGER = singer.get_logger()  # noqa

class PayoutStream(BaseStream):
    API_METHOD = 'GET'
    TABLE = 'payouts'
    KEY_PROPERTIES = ['pyrefid']
    REPLICATION_KEY = 'cycle_end_timestamp'
    CACHE = True

    @property
    def api_path(self):
        return '/api/billing/payouts/past-cycles'
    
    def get_params(self):
        from_date_str = self.config.get('start_date', None)  # Default start date if no state
        # Ensure state is available in config, default to empty dict if None for get_last_record_value_for_table
        current_state = self.state
        
        last_sync_date_obj = get_last_record_value_for_table(current_state, self.TABLE)

        LOGGER.info(f"Last sync date for stream {self.TABLE}: {last_sync_date_obj}")

        if last_sync_date_obj:
            # last_sync_date_obj is a datetime.date object from state.py
            sync_start_date = last_sync_date_obj + timedelta(days=1)
        else:  # Parse initial start date
            sync_start_date = datetime.strptime(from_date_str, '%d/%m/%Y').date()

        today = date.today()
        sync_end_date = sync_start_date + timedelta(days=90)

        if sync_end_date > today:
            sync_end_date = today

        from_date_str = int(time.mktime(sync_start_date.timetuple()))
        to_date_str = int(time.mktime(sync_end_date.timetuple()))

        LOGGER.info(f"Stream {self.TABLE}: Fetching data from {from_date_str} to {to_date_str}")

        return {
            "start_date": from_date_str,
            "end_date": to_date_str
        }

    def get_stream_data(self, result):
        results = []
        max_timestamp = None

        for record in result['data']:
            transformed_record = self.transform_record(record)
            results.append(transformed_record)

            # Update max_timestamp from the REPLICATION_KEY field (cycle_end_timestamp)
            current_timestamp = record.get(self.REPLICATION_KEY)

            if current_timestamp:
                try:
                    current_timestamp = int(current_timestamp)  # Ensure it's an integer
                    if max_timestamp is None or current_timestamp > max_timestamp:
                        max_timestamp = current_timestamp
                except ValueError as e:
                    LOGGER.error(
                        f"Error processing timestamp '{current_timestamp}' from field '{self.REPLICATION_KEY}' in stream {self.TABLE}. Record: {record}. Error: {e}"
                    )

        # After processing all records in the batch, update the state
        current_state = self.state
        if max_timestamp is not None and current_state is not None:
            LOGGER.info(f"Updating state for stream {self.TABLE} with {self.REPLICATION_KEY}: {max_timestamp}")
            self.state = incorporate(
                current_state,
                self.TABLE,
                self.REPLICATION_KEY,  # Field name, e.g., 'cycle_end_timestamp'
                datetime.fromtimestamp(max_timestamp).isoformat()  # Value, e.g., 1748629800
            )
        elif current_state is None:
            LOGGER.warning(f"State object not found in config. Cannot update state for stream {self.TABLE}.")
        elif not max_timestamp and result:  # Processed records but no valid timestamp found
            LOGGER.warning(f"No valid timestamp found in batch to update state for stream {self.TABLE}.")

        return results
