__author__ = 'Lothilius'

import datetime as dt
import pandas as pd
from pyprogressbar import Bar
from helper_scripts.misc_helpers.data_manipulation import correct_date_dtype
from helper_scripts.notify_helpers import *
from time import time

pd.set_option('display.width', 280)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 16)


def create_history(data_row, cursor, open_list_columns):
    """ Given the row of data for the history and the cursor create a row for each date up to the cursor date

    :param data_row: list of data
    :param cursor: date.
    :return: dataframe
    """
    open_list = pd.DataFrame(
        columns=open_list_columns)

    if data_row[1] == dt.datetime.strptime('2000-01-01', '%Y-%m-%d'):
        while cursor <= dt.datetime.strptime('2017-01-31', '%Y-%m-%d'):
            data = pd.DataFrame(data=[[data_row[0], cursor, data_row[1], data_row[2], data_row[3], data_row[4]]], columns=open_list_columns)# data_row[3], data_row[4], data_row[5], data_row[6]]], columns=open_list_columns)
            # print data
            open_list = open_list.append(data, ignore_index=True)
            cursor += dt.timedelta(days=1)
    else:
        while cursor <= data_row[1]:
            data = pd.DataFrame(data=[[data_row[0], cursor, data_row[1], data_row[2], data_row[3], data_row[4]]], columns=open_list_columns)# data_row[3], data_row[4], data_row[5], data_row[6]]], columns=open_list_columns)
            # print data
            open_list = open_list.append(data, ignore_index=True)
            cursor += dt.timedelta(days=1)

    return open_list


def main():
    # try:
    employee_list = pd.read_csv('/Users/martin.valenzuela/Box Sync/'
                                 'Documents/Austin Office/Data/History_Active_Employees_1-31-17.csv',
    error_bad_lines=False, warn_bad_lines=True)

    cut_off_date = dt.datetime.strptime('2017-01-31', '%Y-%m-%d')
    stop_date = dt.datetime.strptime('2017-01-31', '%Y-%m-%d')
    date_time_columns = ['DOT', 'DOH']
    employee_list = correct_date_dtype(employee_list, date_time_format='%Y-%m-%d', date_time_columns=date_time_columns)
    print employee_list['DOT'].iloc[19]


    # employee_list.replace(to_replace=['0', 'NA', '-1', '-', 'Not Assigned'], value=np.nan, inplace=True)
    # print employee_list

    historical_list = pd.DataFrame(columns=['DOH', 'Snap Shot Date', 'DOT', 'EEID', 'WorkerType', 'EEType'])
    open_list_columns = historical_list.columns.tolist()

    pbar = Bar(len(employee_list.values))

    for each in employee_list[['DOH', 'DOT', 'EEID', 'WorkerType', 'EEType']].values:
        try:
            # print each
            cursor = each[0]
            historical_list = historical_list.append(create_history(each, cursor, open_list_columns), ignore_index=True)
        except:
            error_result = "Unexpected error 1G: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
            print error_result, " ", open_list_columns
        # print historical_list
        pbar.passed()


    print historical_list.head()
    now = dt.datetime.now().strftime('%Y-%m-%d_%H_%M')
    historical_list.to_csv('/Users/martin.valenzuela/Box Sync/Documents/employee_history_%s.csv' % now, index=False)
    alert_the_light()
    alert_homer()

if __name__ == '__main__':
    start = time()
    main()
    end = time()
    print (end - start) / 60