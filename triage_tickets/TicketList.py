__author__ = 'Lothilius'
# coding: utf-8

import datetime
import re
import sys

import pandas as pd
from pyprogressbar import Bar

from HelpdeskConnection import HelpdeskConnection as hdc
from HelpdeskConnectionV3 import HelpdeskConnection as hdc3
from Ticket import Ticket
from helper_scripts.misc_helpers.data_manipulation import correct_date_dtype
from time import time
import numpy as np


pd.set_option('display.width', 340)
pd.set_option('display.max_columns', 50)

class TicketList(object):
    """ The ticket list class creates an object that gathers individual tickets that belong to a particular list view.
        The list view will need to be specified from the list of view available to the person running the quarry to
        gather the tickets.
    """
    def __init__(self, helpdesk_que='Triage', with_resolution=False, with_conversations=False,
                 with_detail=True, last_id=0, version=1, query='', count_only=False):
        self.ticket_cursor = 1
        self.total_count = 0
        self.last_ticket_id = last_id
        self.with_resolution = with_resolution
        self.with_conversations = with_conversations
        self.version = version
        self.query = query
        self.count_only = count_only
        if version == 3:
            self.tickets = list(self.get_all_tickets(with_detail=False))
        else:
            view_id = self.get_view_id(helpdesk_que)
            self.tickets = list(self.get_all_tickets(view_id, with_detail))


    def __getitem__(self, item):
        return self.tickets[item]

    def __str__(self):
        return str(self.tickets)

    @staticmethod
    def get_filter_list():
        """ Retrieve list request filters available.
        :return: Dictionary of the ticket details
        """
        url, querystring, headers = hdc.create_api_request()

        url = url + "/filters"

        querystring['OPERATION_NAME'] = "GET_REQUEST_FILTERS"
        del querystring['INPUT_DATA']
        # print querystring
        filter_list = hdc.fetch_from_helpdesk(url, querystring, headers)

        return filter_list

    @staticmethod
    def get_view_id(view_name=''):
        try:
            # Get the view ID for the pending view HD
            filters = pd.DataFrame(TicketList.get_filter_list())
            view__id = filters[filters.VIEWNAME == view_name].VIEWID.iloc[0]
            return view__id
        except ValueError, e:
            print e
            view_name = raw_input('Please enter valid view name: ')
            TicketList.get_view_id(view_name)
        except:
            error_result = "Unexpected error 1TL: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
            print error_result

    def aggregate_tickets(self, ticket_list_a, ticket_list_b):
        """ Join to lists of helpdesk tickets.

        :param ticket_list_a: list
        :param ticket_list_b: list
        :return: list - helpdesk_tickets
        """
        helpdesk_tickets = ticket_list_a + ticket_list_b

        return helpdesk_tickets

    def get_100_tickets(self, helpdesk_que='7256000001531681_MyView_7256000001531679', from_value=1): # 7256000001531681_MyView_7256000001531679 7256000001516015_MyView_7256000000736233
        """ Get helpdesk tickets for the respective query 100 at a time.
        :return: list of dicts - helpdesk_tickets
        """
        if self.version == 3:
            url, querystring, headers = hdc3.create_api_request(from_value, query=self.query)
            helpdesk_tickets, ticket_info = hdc3.fetch_from_helpdesk(url, querystring, headers)
            self.total_count = ticket_info['total_count']
            return helpdesk_tickets
        else:
            url, querystring, headers = hdc.create_api_request(helpdesk_que, from_value)
            return hdc.fetch_from_helpdesk(url, querystring, headers)



    def get_all_tickets(self, helpdesk_que='7256000001531681_MyView_7256000001531679', with_detail=True):
        try:
            # Get first 100 ticket from helpdesk
            helpdesk_tickets = self.get_100_tickets(helpdesk_que=helpdesk_que)
            if self.total_count > 0 and self.total_count > 100:
                print "Retrieving list of Tickets: \n"
                pbar = Bar(self.total_count / 100)

            # Check if more than 100 exist and need to be aggregated.
            if len(helpdesk_tickets) == 100 and not self.count_only:

                # TODO - Make this a recursive method!!!
                while len(helpdesk_tickets) % 100 == 0:
                    self.ticket_cursor = self.ticket_cursor + 100
                    helpdesk_tickets = self.aggregate_tickets(
                        helpdesk_tickets, self.get_100_tickets(helpdesk_que=helpdesk_que,
                                                               from_value=self.ticket_cursor))
                    if self.total_count != 0:
                        pbar.passed()

            if with_detail and self.version != 3:
                ticket_details = []
                try:
                    # Convert helpdesk ticket list to Dataframe
                    helpdesk_df = pd.DataFrame(helpdesk_tickets)
                    helpdesk_df['WORKORDERID'] = pd.to_numeric(helpdesk_df['WORKORDERID'], errors='coerce')

                    # Reduce ticket list to only tickets greater than the last ticket id
                    # Note: If now last ticket ID is given the last ticket ID is 0 and so all ticket detail is retrieved.
                    detail_list = helpdesk_df[helpdesk_df['WORKORDERID'] > self.last_ticket_id]
                    if self.last_ticket_id != 0:
                        print 'Retrieving ticket detail from Work order ID: %s' % self.last_ticket_id
                    else:
                        print 'Retrieving ticket detail.'

                    # Gather Ticket details for each in the summery dataframe
                    pbar = Bar(len(detail_list['WORKORDERID'].tolist()))
                    for i, each in enumerate(detail_list['WORKORDERID'].tolist()):
                        # print i
                        ticket = Ticket(str(each), self.with_resolution, self.with_conversations)
                        ticket_details.append(ticket.details)
                        pbar.passed()

                except:
                    error_result = "Unexpected error 1TL: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
                    print error_result
                    raise Exception(error_result)

                return ticket_details
            else:
                helpdesk_tickets
                return helpdesk_tickets
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
    def reformat_as_dataframe(ticket_details):
        """ Use to reformat responses to a panda data frame.
        :param ticket_details: Should be in the form of an array of dicts ie [{1,2,...,n},{...}...,{...}]
        :return: returns panda dataframe
        """
        version = ticket_details.version
        ticket_details = pd.DataFrame(list(ticket_details))
        if version == 3:
            ticket_details = TicketList.version3_reformat_helper(ticket_details)
        ticket_details = ticket_details.rename(columns={'UDF_CHAR1': 'Department_Group',
                                                        'UDF_CHAR2': 'System',
                                                        'UDF_CHAR11': 'System Component'})
        ticket_details = ticket_details.applymap(TicketList.convert_time)
        # ticket_details = ticket_details.applymap(TicketList.reduce_to_year)
        ticket_details = correct_date_dtype(ticket_details, date_time_format='%Y-%m-%d %H:%M:%S')

        return ticket_details

    @staticmethod
    def version3_reformat_helper(ticket_details):
        """Convert the base data frame to the expected data frame"""
        # Replace None values with
        ticket_details.replace(to_replace={None: np.nan}, inplace=True)

        # Split columns that have sub-columns in the form of a dict with lists
        column_replacements = {'udf_fields': ['udf_char1', 'udf_char2', 'udf_char11'], 'mode': ['name'],
                               'template': ['name'], 'requester': ['email_id', 'name'], 'technician': ['name'],
                               'status': ['name'], 'sla': ['name'], 'site': ['name'],
                               'responded_time': ['value'], 'priority': ['name'],
                               'group': ['name'], 'first_response_due_by_time': ['value'], 'due_by_time': ['value'],
                               'department': ['name'], 'created_time': ['value'], 'created_by': ['value'],
                               'completed_time': ['value'], 'category': ['name'], 'resolved_time': ['value'],
                               'item': ['name'], 'level': ['name'], 'subcategory': ['name']}

        for column in column_replacements.keys():
            for subcolumn in column_replacements[column]:
                if subcolumn in ['name', 'value']:
                    ticket_details[column] = ticket_details[column].apply(
                        lambda x: TicketList.version3_null_filler(x, subcolumn))
                else:
                    ticket_details[subcolumn] = ticket_details[column].apply(
                        lambda x: TicketList.version3_null_filler(x, subcolumn))

        # Remove the field containing custom fields and approval status
        ticket_details.drop(columns=['udf_fields', 'approval_status', 'first_response_due_by_time'], inplace=True)

        # Add missing columns that are supposed to come through v3
        if 'resolution' not in ticket_details.columns.tolist():
            ticket_details['resolution'] = np.nan
        if 'item' not in ticket_details.columns.tolist():
            ticket_details['item'] = np.nan
        if 'level' not in ticket_details.columns.tolist():
            ticket_details['level'] = np.nan
        if 'subcategory' not in ticket_details.columns.tolist():
            ticket_details['subcategory'] = np.nan

        # Rename columns to v1 naming schema
        ticket_details = ticket_details.rename(columns={'created_by': 'CREATEDBY', 'created_time': 'CREATEDTIME',
                                                        'description': 'SHORTDESCRIPTION', 'display_id': 'WORKORDERID',
                                                        'due_by_time': 'DUEBYTIME', 'group': 'GROUP',
                                                        'has_attachments': 'HASATTACHMENTS',
                                                        'id': 'LONG_REQUESTID', 'attachments': 'ATTACHMENTS',
                                                        'category': 'CATEGORY', 'completed_time': 'COMPLETEDTIME',
                                                        'deleted_on': 'DELETED_TIME', 'department': 'DEPARTMENT',
                                                        'has_notes': 'HASNOTES', 'mode': 'MODE', 'priority': 'PRIORITY',
                                                        'requester': 'REQUESTER', 'level': 'LEVEL', 'item': 'ITEM',
                                                        'responded_time': 'RESPONDEDTIME', 'email_id': 'REQUESTEREMAIL',
                                                        'site': 'SITE', 'sla': 'SLA',
                                                        'status': 'STATUS', 'technician': 'TECHNICIAN',
                                                        'template': 'TEMPLATEID', 'time_elapsed ': 'TIMESPENTONREQ',
                                                        'udf_char1': 'UDF_CHAR1', 'udf_char2': 'UDF_CHAR2',
                                                        'resolved_time': 'RESOLUTIONLASTUPDATEDTIME',
                                                        'subject': 'SUBJECT', 'resolution': 'RESOLUTION',
                                                        'subcategory': 'SUBCATEGORY', 'udf_char11': 'UDF_CHAR11'})

        missing_columns = ['DELETED_TIME', 'HASCONVERSATION', 'ISPENDING', 'REQUESTTEMPLATE',
                           'STOPTIMER', 'TIMESPENTONREQ', 'RESOLVER']
        ticket_details = ticket_details.assign(**dict.fromkeys(missing_columns, np.nan))

        return ticket_details

    @staticmethod
    def version3_null_filler(record, column):
        try:
            value = record[column]
        except KeyError:
            value = np.nan
        except TypeError:
            value = np.nan
        return value

if __name__ == '__main__':
    start = time()
    try:
        test_tickets = TicketList(version=3, query=["BizApps - Technical"], count_only=False)
    except AttributeError as e:
        tickets = e.args[0]

    # print type(tickets)
    # print tickets[0]['WORKORDERID']

    test_tickets = TicketList.reformat_as_dataframe(test_tickets)
    # tickets.drop('ATTACHMENTS', axis=1, inplace=True)
    end = time()
    print (end - start) / 60
    print test_tickets
