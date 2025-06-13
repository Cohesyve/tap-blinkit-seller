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
from tap_blinkit_seller.streams.base import ReportStream

LOGGER = singer.get_logger()  # noqa


class OrderReportStream(ReportStream):
    API_METHOD = 'GET'
    # KEY_PROPERTIES will be defined in subclasses
    REPLICATION_METHOD = 'INCREMENTAL'  # Changed from FULL_TABLE
    REPLICATION_KEY = 'Order Date'  # Field name for bookmarking

    @property
    def api_path(self):
        return '/api/billing/download-sales-summary'
    
    def get_params(self):
        from_date_str = self.config.get('start_date', None)  # Default start date if no state
        # Ensure state is available in config, default to empty dict if None for get_last_record_value_for_table
        current_state = self.state
        
        last_sync_date_obj = get_last_record_value_for_table(current_state, self.TABLE)

        LOGGER.info(f"Last sync date for stream {self.TABLE}: {last_sync_date_obj}")

        if last_sync_date_obj:
            # last_sync_date_obj is a datetime.date object from state.py
            if isinstance(last_sync_date_obj, str):
                # Convert a date string like '5 May 2025' into a date object and add one day
                sync_start_date = datetime.strptime(last_sync_date_obj, "%d %B %Y").date() + timedelta(days=1)
            else:
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
        report_url = result['data']['url']
        report_data = requests.get(report_url)

        excel_file = pd.ExcelFile(io.BytesIO(report_data.content))

        results = []

        max_date_str_in_batch = None  # Stores max date as "MM/DD/YYYY" string

        try:
            raw_records = excel_file.parse(self.REPORT_NAME).to_dict(orient='records')
        except Exception as e:
            LOGGER.error(f"Failed to parse Excel sheet '{self.REPORT_NAME}' for stream {self.TABLE}. Error: {e}")
            return []

        if not raw_records:
            LOGGER.info(f"No records found in report for stream {self.TABLE}, sheet {self.REPORT_NAME}.")
            return []

        for record in raw_records:
            transformed_record = self.transform_record(record)
            results.append(transformed_record)

            # Update max_date_str_in_batch from the REPLICATION_KEY field (e.g., 'Date')
            current_record_date_value = transformed_record.get(self.REPLICATION_KEY)

            if current_record_date_value:
                try:
                    current_date_obj = None
                    if isinstance(current_record_date_value, datetime):
                        current_date_obj = current_record_date_value.date()
                    elif isinstance(current_record_date_value, date):
                        current_date_obj = current_record_date_value
                    elif isinstance(current_record_date_value, str):
                        try:
                            current_date_obj = datetime.strptime(current_record_date_value, "%d %B %Y").date()
                        except ValueError:
                            current_date_obj = parse(current_record_date_value).date()
                    else:
                        LOGGER.warning(
                            f"Date field '{self.REPLICATION_KEY}' has unexpected type: {type(current_record_date_value)} for record: {transformed_record}"
                        )
                        continue  # Skip if date cannot be processed

                    if max_date_str_in_batch is None or \
                       current_date_obj > parse(max_date_str_in_batch).date():
                        max_date_str_in_batch = current_date_obj.strftime("%Y-%m-%dT%H:%M:%SZ")
                except Exception as e:
                    LOGGER.error(
                        f"Error processing date '{current_record_date_value}' from field '{self.REPLICATION_KEY}' in stream {self.TABLE}. Record: {transformed_record}. Error: {e}"
                    )

        # After processing all records in the batch, update the state
        # Ensure state object exists in config; it's managed by the tap runner.
        current_state = self.state
        if max_date_str_in_batch and current_state is not None:
            LOGGER.info(f"Updating state for stream {self.TABLE} with {self.REPLICATION_KEY}: {max_date_str_in_batch}")
            self.state = incorporate(
                current_state,
                self.TABLE,
                self.REPLICATION_KEY,  # Field name, e.g., 'Date'
                max_date_str_in_batch  # Value, e.g., "MM/DD/YYYY"
            )
        elif current_state is None:
             LOGGER.warning(f"State object not found in config. Cannot update state for stream {self.TABLE}.")
        elif not max_date_str_in_batch and raw_records: # Processed records but no valid date found
            LOGGER.warning(f"No valid date found in batch to update state for stream {self.TABLE}.")

        return results


class OrderStream(OrderReportStream):
    TABLE = 'orders'
    REPORT_NAME = "Sales Summary Information"
    KEY_PROPERTIES = ['Order ID'] # Singer primary key