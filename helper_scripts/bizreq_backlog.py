__author__ = 'Lothilius'

import pandas as pd
import datetime as dt
from sfdc.SFDC import SFDC
from pyprogressbar import Bar
from helper_scripts.notify_helpers import *
from os import environ
from tableau_data_publisher.data_assembler_hyper import HyperAssembler
from tableau_data_publisher.Tableau import Tableau
from tableau_data_publisher.data_publisher import publish_data



pd.set_option('display.width', 290)

if environ['MY_ENVIRONMENT'] == 'prod':
    file_path = '/var/shared_folder/EUS/Tableau_data/'
    project = 'Business Applications'
else:
    file_path = '/Users/%s/Downloads/' % environ['USER']
    project = 'Testing'

extract_name = 'BizApps_BizReqs'

def convert_datetime_to_date(the_datetime):
    # print the_datetime
    if the_datetime is not None:
        the_datetime = the_datetime.split('T')
        the_datetime = dt.datetime.strptime(the_datetime[0], '%Y-%m-%d').date()
        return the_datetime
    else:
        return dt.datetime.strptime('2000-01-01', '%Y-%m-%d').date()


def get_sfdc_data(environment='prod'):
    """
    """
    sf = SFDC.connect_to_SFDC(environment)
    build_query = "Select Id, Status, CreatedDate, Department_Requesting__c, Project__c, Release_Date__c, ClosedDate, " \
                  "Sub_Status__c, Priority, (select OldValue, NewValue, CreatedDate from Histories) FROM Case WHERE RecordTypeId = '01250000000Hnex' " \
                  "AND (Project__c = 'a8B50000000Kyq8' OR Project__c = 'a8B50000000Kyqr') " \
                  "AND (Status = 'Approved Backlog' OR Status = 'Prioritized' )"
    result = sf.query_all(build_query)

    return result


def check_if_null(series):
    """ Check a series and return a series with the null date value or return the series
    :param series: panda series
    :return: a panda series
    """
    if series.empty:
        return pd.Series(data=['2000-01-01T00:00:00.000Z'])
    else:
        return series


def get_history(data_frame_element):
    """ Parse the data frame from the field update history and gather dates for inprogress and copleted.
    :param dataframe_element:
    :return:
    """
    try:
        df = pd.DataFrame(data_frame_element['records'])
        in_progress = check_if_null(df[df['NewValue'] == 'In Progress']['CreatedDate'])
        completed = check_if_null(df[df['NewValue'] == 'Completed']['CreatedDate'])
        return in_progress.iloc[0], completed.iloc[-1]
    except:
        error_result = "Unexpected error 1gh: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
        print error_result

        # for each in data_frame_element['records']:
        #     if each['NewValue'] == 'In Progress':
        #         return each['CreatedDate']


def create_history(data_row, cursor, open_list_columns):
    """ Given the row of data for the history and the cursor create a row for each date up to the cursor date

    :param data_row: list of data
    :param cursor: date.
    :return: dataframe
    """
    open_list = pd.DataFrame(
        columns=open_list_columns)

    if data_row[1] == dt.datetime.strptime('2000-01-01', '%Y-%m-%d').date():
        while cursor <= dt.date.today():
            data = pd.DataFrame(data=[[data_row[0], cursor, data_row[2], data_row[3], data_row[4], data_row[5], data_row[6], data_row[7], data_row[8]]], columns=open_list_columns)# data_row[3], data_row[4], data_row[5], data_row[6]]], columns=open_list_columns)
            # print data
            open_list = open_list.append(data, ignore_index=True)
            cursor += dt.timedelta(days=1)
    else:
        while cursor <= data_row[1]:
            data = pd.DataFrame(data=[[data_row[0], cursor, data_row[2], data_row[3], data_row[4], data_row[5], data_row[6], data_row[7], data_row[8]]], columns=open_list_columns)# data_row[3], data_row[4], data_row[5], data_row[6]]], columns=open_list_columns)
            # print data
            open_list = open_list.append(data, ignore_index=True)
            cursor += dt.timedelta(days=1)

    return open_list


def determine_true_closed_date(row):
    if row[0] == dt.datetime.strptime('2000-01-01', '%Y-%m-%d').date():
        return row[1]
    else:
        return row[0]

def main():
    try:
        ticket_list = get_sfdc_data()
        # print ticket_list['records'][0]['Histories']['records']

        ticket_list = pd.DataFrame(ticket_list['records'])
        ticket_list[['InProgress Date', 'CompletedDate']] = ticket_list['Histories'].map(get_history).apply(pd.Series)


        # Change date columns in to proper date columns
        ticket_list['Created Date'] = ticket_list['CreatedDate'].apply(convert_datetime_to_date)
        ticket_list['In Progress Date'] = ticket_list['InProgress Date'].apply(convert_datetime_to_date)
        ticket_list['Completed Date'] = ticket_list['CompletedDate'].apply(convert_datetime_to_date)
        ticket_list['Closed Date'] = ticket_list['ClosedDate'].apply(convert_datetime_to_date)

        # Compare the start column and the completed date column to determine the date to use.
        ticket_list['True Start Date'] = ticket_list[['In Progress Date', 'Created Date']]\
            .apply(determine_true_closed_date, axis=1)

        # Compare the completed column and the completed date column to determine the date to use.
        ticket_list['True Closed Date'] = ticket_list[['Completed Date', 'Closed Date']]\
            .apply(determine_true_closed_date, axis=1)

        # Standardize the True completed date column
        # ticket_list['True Closed Date'] = ticket_list['TrueClosed'].apply(convert_datetime_to_date)

        ticket_list.drop(['attributes'], axis=1, inplace=True)

        print "\n<--------------Yo here ------------>"
        print ticket_list.head()

        # Reduce the columns used.
        grouped_tickets = ticket_list[['True Start Date', 'True Closed Date', 'Id', 'Status', 'Created Date', 'Department_Requesting__c', 'Project__c', 'Priority', 'Closed Date']]
        grouped_tickets_columns = grouped_tickets.columns


        print "\n<--------------Grouped here ------------>"
        print grouped_tickets.head()

        open_list = pd.DataFrame(columns=['True Start Date', 'Snap Shot Date', 'Id', 'Status', 'Created Date', 'Department_Requesting__c', 'Project__c', 'Priority', 'True Closed Date']) #, 'Project__c', 'Release_Date__c', 'Status', 'Department_Requesting__c', 'Open Cases'])
        open_list_columns = open_list.columns.tolist()

        pbar = Bar(len(grouped_tickets.values))
        for each in grouped_tickets.values:
            try:
                if each[0] != dt.datetime.strptime('2000-01-01', '%Y-%m-%d').date():
                    cursor = each[0]
                    open_list = open_list.append(create_history(each, cursor, open_list_columns), ignore_index=True)
                else:
                    print each[0],  each[-1]
            except:
                error_result = "Unexpected error 1G: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
                print error_result, " ", open_list_columns
            pbar.passed()

        print open_list

        # Package in to a tde file
        # Package in to a hyper file
        data_file = HyperAssembler(data_frame=open_list, extract_name=extract_name, file_path=file_path)
        # Set values for publishing the data.
        file_name = str(data_file)
        tableau_server = Tableau(server_url='https://tableau.bazaarvoice.com/', site_id='BizTech')
        global project
        tableau_server.publish_datasource(project=project,
                                          file_path=file_name,
                                          mode='Append', name=extract_name)
        file_name = str(data_file)

        # Set values for publishing the data.
        server_url, username, password, site_id, data_source_name, project = \
            auth.tableau_publishing(datasource_type='BizApps',
                                    data_source_name="Historical BizReq Business Demand Backlog")
        publish_data(server_url, username, password, site_id, file_name, data_source_name, project, replace_data=True)

        notify = Notifier()
        notify.alert_the_light()
        # alert_homer()
    except:
        error_result = "Unexpected error 1TL: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
        print error_result


if __name__ == '__main__':
    main()