__author__ = 'Lothilius'
# coding: utf-8

import datetime
import re
import sys

import pandas as pd
from Lever_Connection import LeverConnection as lhc
from helper_scripts.misc_helpers.data_manipulation import correct_date_dtype
from helper_scripts.misc_helpers.data_manipulation import create_feature_dataframe
from lever.Candidates import Candidates
from helper_scripts.misc_helpers.data_manipulation import expand_nested_fields_to_dataframe
from time import time
import collections
from Candidates import Candidates



pd.set_option('display.width', 350)
pd.set_option('display.max_columns', 50)
pd.set_option('display.max_colwidth', 50)


class Applications(object):
    """ The  class creates an object that gathers individual applications that belong to a particular list view.
    """
    def __init__(self, candidate_id, record_id=''):
        self.candidate_id = candidate_id

        self.extra_fields = pd.DataFrame()
        self.last_application_id = record_id
        self.application = self.get_all_applications(record_id)
        try:
            self.full_application = pd.merge(self.application, self.extra_fields, how='left', on='application_id',
                                             suffixes=('_application', '_fields'))
        except ValueError:
            if self.extra_fields.empty:
                self.extra_fields = pd.DataFrame(data=[{'application_id': None, 'candidate_id': self.candidate_id}])
                self.full_application = pd.DataFrame(data=[{'application_id': None, 'candidate_id': self.candidate_id}])
            else:
                error_result = "Unexpected error 2LO: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
                print error_result


    def __getitem__(self, item):
        return self.application[item]

    def __str__(self):
        return str(self.application)

    def aggregate_applications(self, application_list_a, application_list_b):
        """ Join to lists of lever records.

        :param application_list_a: list
        :param application_list_b: list
        :return: list - application_list
        """

        application_list = application_list_a + application_list_b

        return application_list

    def get_the_application(self, offset='', record_id=''):
        """ Get lever records up to 100 at a time.
        :return: dict with lever application info {data, hasNext[, next]}
        """
        url, querystring, headers = lhc.create_api_request(object='candidates/%s/applications' % (offset),
                                                           record_id=record_id)

        return lhc.fetch_from_lever(url, querystring, headers)


    def gather_application(self, lever_record_list='', lever_records=''):
        try:
            if isinstance(lever_record_list, str):
                lever_record_list = []
            if isinstance(self.candidate_id, list):
                self.record_cursor = self.candidate_id.pop()
            else:
                self.candidate_id = [self.candidate_id]
                self.record_cursor = self.candidate_id.pop()
            lever_records = self.get_the_application(offset=self.record_cursor)
            lever_record_list = self.aggregate_applications(lever_record_list, lever_records['data'])
            lever_record_list, lever_records = self.gather_application(lever_record_list, lever_records)
        except IndexError:
            pass

        return lever_record_list, lever_records


    def get_all_applications(self, record_id=''):
        try:
            # Gather the records for tall the submitted candidates
            lever_record_list, lever_records = self.gather_application()
            if lever_record_list != []:
                try:
                    # Convert application list to Dataframe
                    lever_df = pd.DataFrame(lever_record_list)
                    lever_df.rename(columns={'id': 'application_id'}, inplace=True)
                    lever_df = self.reformat_as_dataframe(lever_df)
                    # print lever_df
                    return lever_df
                except:
                    error_result = "Unexpected error 1TL: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
                    print error_result
            else:
                print "no application found"
                self.application = pd.DataFrame(data=[{'application_id': None, 'candidate_id': self.candidate_id}])



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

    def reformat_as_dataframe(self, application_details):
        """ Use to reformat responses to a panda data frame.
        :param application_details: Should be in the form of an array of dicts ie [{1,2,...,n},{...}...,{...}]
        :return: returns panda dataframe
        """
        application_details = pd.DataFrame(application_details)
        # print application_details
        application_details = application_details.applymap(Applications.convert_time)

        # application_details = application_details.applymap(TicketList.reduce_to_year)
        application_details = correct_date_dtype(application_details, date_time_format='%Y-%m-%d %H:%M:%S',
                                                 date_time_columns={'createdAt'})
        # application_details.drop(labels=['content'], axis=1, inplace=True)

        # Convert extra fields nested in a dataframe column in to column with values
        self.extra_fields = create_feature_dataframe(application_details, "application_id", "customQuestions")
        self.extra_fields.rename(columns={'id': 'form_id'}, inplace=True)
        self.extra_fields = correct_date_dtype(self.extra_fields, date_time_format='%Y-%m-%d %H:%M:%S',
                                               date_time_columns={'createdAt'})

        # self.extra_fields = expand_nested_fields_to_dataframe(self.extra_fields, "id", "text", "value")

        return application_details


if __name__ == '__main__':
    start = time()
    # try:
    stage_ids = ['44015e45-bbf3-447c-8517-55fe4540acdc', 'offer']
    # candidates = Candidates()
    # candidates = candidates.candidates
    # # print candidates
    # candidates_with_applications = candidates[candidates['stage'].isin(stage_ids)]['candidate_id']
    # print len(candidates_with_applications)
    # candidates.to_pickle('/Users/martin.valenzuela/Box Sync/Documents/Austin Office/BizReqs/Lever_API_595101/Lever_Candidates_')
    applications = Applications(candidate_id='9a5bca12-ef0e-42ba-bbb0-85e3155cc935')

    end = time()
    print (end - start) / 60
    print applications.extra_fields.columns
    print applications.application.columns
    print applications.full_application.columns
