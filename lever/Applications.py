__author__ = 'Lothilius'
# coding: utf-8

import datetime
import re
import sys

import pandas as pd
from pyprogressbar import Bar
from Lever_Connection import LeverConnection as lhc
from helper_scripts.misc_helpers.data_manipulation import correct_date_dtype
from helper_scripts.misc_helpers.data_manipulation import create_feature_dataframe
from time import time
from helper_scripts.misc_helpers.data_manipulation import multiply_by_multiselect


pd.set_option('display.width', 350)
pd.set_option('display.max_columns', 50)
pd.set_option('display.max_colwidth', 50)

class Requisitions(object):
    """ The requisition list class creates an object that gathers individual requisitions that are published on Lever.
    """
    def __init__(self, record_id=''):
        self.compensation_band = pd.DataFrame()
        self.custom_fields = pd.DataFrame()
        self.record_cursor = None
        self.last_requisition_id = record_id
        self.requisitions = self.get_all_requisitions(record_id)
        self.full_requisitions = pd.merge(pd.merge(self.requisitions, self.compensation_band, how='left', on='id'),
                                      self.custom_fields,how='left', on='id')



    def __getitem__(self, item):
        return self.requisitions[item]

    def __str__(self):
        return str(self.requisitions)

    def aggregate_requisitions(self, requisition_list_a, requisition_list_b):
        """ Join to lists of lever records.

        :param requisition_list_a: list
        :param requisition_list_b: list
        :return: list - lever_requisitions
        """
        lever_requisitions = requisition_list_a + requisition_list_b

        return lever_requisitions

    def get_100_requisitions(self, offset='', record_id=''):
        """ Get lever records up to 100 at a time.
        :return: dict with lever requisition info {data, hasNext[, next]}
        """
        url, querystring, headers = lhc.create_api_request(offset=offset, record_id=record_id)

        return lhc.fetch_from_lever(url, querystring, headers)


    def gather_requisitions(self, lever_record_list, lever_records):
        try:
            self.record_cursor = lever_records['next']
            lever_records = self.get_100_requisitions(offset=self.record_cursor)
            lever_record_list = self.aggregate_requisitions(lever_record_list, lever_records['data'])

            lever_record_list, next_lever_records = self.gather_requisitions(lever_record_list, lever_records)
        except KeyError:
            pass

        return lever_record_list, lever_records


    def get_all_requisitions(self, record_id=''):
        try:
            # Get first 100 requisition from lever
            lever_records = self.get_100_requisitions(record_id=record_id)
            # print type(lever_records['data'])
            lever_record_list = lever_records['data']

            # Check if more than 100 exist and need to be aggregated.
            if len(lever_record_list) == 100:
                lever_record_list, lever_records = self.gather_requisitions(lever_record_list, lever_records)
            else:
                lever_record_list = [lever_record_list]

            try:
                # Convert lever requisition list to Dataframe
                lever_df = pd.DataFrame(lever_record_list)
                lever_df = self.reformat_as_dataframe(lever_df)
                # print lever_df

            except:
                error_result = "Unexpected error 2TL: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
                print error_result
                # raise Exception(error_result)

            return lever_df
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

    def reformat_as_dataframe(self, requisition_details):
        """ Use to reformat responses to a panda data frame.
        :param requisition_details: Should be in the form of an array of dicts ie [{1,2,...,n},{...}...,{...}]
        :return: returns panda dataframe
        """
        requisition_details = pd.DataFrame(requisition_details)
        requisition_details = requisition_details.applymap(Requisitions.convert_time)

        requisition_details = correct_date_dtype(requisition_details, date_time_format='%Y-%m-%d %H:%M:%S',
                                                 date_time_columns={'updatedAt', 'createdAt'})

        self.compensation_band = create_feature_dataframe(requisition_details, "id", "compensationBand")
        self.custom_fields = create_feature_dataframe(requisition_details, "id", "customFields")

        # Duplicate records by number of postings
        requisition_details = multiply_by_multiselect(requisition_details, "id", "postings")

        return requisition_details


if __name__ == '__main__':
    start = time()
    try:
        reqs = Requisitions()
    except AttributeError as e:
        reqs = e.args[0]

    end = time()
    print (end - start) / 60
    # print type(reqs.requisitions)
    print reqs.full_requisitions