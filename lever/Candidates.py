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
from time import time
from se_helpers.actions import wait

pd.set_option('display.width', 290)
pd.set_option('display.max_columns', 50)
pd.set_option('display.max_colwidth', 250)


class Candidates(object):
    """ The ticket list class creates an object that gathers individual tickets that belong to a particular list view.
        The list view will need to be specified from the list of view available to the person running the quarry to
        gather the tickets.
    """

    def __init__(self, record_id=''):
        self.stages = pd.DataFrame()
        self.last_candidate_id = record_id
        self.candidates = self.get_all_candidates(record_id)

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

    def get_100_postings(self, offset='', record_id=''):
        """ Get lever records up to 100 at a time.
        :return: dict with lever requisition info {data, hasNext[, next]}
        """
        url, querystring, headers = lhc.create_api_request(object='candidates', offset=offset, record_id=record_id)

        return lhc.fetch_from_lever(url, querystring, headers)

    def gather_candidates(self, lever_record_list, lever_records):
        try:
            self.record_cursor = lever_records['next']
            lever_records = self.get_100_postings(offset=self.record_cursor)
            lever_record_list = self.aggregate_candidates(lever_record_list, lever_records['data'])

            lever_record_list, lever_records = self.gather_candidates(lever_record_list, lever_records)
        except KeyError:
            pass

        return lever_record_list, lever_records

    def get_all_candidates(self, record_id=''):
        try:
            # Get first 100 ticket from lever
            lever_records = self.get_100_postings(record_id=record_id)
            # print type(lever_records['data'])
            lever_record_list = lever_records['data']

            # Check if more than 100 exist and need to be aggregated.
            if len(lever_record_list) == 100:
                lever_record_list, lever_records = self.gather_candidates(lever_record_list, lever_records)

            try:
                # lever_record_list = self.flaten_dictionary(lever_record_list)
                # Convert helpdesk ticket list to Dataframe
                lever_df = pd.DataFrame(lever_record_list)
                print '------ here goober --------'
                # print lever_df
                lever_df = self.reformat_as_dataframe(lever_record_list)
                # print lever_df

            except EOFError:
                error_result = "Unexpected error 1TL: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
                print error_result
                # raise Exception(error_result)

            return lever_df
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

    def reformat_as_dataframe(self, candidate_details):
        """ Use to reformat responses to a panda data frame.
        :param candidate_details: Should be in the form of an array of dicts ie [{1,2,...,n},{...}...,{...}]
        :return: returns panda dataframe
        """
        candidate_details = pd.DataFrame(candidate_details)
        candidate_details = candidate_details.applymap(Candidates.convert_time)

        candidate_details = correct_date_dtype(candidate_details, date_time_format='%Y-%m-%d %H:%M:%S')
        self.create_stages_dataframe(candidate_details, "id", "stageChanges")

        # Duplicate records by number of postings
        candidate_details = multiply_by_multiselect(candidate_details, "id", "applications")

        return candidate_details

    def create_stages_dataframe(self, df, id_column, feature_column):
        """ Create a dataframe of the stages time line

        :param df:
        :param id_column:
        :param feature_column:
        :return:
        """
        # Create Copy of dataframe for changes
        stages = df[[feature_column, id_column]].copy(deep=True)
        # Convert Dict elements in to daraframes and
        stages.apply(lambda row: self.gather_ided_lists(row[id_column], row[feature_column], id_column), axis=1)

        stages_ready = stages.applymap(Candidates.convert_time)
        stages_ready = correct_date_dtype(stages_ready, date_time_format='%Y-%m-%d %H:%M:%S')


        return stages_ready

    def gather_ided_lists(self, id_value, dict_column_values, id_column):
        df_feature_values = pd.DataFrame(dict_column_values)
        df_feature_values[id_column] = id_value

        self.stages = pd.concat([self.stages, df_feature_values])

        return dict_column_values

    @staticmethod
    def flaten_dictionary(results_od):
        """ Create a flat dictionary that can be converted in to a Pandas Dataframe.
        :param results_od: Dict
        :return: a flattened dictionary of the reasults_od data
        """

        # Gather all keys present
        data = {}
        keys = results_od[0][0].keys()
        for row in results_od:
            for thing in row:
                for key in thing.keys():
                    if key not in keys:
                        keys.append(key)

        # Using all gethered keys create columns of keys)
        for each in results_od:
            # wait(15)
            for thing in each:
                for key in keys:
                    try:
                        if isinstance(thing[key], dict):
                            data.setdefault(key, []).append(thing[key])
                        else:
                            data.setdefault(key, []).append(thing[key])
                    except KeyError:
                        data.setdefault(key, []).append(None)
        flat_df = pd.DataFrame.from_dict(data)
        # print flat_df

        return flat_df


if __name__ == '__main__':
    start = time()
    # try:
    candis = Candidates()
    print candis.stages
    end = time()
    print (end - start) / 60
    # print candis.candidates

    # candis.candidates.to_csv(
    #     "/Users/martin.valenzuela/Box Sync/Documents/Austin Office/Tickets/Lever_Testing/postings.csv",
    #     encoding='utf-8',
    #     escapechar='\\',
    #     index=False)
