__author__ = 'Lothilius'

import datetime as dt

import numpy as np
import pandas as pd
from pyprogressbar import Bar

from helper_scripts.notify_helpers import *
from misc_helpers.data_manipulation import correct_date_dtype

pd.set_option('display.width', 280)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 16)


def convert_datetime_to_date(the_datetime):
    # the_datetime = str(the_datetime)
    try:
        still_open_date = dt.datetime.strptime('2000-01-01', '%Y-%m-%d').date()
        if the_datetime == '2000-01-01 00:00:00' or the_datetime is None or the_datetime == np.nan\
                or the_datetime == 'None' or the_datetime == '2000-01-01' \
                or the_datetime == still_open_date or the_datetime == '-':
            return dt.datetime.strptime('2000-01-01', '%Y-%m-%d').date()
        elif isinstance(the_datetime, dt.date):
            return the_datetime
        else:
            the_datetime = dt.datetime.strptime(the_datetime, '%Y-%m-%d %H:%M:%S').date()
            return the_datetime
    except ValueError:
        try:
            # print the_datetime
            the_datetime = dt.datetime.strptime(the_datetime, '%Y-%m-%d %H:%M').date()
            return the_datetime
        except ValueError:
            try:
                the_datetime = dt.datetime.strptime(the_datetime, '%Y-%m-%d').date()
                return the_datetime
            except ValueError:
                try:
                    the_datetime = dt.datetime.strptime(the_datetime, '%Y-%M-%d').date()
                    return the_datetime
                except ValueError, e:
                    print 'error', e
    except TypeError, e:
        print 'error', e

def main():
    # try:
    ticket_list = pd.read_pickle("/Users/martin.valenzuela/Box Sync/Documents/Austin Office/Data/EUS_File__pickle")#,
                              #error_bad_lines=False, warn_bad_lines=True)
    # print ticket_list.columns

    ticket_list.rename(columns={'CREATEDTIME': 'Created Date',
                                'COMPLETEDTIME': 'Completed Date',
                                'RESOLUTIONLASTUPDATEDTIME': 'Resolved Time'}, inplace=True)

    # cut_off_date = dt.datetime.strptime('2014-01-01', '%Y-%m-%d').date()
    stop_date = dt.datetime.strptime('2017-06-20', '%Y-%m-%d').date()

    print ticket_list
    ticket_list.replace(to_replace=['0', 'NA', '-1', '-', 'Not Assigned'], value=np.nan, inplace=True)
    print ticket_list

    ticket_list['Created Dated'] = ticket_list['Created Date'].apply(lambda x: x.date())#dt.datetime.strptime(str(x), '%Y-%m-%d'))
    ticket_list['Completed Date'] = ticket_list['Completed Date'].apply(lambda x: x.date())#dt.datetime.strptime(str(x), '%Y-%m-%d'))
    ticket_list['Resolved Date'] = ticket_list['Resolved Time'].apply(lambda x: x.date())#dt.datetime.strptime(str(x), '%Y-%m-%d'))
    # print ticket_list['CREATEDTIME']
    # ticket_list['Created Dated'] = pd.to_datetime(ticket_list['Created Dated'], format='%Y-%m-%d')
    # print ticket_list
    # ticket_list = ticket_list[ticket_list['Created Date'] >= cut_off_date]

    # ticket_list['Created Dated'] = ticket_list['Created Time'].apply(convert_datetime_to_date)
    # print 'break \n'
    ticket_list['Completed Dated'] = ticket_list['Completed Date'].apply(convert_datetime_to_date)
    ticket_list['Resolved Dated'] = ticket_list['Resolved Date'].apply(convert_datetime_to_date)
    print ticket_list.size
    ticket_list.drop_duplicates(subset=['WORKORDERID', 'Created Date'], keep='last', inplace=True)
    print ticket_list.size


    ticket_list = correct_date_dtype(ticket_list, date_time_format='%Y-%m-%d %H:%M:%S')
    print ticket_list.head(25)

    # Group tickets by created date and resolved date.
    # grouped_tickets = ticket_list.groupby(['Created Dated', 'Completed Dated', 'WORKORDERID', 'GROUP', 'PRIORITY', 'Department_Group'], as_index=False)
    # grouped_tickets = pd.DataFrame(grouped_tickets.size(), columns=['Open Tickets'])
    # grouped_tickets = grouped_tickets.reset_index()
    grouped_tickets = ticket_list[
        ['Created Dated', 'Completed Dated', 'WORKORDERID', 'GROUP', 'PRIORITY', 'Department_Group']].copy()

    print "Yo Goober"
    print grouped_tickets

    open_list = pd.DataFrame(columns=['Created Dated', 'Snap Shot Date', 'Completed Dated', 'WORKORDERID', 'GROUP', 'PRIORITY', 'Department_Group'])
    open_list_columns = open_list.columns.tolist()

    # try:
    pbar = Bar(len(grouped_tickets.values))

    for each in grouped_tickets.values:
        # print each[1], type(each[1])
        # try:
        if each[1] == dt.datetime.strptime('2000-01-01', '%Y-%m-%d').date():
            # print "still open %s\n" % each
            if each[0] < dt.datetime.strptime('2015-05-01', '%Y-%m-%d').date():
                stop_loss = stop_date + dt.timedelta(days=90)
            else:
                stop_loss = stop_date
            cursor = each[0]
            while cursor <= stop_loss:
                data = pd.DataFrame(data=[[each[0], cursor, each[1], each[2], each[3], each[4], each[5]]],
                                    columns=open_list_columns)
                # print data
                open_list = open_list.append(data, ignore_index=True)
                cursor += dt.timedelta(days=1)
            # print "Done creating still open %s\n" % cursor
        else:
            cursor = each[0]
            while cursor <= each[1]:
                data = pd.DataFrame(data=[[each[0], cursor, each[1], each[2], each[3], each[4], each[5]]],
                                    columns=open_list_columns)
                # print data
                data.drop
                open_list = open_list.append(data, ignore_index=True)
                cursor += dt.timedelta(days=1)
        # except:
        #     error_result = "Unexpected error 1TL: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
        #     print error_result
        pbar.passed()
    # except TypeError:
    #     print cursor, each
    # except:
    #     error_result = "Unexpected error 1TL: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
    #     print error_result


    # print open_list.head()
    now = dt.datetime.now().strftime('%Y-%m-%d_%H_%M')
    open_list.to_csv('/Users/martin.valenzuela/Box Sync/Documents/Austin Office/Tickets/EUS_Tableau_report_request_30465/back_log_%s.csv' % now, index=False)
    alert_the_light()
    alert_homer()

if __name__ == '__main__':
    main()