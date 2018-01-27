__author__ = 'Lothilius'
# coding: utf-8

import datetime
import re
import sys

import pandas as pd
from pyprogressbar import Bar
from Lever_Connection import LeverConnection as lhc
from helper_scripts.misc_helpers.data_manipulation import correct_date_dtype
from time import time
from helper_scripts.misc_helpers.data_manipulation import multiply_by_multiselect


pd.set_option('display.width', 340)
pd.set_option('display.max_columns', 50)

class Archive_Reasons(object):
    """ The archive_reason list class creates an object that gathers individual archive_reasons that belong to a particular list view.
    """
    def __init__(self, archive_reason_id=''):
        self.record_cursor = None
        self.last_record_id = archive_reason_id
        self.archive_reasons = self.get_all_lever_archive_reasons(archive_reason_id)


    def __getitem__(self, item):
        return self.archive_reasons[item]

    def __str__(self):
        return str(self.archive_reasons)

    def aggregate_archive_reasons(self, archive_reason_list_a, archive_reason_list_b):
        """ Join to lists of lever records.

        :param archive_reason_list_a: list
        :param archive_reason_list_b: list
        :return: list - lever_archive_reasons
        """
        lever_archive_reasons = archive_reason_list_a + archive_reason_list_b

        return lever_archive_reasons

    @staticmethod
    def get_100_lever_archive_reasons(offset='', record_id=''):
        """ Get lever records up to 100 at a time.
        :return: dict with lever archive_reason info {data, hasNext[, next]}
        """
        url, querystring, headers = lhc.create_api_request(object='archive_reasons', offset=offset, record_id=record_id)

        return lhc.fetch_from_lever(url, querystring, headers)

    def gather_lever_archive_reasons(self, lever_record_list, lever_records):
        try:
            self.record_cursor = lever_records['next']
            lever_records = self.get_100_lever_archive_reasons(offset=self.record_cursor)
            lever_record_list = self.aggregate_archive_reasons(lever_record_list, lever_records['data'])

            lever_record_list, next_lever_records = self.gather_lever_archive_reasons(lever_record_list, lever_records)
        except KeyError:
            pass

        return lever_record_list, lever_records

    def get_all_lever_archive_reasons(self, record_id=''):
        try:
            # Get first 100 archive_reason from lever
            lever_records = self.get_100_lever_archive_reasons(record_id=record_id)
            # print type(lever_records['data'][0])
            lever_record_list = lever_records['data']

            # Check if more than 100 exist and need to be aggregated.
            if len(lever_record_list) == 100:
                lever_record_list, lever_records = self.gather_lever_archive_reasons(lever_record_list, lever_records)
            else:
                # lever_record_list = [lever_record_list]
                pass

            try:
                # Convert lever archive_reason list to Dataframe
                lever_df = pd.DataFrame(lever_record_list)
                lever_df.rename(columns={'id': 'archive_reason_id'}, inplace=True)
                lever_df = self.reformat_as_dataframe(lever_df)
                return lever_df

            except:
                error_result = "Unexpected error 1TL: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
                print error_result

        except EOFError:
            error_result = "Unexpected error 1TL: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
            print error_result

    @staticmethod
    def convert_time(unicode_series):
        """Given value for date time
            Convert it to a regular datetime string"""
        # for each in unicode_series:
        # print unicode_series
        try:
            unicode_series = int(unicode_series)
            if len(str(unicode_series)) == 10 or len(str(unicode_series)) == 13:
                if len(str(unicode_series)) == 10:
                    unicode_series = str(unicode_series)
                elif len(str(unicode_series)) == 13:
                    unicode_series = str(unicode_series)[:10]
                date_time_value = datetime.datetime.fromtimestamp(int(unicode_series)).strftime('%Y-%m-%d %H:%M:%S')
                if int(date_time_value[:4]) > 2009:
                    return date_time_value
                else:
                    return str(unicode_series)
            else:
                return str(unicode_series)
        except:
            return unicode_series

    @staticmethod
    def reformat_as_dataframe(archive_reason_details):
        """ Use to reformat responses to a panda data frame.
        :param archive_reason_details: Should be in the form of an array of dicts ie [{1,2,...,n},{...}...,{...}]
        :return: returns panda dataframe
        """
        archive_reason_details = pd.DataFrame(archive_reason_details)
        archive_reason_details = archive_reason_details.applymap(Archive_Reasons.convert_time)

        archive_reason_details = correct_date_dtype(archive_reason_details, date_time_format='%Y-%m-%d %H:%M:%S',
                                           date_time_columns={'createdAt'})


        return archive_reason_details


if __name__ == '__main__':
    start = time()
    try:
        archive_reasons = Archive_Reasons()
    except AttributeError as e:
        archive_reasons = e.args[0]

    end = time()
    print (end - start) / 60
    # print type(reqs.archive_reasons)
    print archive_reasons.archive_reasons