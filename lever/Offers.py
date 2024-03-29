__author__ = 'Lothilius'
# coding: utf-8

import datetime
import re
import sys

import pandas as pd
from lever.Lever_Connection import LeverConnection as lhc
from helper_scripts.misc_helpers.data_manipulation import correct_date_dtype
from helper_scripts.misc_helpers.data_manipulation import create_feature_dataframe

from lever.Candidates import Candidates
from helper_scripts.misc_helpers.data_manipulation import expand_nested_fields_to_dataframe
from time import time

import traceback



pd.set_option('display.width', 350)
pd.set_option('display.max_columns', 50)
pd.set_option('display.max_colwidth', 50)


class Offers(object):
    """ The  class creates an object that gathers individual offers that belong to a particular list view.
    """
    def __init__(self, candidate_id, record_id=''):
        self.candidate_id = candidate_id
        self.record_cursor = record_id
        self.extra_fields = pd.DataFrame()
        self.last_offer_id = record_id
        self.offer = self.get_all_offers(record_id)
        try:
            self.full_offer = pd.merge(self.offer, self.extra_fields, how='left', on='offer_id',
                                             suffixes=('_offer', '_fields'))
        except ValueError:
            if self.extra_fields.empty:
                self.extra_fields = pd.DataFrame(data=[{'offer_id': None, 'candidate_id': self.candidate_id}])
                self.full_offer = pd.DataFrame(data=[{'offer_id': None, 'candidate_id': self.candidate_id}])
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

    def get_the_offer(self, record_id=''):
        """ Get lever records up to 100 at a time.
        :return: dict with lever offer info {data, hasNext[, next]}
        """
        url, querystring, headers = lhc.create_api_request(object='candidates/%s/offers' % record_id)

        return lhc.fetch_from_lever(url, querystring, headers)

    def gather_offer(self, lever_record_list='', lever_records=''):
        try:
            if isinstance(lever_record_list, str):
                lever_record_list = []
            if isinstance(self.candidate_id, list):
                if len(self.candidate_id) != 0:
                    self.record_cursor = self.candidate_id.pop()
            else:
                self.candidate_id = [self.candidate_id]
                self.record_cursor = self.candidate_id.pop()
            lever_records = self.get_the_offer(record_id=self.record_cursor)
            if lever_records['data'] == []:
                candidates_id = self.record_cursor
                lever_records['data'] = [{'id': '-', 'candidate_id': candidates_id, 'fields': ['No fields']}]
            else:
                lever_records['data'][0]['candidate_id'] = self.record_cursor
            lever_record_list = self.aggregate_offers(lever_record_list, lever_records['data'])
            if len(self.candidate_id) != 0:
                lever_record_list, lever_records = self.gather_offer(lever_record_list, lever_records)
        except IndexError:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            error_result = "Unexpected error 1go: %s, %s, %s" % \
                           (sys.exc_info()[0], sys.exc_info()[1], traceback.format_exc())
            print error_result
        except KeyError:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            error_result = "Unexpected error 2gp_ke: %s, %s, %s" % \
                           (sys.exc_info()[0], sys.exc_info()[1], traceback.format_exc())
            print error_result
            print lever_records


        return lever_record_list, lever_records


    def get_all_offers(self, record_id=''):
        try:
            # Gather the records for all the submitted candidates
            lever_record_list, lever_records = self.gather_offer()
            if lever_record_list != []:
                try:
                    # Convert offer list to Dataframe
                    lever_df = pd.DataFrame(lever_record_list)
                    lever_df.rename(columns={'id': 'offer_id'}, inplace=True)
                    lever_df = self.reformat_as_dataframe(lever_df)
                    # print lever_df
                    return lever_df
                except:
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    traceback.print_exception(exc_type, exc_value, exc_traceback)
                    error_result = "Unexpected Error: %s, %s, %s" \
                                   % (exc_type, exc_value, traceback.format_exc())
                    print error_result
            else:
                print 'Offers List empty'
                # self.offer = pd.DataFrame(data=[{'offer_id': '-', 'candidate_id': self.candidate_id}])



        except EOFError:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            error_result = "Unexpected Error: %s, %s, %s" \
                           % (exc_type, exc_value, traceback.format_exc())
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

    def reformat_as_dataframe(self, offer_details):
        """ Use to reformat responses to a panda data frame.
        :param offer_details: Should be in the form of an array of dicts ie [{1,2,...,n},{...}...,{...}]
        :return: returns panda dataframe
        """
        offer_details = pd.DataFrame(offer_details)
        # print offer_details
        offer_details = offer_details.applymap(Offers.convert_time)

        # offer_details = offer_details.applymap(TicketList.reduce_to_year)
        offer_details = correct_date_dtype(offer_details, date_time_format='%Y-%m-%d %H:%M:%S',
                                                 date_time_columns={'createdAt', 'approvedAt', 'sentAt'})
        # offer_details.drop(labels=['content'], axis=1, inplace=True)

        # Convert extra fields nested in a dataframe column in to column with values
        feature_dataframe = create_feature_dataframe(offer_details, "offer_id", "fields")
        # print feature_dataframe
        # feature_dataframe.drop(columns=[''], axis=1, inplace=True)
        # feature_dataframe.drop(0, inplace=True)
        feature_dataframe.fillna('-', inplace=True)
        feature_dataframe = correct_date_dtype(feature_dataframe, date_time_format='%Y-%m-%d %H:%M:%S',
                                               date_time_columns={'createdAt', "Today's date", 'Anticipated start date',
                                                                  'End date (Intern/co-op or Contractor)',
                                                                  'NHO date', 'Vesting commencement (Date)',
                                                                  'Vesting commencement date (MM/DD/YYYY)',
                                                                  "Today's date", 'Anticipated start date', 'NHO date'})
        if feature_dataframe.empty:
            pass
        else:
            self.extra_fields = expand_nested_fields_to_dataframe(feature_dataframe, "offer_id", "text", "value")
            self.extra_fields.rename(columns={'Type (new, rehire, internal, contractor/intern conversion)': 'Type'},
                                 inplace=True)

        return offer_details


if __name__ == '__main__':
    start = time()
    # try:
    stage_ids = ['44015e45-bbf3-447c-8517-55fe4540acdc', 'offer']
    today = datetime.datetime.today()
    current_month = today.replace(day=28, hour=0, minute=0, second=0, microsecond=0)
    beginning_of_three_months_ago = current_month - pd.offsets.MonthBegin(1)
    beginning_of_three_months_ago = beginning_of_three_months_ago.value / 1000000

    candidates = Candidates(date_limit=beginning_of_three_months_ago)
    candidate_stages_ids = candidates.stages[['candidate_id', 'toStageId']]
    candidates_with_offers = candidate_stages_ids[candidate_stages_ids['toStageId'].isin(stage_ids)]['candidate_id']
    candidates_with_offers = candidates_with_offers.copy()
    # print len(candidates_with_offers)
    candidates_with_offers.drop_duplicates(inplace=True)
    candidates_with_offers = candidates_with_offers.tolist()
    offers = Offers(candidate_id=candidates_with_offers)

    end = time()
    print (end - start) / 60
    # print offers.offer.columns
    print offers.offer
    print offers.extra_fields.columns
    print offers.extra_fields
    print offers.full_offer.columns
    print offers.full_offer
