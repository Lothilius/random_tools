__author__ = 'Lothilius'

from Ticket import Ticket
from HelpdeskConnection import HelpdeskConnection as hdc
import pandas as pd
import re
import datetime
import sys

pd.set_option('display.width', 160)

class TicketList(object):
    def __init__(self, helpdesk_que='7256000001531681_MyView_7256000001531679'):
        self.tickets = list(self.get_all_tickets(helpdesk_que))

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

    def aggregate_tickets(self, ticket_list_a, ticket_list_b):
        """ Join to lists of helpdesk tickets.

        :param ticket_list_a: list
        :param ticket_list_b: list
        :return: list - helpdesk_tickets
        """
        helpdesk_tickets = ticket_list_a + ticket_list_b

        return helpdesk_tickets

    def get_100_tickets(self, helpdesk_que='7256000001531681_MyView_7256000001531679', from_value=1): # 7256000001531681_MyView_7256000001531679 7256000001516015_MyView_7256000000736233
        """ Get helpdesk tickets for the respective que 100 at a time.
        :return: list of dicts - helpdesk_tickets
        """
        url, querystring, headers = hdc.create_api_request(helpdesk_que, from_value)

        return hdc.fetch_from_helpdesk(url, querystring, headers)

    def get_all_tickets(self, helpdesk_que='7256000001531681_MyView_7256000001531679'):
        try:
            from_value = 1
            # Get first 100 ticket from helpdesk
            helpdesk_tickets = self.get_100_tickets(helpdesk_que=helpdesk_que)

            # Check if more than 100 exist and need to be aggregated.
            if len(helpdesk_tickets) == 100:
                # TODO - Make this a recursive method!!!
                while len(helpdesk_tickets) % 100 == 0:
                    from_value = from_value + 100
                    helpdesk_tickets = self.aggregate_tickets(
                        helpdesk_tickets, self.get_100_tickets(from_value=from_value))

            ticket_details = []
            for each in helpdesk_tickets:
                ticket = Ticket(each['WORKORDERID'])
                ticket_details.append(ticket.details)

            return ticket_details
        except:
            error_result = "Unexpected error 1: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
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
                return unicode_series[:10]
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
        ticket_details = pd.DataFrame(list(ticket_details))
        ticket_details = ticket_details.rename(columns={'UDF_CHAR1': 'Department_Group', 'UDF_CHAR2': 'System'})
        ticket_details = ticket_details.applymap(TicketList.convert_time)
        ticket_details = ticket_details.applymap(TicketList.reduce_to_year)

        return ticket_details


if __name__ == '__main__':
    tickets = TicketList()
    filters = pd.DataFrame(tickets.get_filter_list())
    print filters[filters.VIEWNAME == 'Holding Pool - Pending Assignment'].VIEWID.iloc[0]
