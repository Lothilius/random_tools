__author__ = 'Lothilius'

import pandas as pd
import datetime as dt
from sfdc.SFDC import SFDC

pd.set_option('display.width', 200)


def convert_datetime_to_date(the_datetime):
    # print the_datetime
    if the_datetime is not None:
        the_datetime = the_datetime.split('T')
        the_datetime = dt.datetime.strptime(the_datetime[0], '%Y-%m-%d').date()
        return the_datetime
    else:
        return "Still Open"


def get_sfdc_data(environment='prod'):
    """
    """
    sf = SFDC.connect_to_SFDC(environment)
    build_query = "Select Id, Status, CreatedDate, Department_Requesting__c, Project__c, Release_Date__c, ClosedDate, " \
                  "Sub_Status__c FROM Case WHERE RecordTypeId = '01250000000Hnex' AND Project__c = 'a8B50000000Kyq8'"
    result = sf.query_all(build_query)

    return result

ticket_list = get_sfdc_data()

ticket_list = pd.DataFrame(ticket_list['records'])


ticket_list['Created Date'] = ticket_list['CreatedDate'].apply(convert_datetime_to_date)
ticket_list['Closed Date'] = ticket_list['ClosedDate'].apply(convert_datetime_to_date)

ticket_list.drop(['attributes'], axis=1, inplace=True)

# print ticket_list

# Group Cases by created date and resolved date.
grouped_tickets = ticket_list.groupby(['Created Date', 'Closed Date', 'Department_Requesting__c'], as_index=False)
grouped_tickets = pd.DataFrame(grouped_tickets.size(), columns=['Open Cases'])
grouped_tickets = grouped_tickets.reset_index()

print grouped_tickets

open_list = pd.DataFrame(columns=['Created Date', 'Snap Shot Date', 'Department_Requesting__c', 'Open Cases'])

for each in grouped_tickets.values:
    if each[1] == 'Still Open':
        cursor = each[0]
        while cursor <= dt.date.today():
            data = pd.DataFrame(data=[[each[0], cursor, each[2], each[3]]],
                                columns=['Created Date', 'Snap Shot Date', 'Department_Requesting__c', 'Open Cases'])
            # print data
            open_list = open_list.append(data, ignore_index=True)
            cursor += dt.timedelta(days=1)
    else:
        cursor = each[0]
        while cursor <= each[1]:
            data = pd.DataFrame(data=[[each[0], cursor, each[2], each[3]]],
                                columns=['Created Date', 'Snap Shot Date', 'Department_Requesting__c', 'Open Cases'])
            # print data
            open_list = open_list.append(data, ignore_index=True)
            cursor += dt.timedelta(days=1)

print open_list.head(25)
open_list.to_csv('/Users/martin.valenzuela/Box Sync/Documents/Austin Office/HDT/sfdc_back_log.csv', index=False)