__author__ = 'Lothilius'
# coding: utf-8

import datetime
import re
import sys

import pandas as pd
from pyprogressbar import Bar
from Lever_Connection import LeverConnection as lhc
from helper_scripts.misc_helpers.data_manipulation import correct_date_dtype
from helper_scripts.misc_helpers.data_manipulation import multiply_by_multiselect
from helper_scripts.misc_helpers.data_manipulation import create_feature_dataframe
from datetime import date
from dateutil.parser import *
from time import time
from se_helpers.actions import wait

pd.set_option('display.width', 350)
pd.set_option('display.max_columns', 50)
pd.set_option('display.max_colwidth', 50)


class Candidates(object):
    """ The candidate list class creates an object that gathers individual candidates that belong to a particular list view.

    """

    def __init__(self, record_id='', date_limit=''):
        """
        :param record_id:
        :param datelimit:
        """
        self.date_limit = date_limit
        self.stages = pd.DataFrame()
        self.last_candidate_id = record_id
        self.candidates = self.get_all_candidates(record_id)
        print 'waiting for merge'
        self.full_candidates = pd.merge(self.candidates, self.stages, how='left', on='candidate_id')


    def __getitem__(self, item):
        return self.candidates[item]

    def __str__(self):
        return str(self.candidates)

    def aggregate_candidates(self, candidate_list_a, candidate_list_b):
        """ Join to lists of lever records.

        :param candidate_list_a: list
        :param candidate_list_b: list
        :return: list - candidate_list
        """
        candidate_list = candidate_list_a + candidate_list_b

        return candidate_list

    def get_100_candidates(self, offset='', record_id='', **kwargs):
        """ Get lever records up to 100 at a time.
        :return: dict with lever requisition info {data, hasNext[, next]}
        """
        url, querystring, headers = lhc.create_api_request(object='candidates',
                                                           offset=offset,
                                                           record_id=record_id,
                                                           **kwargs)

        return lhc.fetch_from_lever(url, querystring, headers)

    def gather_candidates(self, lever_record_list, lever_records):
        try:
            self.record_cursor = lever_records['next']
            lever_records = self.get_100_candidates(offset=self.record_cursor, updated_at_start=self.date_limit)
            lever_record_list = self.aggregate_candidates(lever_record_list, lever_records['data'])

            lever_record_list, lever_records = self.gather_candidates(lever_record_list, lever_records)
        except KeyError:
            pass

        return lever_record_list, lever_records

    def get_all_candidates(self, record_id=''):
        try:
            # Get first 100 candidate from lever
            lever_records = self.get_100_candidates(record_id=record_id, updated_at_start=self.date_limit)
            # print type(lever_records['data'])
            lever_record_list = lever_records['data']

            # Check if more than 100 exist and need to be aggregated.
            if len(lever_record_list) == 100:
                lever_record_list, lever_records = self.gather_candidates(lever_record_list, lever_records)

            try:
                # Convert lever candidate list to Dataframe
                lever_df = pd.DataFrame(lever_record_list)
                lever_df.rename(columns={'id': 'candidate_id'}, inplace=True)
                lever_df = self.reformat_as_dataframe(lever_df)
                return lever_df

            except EOFError:
                error_result = "Unexpected error 1TL: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
                print error_result
                # raise Exception(error_result)

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
                if int(date_time_value[:4]) > 2004:
                    return date_time_value
                else:
                    return str(unicode_series)
            else:
                return str(unicode_series)
        except:
            return unicode_series

    @staticmethod
    def create_hired_stage_entry(row):
        if pd.isnull(row['archivedAt']):
           return row
        else:
            row['stageChanges'].append({u'toStageIndex': 14, u'userId': row['owner'], u'toStageId': row['reason'],
                                        u'updatedAt': row['archivedAt']})
            return row


    def reformat_as_dataframe(self, candidate_details):
        """ Use to reformat responses to a panda data frame.
        :param candidate_details: Should be in the form of an array of dicts ie [{1,2,...,n},{...}...,{...}]
        :return: returns panda dataframe
        """
        candidate_details = pd.DataFrame(candidate_details)
        candidate_details['sources'] = candidate_details['sources'].apply(lambda x: ', '.join(x))
        # Move archived reason to main dataframe
        archived = create_feature_dataframe(candidate_details, "candidate_id", "archived")
        archived.drop(columns=0, axis=1, inplace=True)
        candidate_details = pd.merge(candidate_details, archived, how='left', on='candidate_id')

        # Change Unix time to date time values.
        candidate_details = candidate_details.applymap(Candidates.convert_time)
        candidate_details[['owner', 'reason', 'archivedAt', 'stageChanges']] = \
            candidate_details[['owner',
                                'reason',
                                'archivedAt',
                                'stageChanges']].apply(self.create_hired_stage_entry, axis=1)

        candidate_details = correct_date_dtype(candidate_details, date_time_format='%Y-%m-%d %H:%M:%S',
                                         date_time_columns={'createdAt', 'lastAdvancedAt',
                                                            'lastInteractionAt', 'updatedAt',
                                                            'snoozedUntil', 'archivedAt'})


        # Use candidate details to create stages data frame
        self.stages = create_feature_dataframe(candidate_details, "candidate_id", "stageChanges")
        self.stages = self.stages.applymap(Candidates.convert_time)
        self.stages = correct_date_dtype(self.stages, date_time_format='%Y-%m-%d %H:%M:%S',
                                         date_time_columns={'updatedAt'})

        # Duplicate records by number of postings
        candidate_details = multiply_by_multiselect(candidate_details, "candidate_id", "applications")

        return candidate_details


if __name__ == '__main__':
    start = time()
    # try:
    candis = Candidates(date_limit='1522540800000')
    end = time()
    print (end - start) / 60
    # print candis.candidates
    print candis.candidates.info()
    print candis.stages.info()