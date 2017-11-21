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


pd.set_option('display.width', 340)
pd.set_option('display.max_columns', 50)

class Postings(object):
    """ The ticket list class creates an object that gathers individual tickets that belong to a particular list view.
        The list view will need to be specified from the list of view available to the person running the quarry to
        gather the tickets.
    """
    def __init__(self, record_id=''):
        self.last_ticket_id = record_id
        self.postings = self.get_all_postings(record_id)


    def __getitem__(self, item):
        return self.postings[item]

    def __str__(self):
        return str(self.postings)

    def aggregate_postings(self, ticket_list_a, ticket_list_b):
        """ Join to lists of lever records.

        :param ticket_list_a: list
        :param ticket_list_b: list
        :return: list - helpdesk_tickets
        """
        helpdesk_tickets = ticket_list_a + ticket_list_b

        return helpdesk_tickets

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
            # Get first 100 ticket from lever
            lever_records = self.get_100_postings(record_id=record_id)
            # print type(lever_records['data'])
            lever_record_list = lever_records['data']

            # Check if more than 100 exist and need to be aggregated.
            if len(lever_record_list) == 100:
                lever_record_list, lever_records = self.gather_postings(lever_record_list, lever_records)

            try:
                # Convert helpdesk ticket list to Dataframe
                lever_df = pd.DataFrame(lever_record_list)
                lever_df = self.reformat_as_dataframe(lever_df)
                print lever_df

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

    @staticmethod
    def reformat_as_dataframe(requisition_details):
        """ Use to reformat responses to a panda data frame.
        :param requisition_details: Should be in the form of an array of dicts ie [{1,2,...,n},{...}...,{...}]
        :return: returns panda dataframe
        """
        requisition_details = pd.DataFrame(requisition_details)
        requisition_details = requisition_details.applymap(Postings.convert_time)
        # ticket_details = ticket_details.applymap(TicketList.reduce_to_year)
        requisition_details = correct_date_dtype(requisition_details, date_time_format='%Y-%m-%d %H:%M:%S')

        return requisition_details


if __name__ == '__main__':
    start = time()
    # try:
    posts = Postings()
    # except AttributeError as e:
    #     reqs = e.args[0]

    # print type(tickets)
    # print tickets[0]['WORKORDERID']

    # reqs = Postings.reformat_as_dataframe(reqs)
    # reqs.drop('ATTACHMENTS', axis=1, inplace=True)
    end = time()
    print (end - start) / 60
    print type(posts.postings)
    posts.postings.to_csv("/Users/martin.valenzuela/Box Sync/Documents/Austin Office/Tickets/Lever_Testing/postings.csv", encoding='utf-8')
