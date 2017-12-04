__author__ = 'Lothilius'

import requests
import json
import sys
import bv_authenticate.Authentication as auth
import datetime
import pandas as pd
import re

pd.set_option('display.width', 160)


class Helpdesk(object):
    """ Extend Status class for Helpdesk.
    """
    def __init__(self):
        self.tickets = self.get_all_tickets()

    def __str__(self):
        return str(self.tickets)

    def count_unassigned(self, helpdesk_tickets):
        """Count total unassigned"""
        unassigned_total = 0
        for each in helpdesk_tickets:
            if each['TECHNICIAN'] == '':
                unassigned_total += 1

        return unassigned_total



def convert_time(unicode_series):
    """Given value for date time
        Convert it to a regular datetime string"""
    # for each in unicode_series:
    if type(unicode_series) == int and len(unicode_series) == 10:
        pass
    elif type(unicode_series) == int and len(unicode_series) == 13:
        unicode_series = unicode_series[:10]
    try:
        date_time_value = datetime.datetime.fromtimestamp(int(unicode_series)).strftime('%Y-%m-%d %H:%M:%S')
        if int(date_time_value[:4]) > 2009:
            return date_time_value
        else:
            return unicode_series
    except:
        return unicode_series

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

def reformat_hd_dataframe(ticket_details):
    ticket_details = ticket_details.rename(columns={'UDF_CHAR1':'Department_Group'})
    ticket_details = ticket_details.applymap(convert_time)
    ticket_details = ticket_details.applymap(reduce_to_year)

    return ticket_details

if __name__ == '__main__':
    status = Helpdesk()
    tickets = pd.DataFrame(status.tickets)
