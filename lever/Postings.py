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
from se_helpers.actions import wait


pd.set_option('display.width', 183)
pd.set_option('display.max_columns', 50)
pd.set_option('display.max_colwidth', 25)


class Postings(object):
    """ The Postings list class creates an object that gathers individual postings that are in Lever.
    """
    def __init__(self, record_id=''):
        self.categories = pd.DataFrame()
        self.content = pd.DataFrame()
        self.last_posting_id = record_id
        self.postings = self.get_all_postings(record_id)
        self.full_postings = pd.merge(pd.merge(self.postings, self.categories, how='left', on='post_id')
                                      , self.content, how='left', on='post_id')


    def __getitem__(self, item):
        return self.postings[item]

    def __str__(self):
        return str(self.postings)

    def aggregate_postings(self, posting_list_a, posting_list_b):
        """ Join to lists of lever records.

        :param posting_list_a: list
        :param posting_list_b: list
        :return: list - lever_postings
        """
        lever_postings = posting_list_a + posting_list_b

        return lever_postings

    def get_100_postings(self, offset='', record_id=''):
        """ Get lever records up to 100 at a time.
        :return: dict with lever requisition info {data, hasNext[, next]}
        """
        url, querystring, headers = lhc.create_api_request(object='postings', offset=offset, record_id=record_id)

        return lhc.fetch_from_lever(url, querystring, headers)


    def gather_postings(self, lever_record_list, lever_records):
        try:
            self.record_cursor = lever_records['next']
            lever_records = self.get_100_postings(offset=self.record_cursor)
            lever_record_list = self.aggregate_postings(lever_record_list, lever_records['data'])

            lever_record_list, lever_records = self.gather_postings(lever_record_list, lever_records)
        except KeyError:
            pass

        return lever_record_list, lever_records


    def get_all_postings(self, record_id=''):
        try:
            # Get first 100 posts from lever
            lever_records = self.get_100_postings(record_id=record_id)
            # print type(lever_records['data'])
            lever_record_list = lever_records['data']

            # Check if more than 100 exist and need to be aggregated.
            if len(lever_record_list) == 100:
                lever_record_list, lever_records = self.gather_postings(lever_record_list, lever_records)

            try:

                # Convert posting list to Dataframe
                lever_df = pd.DataFrame(lever_record_list)
                lever_df.rename(columns={'id': 'post_id'}, inplace=True)
                lever_df = self.reformat_as_dataframe(lever_df)

                return lever_df

            except:
                error_result = "Unexpected error 2TL: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
                print error_result
                # raise Exception(error_result + str(lever_df))
        except Exception:
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
                if int(date_time_value[:4]) > 2004:
                    return date_time_value
                else:
                    return str(unicode_series)
            else:
                return str(unicode_series)
        except:
            return unicode_series

    def reformat_as_dataframe(self, posting_details):
        """ Use to reformat responses to a panda data frame.
        :param posting_details: Should be in the form of an array of dicts ie [{1,2,...,n},{...}...,{...}]
        :return: returns panda dataframe
        """
        posting_details = pd.DataFrame(posting_details)
        posting_details['tags'] = posting_details['tags'].apply(lambda x: ', '.join(x))
        posting_details = posting_details.applymap(Postings.convert_time)

        posting_details = correct_date_dtype(posting_details, date_time_format='%Y-%m-%d %H:%M:%S',
                                             date_time_columns={'updatedAt', 'createdAt'})

        self.categories = create_feature_dataframe(posting_details, "post_id", "categories")
        self.content = create_feature_dataframe(posting_details, "post_id", "content")

        # posting_details.drop(labels=['content'], axis=1, inplace=True)

        return posting_details


if __name__ == '__main__':
    start = time()

    posts = Postings()

    end = time()
    print (end - start) / 60
    print posts.full_postings
