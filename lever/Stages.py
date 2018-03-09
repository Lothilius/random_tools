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

class Lever_Stages(object):
    """ The stage list class creates an object that gathers individual stages that belong to a particular list view.
    """
    def __init__(self, stage_id=''):
        self.record_cursor = None
        self.last_record_id = stage_id
        self.stages = self.get_all_lever_stages(stage_id)


    def __getitem__(self, item):
        return self.stages[item]

    def __str__(self):
        return str(self.stages)

    def aggregate_stages(self, stage_list_a, stage_list_b):
        """ Join to lists of lever records.

        :param stage_list_a: list
        :param stage_list_b: list
        :return: list - lever_stages
        """
        lever_stages = stage_list_a + stage_list_b

        return lever_stages

    @staticmethod
    def get_100_lever_stages(offset='', record_id=''):
        """ Get lever records up to 100 at a time.
        :return: dict with lever stage info {data, hasNext[, next]}
        """
        url, querystring, headers = lhc.create_api_request(object='stages', offset=offset, record_id=record_id)

        return lhc.fetch_from_lever(url, querystring, headers)

    def gather_lever_stages(self, lever_record_list, lever_records):
        try:
            self.record_cursor = lever_records['next']
            lever_records = self.get_100_lever_stages(offset=self.record_cursor)
            lever_record_list = self.aggregate_stages(lever_record_list, lever_records['data'])

            lever_record_list, next_lever_records = self.gather_lever_stages(lever_record_list, lever_records)
        except KeyError:
            pass

        return lever_record_list, lever_records

    def get_all_lever_stages(self, record_id=''):
        try:
            # Get first 100 stage from lever
            lever_records = self.get_100_lever_stages(record_id=record_id)
            # print type(lever_records['data'][0])
            lever_record_list = lever_records['data']

            # Check if more than 100 exist and need to be aggregated.
            if len(lever_record_list) == 100:
                lever_record_list, lever_records = self.gather_lever_stages(lever_record_list, lever_records)
            else:
                # lever_record_list = [lever_record_list]
                pass

            try:
                # Convert lever stage list to Dataframe
                lever_df = pd.DataFrame(lever_record_list)
                lever_df.rename(columns={'id': 'stage_id'}, inplace=True)
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
    def reformat_as_dataframe(stage_details):
        """ Use to reformat responses to a panda data frame.
        :param stage_details: Should be in the form of an array of dicts ie [{1,2,...,n},{...}...,{...}]
        :return: returns panda dataframe
        """
        stage_details = pd.DataFrame(stage_details)
        # TODO-Check Time zone values are sent in
        stage_details = stage_details.applymap(Lever_Stages.convert_time)

        stage_details = correct_date_dtype(stage_details, date_time_format='%Y-%m-%d %H:%M:%S',
                                           date_time_columns={'createdAt'})


        return stage_details


if __name__ == '__main__':
    start = time()
    try:
        stages = Lever_Stages()
    except AttributeError as e:
        stages = e.args[0]

    end = time()
    print (end - start) / 60
    # print type(reqs.stages)
    print stages.stages