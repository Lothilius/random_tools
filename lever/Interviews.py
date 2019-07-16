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
import collections



pd.set_option('display.width', 283)
pd.set_option('display.max_columns', 50)
pd.set_option('display.max_colwidth', 250)


class Interviews(object):
    """ The ticket list class creates an object that gathers individual tickets that belong to a particular list view.
        The list view will need to be specified from the list of view available to the person running the quarry to
        gather the tickets.
    """
    def __init__(self, record_id='', candidate_id=''):
        self.candidate_id = candidate_id
        self.last_interview_id = record_id
        self.inteview = self.get_all_interviews(record_id)


    def __getitem__(self, item):
        return self.inteview[item]

    def __str__(self):
        return str(self.inteview)

    def aggregate_interviews(self, interview_list_a, interview_list_b):
        """ Join to lists of lever records.

        :param interview_list_a: list
        :param interview_list_b: list
        :return: list - interview_list
        """
        interview_list = interview_list_a + interview_list_b

        return interview_list

    def get_100_interviews(self, offset='', record_id=''):
        """ Get lever records up to 100 at a time.
        :return: dict with lever requisition info {data, hasNext[, next]}
        """
        url, querystring, headers = lhc.create_api_request(object='interview', offset=offset, record_id=record_id)

        return lhc.fetch_from_lever(url, querystring, headers)


    def gather_interviews(self, lever_record_list, lever_records):
        try:
            self.record_cursor = lever_records['next']
            lever_records = self.get_100_interviews(offset=self.record_cursor)
            lever_record_list = self.aggregate_interviews(lever_record_list, lever_records['data'])

            lever_record_list, lever_records = self.gather_interviews(lever_record_list, lever_records)
        except KeyError:
            pass

        return lever_record_list, lever_records


    def get_all_interviews(self, record_id=''):
        try:
            # Get first 100 ticket from lever
            lever_records = self.get_100_interviews(record_id=record_id)
            # print type(lever_records['data'])
            lever_record_list = lever_records['data']

            # Check if more than 100 exist and need to be aggregated.
            if len(lever_record_list) == 100:
                lever_record_list, lever_records = self.gather_interviews(lever_record_list, lever_records)

            try:
                lever_record_list = self.flaten_dictionary(lever_record_list)
                # Convert helpdesk ticket list to Dataframe
                lever_df = pd.DataFrame(lever_record_list)
                print '------ here goober --------'
                print lever_df
                lever_df = self.reformat_as_dataframe(lever_df)
                # print lever_df

            except:
                error_result = "Unexpected error 1TL: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
                print error_result
                raise Exception(error_result + str(lever_df))

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

    def reformat_as_dataframe(self, requisition_details):
        """ Use to reformat responses to a panda data frame.
        :param requisition_details: Should be in the form of an array of dicts ie [{1,2,...,n},{...}...,{...}]
        :return: returns panda dataframe
        """
        requisition_details = pd.DataFrame(requisition_details)
        # print requisition_details
        requisition_details = requisition_details.applymap(Interviews.convert_time)

        # ticket_details = ticket_details.applymap(TicketList.reduce_to_year)
        requisition_details = correct_date_dtype(requisition_details, date_time_format='%Y-%m-%d %H:%M:%S')
        # requisition_details.drop(labels=['content'], axis=1, inplace=True)

        # Duplicate records by number of postings
        requisition_details = multiply_by_multiselect(requisition_details, "id", "applications")

        return requisition_details

    @staticmethod
    def flaten_dictionary(results_od):
        """ Create a flat dictionary that can be converted in to a Pandas Dataframe.
        :param results_od: Dict
        :return: a flattened dictionary of the reasults_od data
        """
        data = {}
        for each in results_od:
            for k, v in each.items():
                # print type(k), v
                if type(v) == collections.OrderedDict:
                    for l, m in v.items():
                        data.setdefault(l, []).append(m)
                else:
                    data.setdefault(k, []).append(v)
        flat_df = pd.DataFrame.from_dict(data)
        print data

        return flat_df

if __name__ == '__main__':
    start = time()
    # try:
    candis = Interviews()

    end = time()
    print (end - start) / 60
    # print candis.candidates
