__author__ = 'Lothilius'

import pandas as pd
import datetime as dt
import numpy as np

pd.set_option('display.width', 180)
pd.set_option('display.max_columns', None)


def convert_datetime_to_date(the_datetime):
    # print the_datetime
    try:
        still_open_date = dt.datetime.strptime('2000-01-01', '%Y-%m-%d').date()
        if the_datetime == '2000-01-01 00:00:00' or the_datetime == None or the_datetime == np.nan\
                or the_datetime == 'None' or the_datetime == '2000-01-01' \
                or the_datetime == still_open_date:
            return "Still Open"
        elif isinstance(the_datetime, dt.date):
            return the_datetime
        else:
            the_datetime = dt.datetime.strptime(the_datetime, '%Y-%m-%d %H:%M:%S').date()
            return the_datetime
    except ValueError:
        try:
            print the_datetime
            the_datetime = dt.datetime.strptime(the_datetime, '%Y-%m-%d %H:%M').date()
            return the_datetime
        except ValueError:
            try:
                the_datetime = dt.datetime.strptime(the_datetime, '%Y-%m-%d').date()
                return the_datetime
            except ValueError:
                try:
                    the_datetime = dt.datetime.strptime(the_datetime, '%Y-%M-%D').date()
                    return the_datetime
                except ValueError, e:
                    print 'error', e
    except TypeError, e:
        print 'error', e

def main():
    date_of_extract = dt.datetime.strptime('2016-07-31', '%Y-%m-%d').date()
    ticket_list = pd.read_csv('/Users/martin.valenzuela/Box Sync/Documents/Austin Office/HDT/full_full_2016-08-03.csv')#,
                              #error_bad_lines=False, warn_bad_lines=True)
    print ticket_list.columns

    ticket_list.rename(columns={'WORKORDERID': 'RequestID', 'ID': 'RequestID', 'STATUS': 'Request Status',
                                    'Department_Group': 'High-Level Department', 'Completedtime': 'Completed Time',
                                    'CREATEDTIME': 'Created Time', 'COMPLETEDTIME':'Completed Time',
                                    'RESOLUTIONLASTUPDATEDTIME':'Resolved Time'}, inplace=True)

    # cut_off_date = dt.datetime.strptime('2016-07-31', '%Y-%m-%d').date()
    # ticket_list = ticket_list[ticket_list['Created Time'] <= cut_off_date]

    ticket_list['Created Date'] = ticket_list['Created Time'].apply(convert_datetime_to_date)
    print 'break \n'
    # ticket_list['Closed Date'] = ticket_list['Completed Time'].apply(convert_datetime_to_date)
    ticket_list['Resolved Date'] = ticket_list['Resolved Time'].apply(convert_datetime_to_date)

    # Group tickets by created date and resolved date.
    grouped_tickets = ticket_list.groupby(['Created Date', 'Resolved Date'], as_index=False)
    grouped_tickets = pd.DataFrame(grouped_tickets.size(), columns=['Open Tickets'])
    grouped_tickets = grouped_tickets.reset_index()

    print grouped_tickets

    open_list = pd.DataFrame(columns=['Created Date', 'Snap Shot Date', 'Open Tickets'])

    try:
        for each in grouped_tickets.values:
            if each[1] == 'Still Open':
                print "still open %s\n" % each
                cursor = each[0]
                while cursor <= date_of_extract:
                    data = pd.DataFrame(data=[[each[0], cursor, each[2]]],
                                        columns=['Created Date', 'Snap Shot Date', 'Open Tickets'])
                    # print data
                    open_list = open_list.append(data, ignore_index=True)
                    cursor += dt.timedelta(days=1)
                print "Done creating still open %s\n" % cursor
            else:
                cursor = each[0]
                while cursor <= each[1]:
                    data = pd.DataFrame(data=[[each[0], cursor, each[2]]],
                                        columns=['Created Date', 'Snap Shot Date', 'Open Tickets'])
                    # print data
                    open_list = open_list.append(data, ignore_index=True)
                    cursor += dt.timedelta(days=1)
    except TypeError:
        print cursor, each

    print open_list.head()
    now = dt.datetime.now().strftime('%Y-%m-%d')
    open_list.to_csv('/Users/martin.valenzuela/Box Sync/Documents/Austin Office/HDT/back_log_%s.csv' % now, index=False)

if __name__ == '__main__':
    main()