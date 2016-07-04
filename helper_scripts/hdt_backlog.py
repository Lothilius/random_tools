__author__ = 'Lothilius'

import pandas as pd
import datetime as dt

pd.set_option('display.width', 200)


def convert_datetime_to_date(the_datetime):
    # print the_datetime
    try:
        the_datetime = dt.datetime.strptime(the_datetime, '%m/%d/%y %H:%M').date()
        return the_datetime
    except ValueError:
        return "Still Open"


ticket_list = pd.read_csv('/Users/martin.valenzuela/Box Sync/Documents/Austin\ Office/HDT/BizApps_Demand_FY16.csv')

ticket_list['Created Date'] = ticket_list['Created Time'].apply(convert_datetime_to_date)
ticket_list['Resolved Date'] = ticket_list['Resolved Time'].apply(convert_datetime_to_date)

# Group tickets by created date and resolved date.
grouped_tickets = ticket_list.groupby(['Created Date', 'Closed Date'], as_index=False)
grouped_tickets = pd.DataFrame(grouped_tickets.size(), columns=['Open Tickets'])
grouped_tickets = grouped_tickets.reset_index()

print grouped_tickets

open_list = pd.DataFrame(columns=['Created Date', 'Snap Shot Date', 'Open Tickets'])

for each in grouped_tickets.values:
    if each[1] == 'Still Open':
        cursor = each[0]
        while cursor <= dt.date.today():
            data = pd.DataFrame(data=[[each[0], cursor, each[2]]],
                                columns=['Created Date', 'Snap Shot Date', 'Open Tickets'])
            # print data
            open_list = open_list.append(data, ignore_index=True)
            cursor += dt.timedelta(days=1)
    else:
        cursor = each[0]
        while cursor <= each[1]:
            data = pd.DataFrame(data=[[each[0], cursor, each[2]]],
                                columns=['Created Date', 'Snap Shot Date', 'Open Tickets'])
            # print data
            open_list = open_list.append(data, ignore_index=True)
            cursor += dt.timedelta(days=1)

print open_list.head()
# open_list.to_csv('/Users/martin.valenzuela/Box Sync/Documents/Austin Office/HDT/back_log.csv', index=False)