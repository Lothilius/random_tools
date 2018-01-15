__author__ = 'Lothilius'
# coding: utf-8

import datetime
import re
import sys

import pandas as pd
from Lever_Connection import LeverConnection as lhc
from helper_scripts.misc_helpers.data_manipulation import correct_date_dtype
from helper_scripts.misc_helpers.data_manipulation import create_feature_dataframe
from helper_scripts.misc_helpers.data_manipulation import expand_nested_fields_to_dataframe
from time import time
import collections
from Candidates import Candidates



pd.set_option('display.width', 350)
pd.set_option('display.max_columns', 50)
pd.set_option('display.max_colwidth', 50)


class Offers(object):
    """ The  class creates an object that gathers individual offers that belong to a particular list view.
    """
    def __init__(self, candidate_id, record_id=''):
        self.extra_fields = pd.DataFrame()
        self.candidate_id = candidate_id
        self.last_offer_id = record_id
        self.offer = self.get_all_offers(record_id)
        try:
            self.full_offer = pd.merge(self.offer, self.extra_fields, how='left', on='id')
        except ValueError:
            if self.extra_fields.empty:
                self.extra_fields = pd.DataFrame(data=[{'id': None, 'candidate_id': self.candidate_id}])
                self.full_offer = pd.DataFrame(data=[{'id': None, 'candidate_id': self.candidate_id}])
            else:
                error_result = "Unexpected error 2LO: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
                print error_result


    def __getitem__(self, item):
        return self.offer[item]

    def __str__(self):
        return str(self.offer)

    def aggregate_offers(self, offer_list_a, offer_list_b):
        """ Join to lists of lever records.

        :param offer_list_a: list
        :param offer_list_b: list
        :return: list - offer_list
        """
        offer_list = offer_list_a + offer_list_b

        return offer_list

    def get_100_offers(self, candidate_id='', offset='', record_id=''):
        """ Get lever records up to 100 at a time.
        :return: dict with lever offer info {data, hasNext[, next]}
        """
        url, querystring, headers = lhc.create_api_request(object='candidates/%s/offers' % (candidate_id),
                                                           offset=offset, record_id=record_id)

        return lhc.fetch_from_lever(url, querystring, headers)


    def gather_offer(self, lever_record_list, lever_records):
        try:
            self.record_cursor = lever_records['next']
            lever_records = self.get_100_offers(offset=self.record_cursor)
            lever_record_list = self.aggregate_offers(lever_record_list, lever_records['data'])

            lever_record_list, lever_records = self.gather_offer(lever_record_list, lever_records)
        except KeyError:
            pass

        return lever_record_list, lever_records


    def get_all_offers(self, record_id=''):
        try:
            # Get first 100 offer from lever
            lever_records = self.get_100_offers(candidate_id=self.candidate_id, record_id=record_id)
            # print type(lever_records['data'])
            lever_record_list = lever_records['data']
            if lever_record_list != []:
                # Check if more than 100 exist and need to be aggregated.
                if len(lever_record_list) == 100:
                    lever_record_list, lever_records = self.gather_offer(lever_record_list, lever_records)

                try:
                    # Convert offer list to Dataframe
                    lever_df = pd.DataFrame(lever_record_list)

                    lever_df = self.reformat_as_dataframe(lever_df)
                    # print lever_df
                    return lever_df
                except:
                    error_result = "Unexpected error 1TL: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
                    print error_result
            else:
                print "no offer found"
                self.offer = pd.DataFrame(data=[{'id': None, 'candidate_id': self.candidate_id}])



        except EOFError:
            error_result = "Unexpected error 1TL: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
            # TODO -Fix this issue so that error_message is populated!
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
    def reduce_to_year(unicode_series):
        try:
            pattern = re.compile("(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2})$")
            match = pattern.match(unicode_series)
            if match:
                date_only = unicode_series[:10]
                date_only = datetime.datetime.strptime(date_only, '%Y-%m-%d')
                return date_only
            else:
                return unicode_series

        except:
            pass

    def reformat_as_dataframe(self, offer_details):
        """ Use to reformat responses to a panda data frame.
        :param offer_details: Should be in the form of an array of dicts ie [{1,2,...,n},{...}...,{...}]
        :return: returns panda dataframe
        """
        offer_details = pd.DataFrame(offer_details)
        # print offer_details
        offer_details = offer_details.applymap(Offers.convert_time)

        # offer_details = offer_details.applymap(TicketList.reduce_to_year)
        offer_details = correct_date_dtype(offer_details, date_time_format='%Y-%m-%d %H:%M:%S')
        # offer_details.drop(labels=['content'], axis=1, inplace=True)

        # Convert extra fields nested in a dataframe column in to column with values
        self.extra_fields = create_feature_dataframe(offer_details, "id", "fields")
        self.extra_fields = expand_nested_fields_to_dataframe(self.extra_fields, "id", "text", "value")

        return offer_details


if __name__ == '__main__':
    start = time()
    # try:
    offers = Offers(candidate_id='9a5bca12-ef0e-42ba-bbb0-85e3155cc935')

    end = time()
    print (end - start) / 60
    print offers.full_offer
