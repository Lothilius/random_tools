# coding: utf-8
__author__ = 'Lothilius'

import datetime as dt
import re
import sys

import pandas as pd

from helper_scripts.misc_helpers.data_manipulation import correct_date_dtype
from helper_scripts.notify_helpers import *

pd.set_option('display.width', 250)
pd.set_option('display.max_columns', 40)
pd.set_option('display.max_rows', 16)
pd.set_option('max_colwidth', 20)

# List of Standard columns
standard_column_names = ['CATEGORY',
                         'COMPLETEDTIME',
                         'CREATEDBY',
                         'CREATEDTIME',
                         'DELETED_TIME',
                         'DEPARTMENT',
                         'DUEBYTIME',
                         'GROUP',
                         'HASATTACHMENTS',
                         'HASCONVERSATION',
                         'HASNOTES',
                         'ISPENDING',
                         'ITEM',
                         'LEVEL',
                         'LONG_REQUESTID',
                         'MODE',
                         'PRIORITY',
                         'REQUESTER',
                         'REQUESTEREMAIL',
                         'REQUESTTEMPLATE',
                         'RESOLUTION',
                         'RESOLUTIONLASTUPDATEDTIME',
                         'RESOLVER',
                         'RESPONDEDTIME',
                         'DESCRIPTION',
                         'SHORTDESCRIPTION',
                         'SITE',
                         'SLA',
                         'STATUS',
                         'STOPTIMER',
                         'SUBCATEGORY',
                         'SUBJECT',
                         'TECHNICIAN',
                         'TEMPLATEID',
                         'TIMESPENTONREQ',
                         'Department_Group',
                         'System Component',
                         'System',
                         'WORKORDERID']


def merge_dataframes(dataframe_a, dataframe_b, unique_id, second_index):
    """
    :param dataframe_a: A pandas dataframe
    :param dataframe_b: A pandas dataframe
    :return: A pandas dataframe that combines the two dataframes and enforces a uniqueness on an index provided.
    """
    frames = [dataframe_a, dataframe_b]
    dataframe_c = pd.concat(frames, ignore_index=True)
    dataframe_c[unique_id] = dataframe_c[unique_id].astype(str)
    dataframe_c[second_index] = dataframe_c[second_index].astype(str)
    dataframe_c.drop_duplicates(subset=[unique_id, second_index], keep='last', inplace=True)
    # print dataframe_c[dataframe_c['CREATEDTIME'] == 'Business Applications']

    dataframe_c = correct_date_dtype(dataframe_c, date_time_format='%Y-%m-%d %H:%M')

    return dataframe_c


def standerdize(value):
    value = value.replace(' ', '')
    value = value.replace('_', '')
    value = value.upper()

    return value


def match_up_columns(dataframe_a, dataframe_b):
    df_a_columns = pd.Series(dataframe_a.columns)
    df_b_columns = pd.Series(dataframe_b.columns)

    df_a_columns = df_a_columns.apply(standerdize)
    df_b_columns = df_b_columns.apply(standerdize)

    # print "DF A length: %s" % len(df_a_columns)
    # print "DF A length: %s" % len(df_b_columns)
    # print len(df_b_columns[~df_b_columns.isin(df_a_columns)])
    # print df_b_columns[~df_b_columns.isin(df_a_columns)]

    return df_b_columns[~df_b_columns.isin(df_a_columns)], len(df_a_columns) - len(df_b_columns)


def remove_description_columns(data_frame):
    try:
        data_frame.drop('Shortdescription', axis=1, inplace=True)
        print 'Shortdescription removed'
    except:
        pass
    try:
        data_frame.drop('Description', axis=1, inplace=True)
        print 'Description removed'
    except:
        pass
    try:
        data_frame.drop('Resolution', axis=1, inplace=True)
        print 'Resolution removed'
    except:
        pass
    try:
        data_frame.drop('Subject', axis=1, inplace=True)
        print 'Subject removed'
    except:
        pass
    return data_frame


def add_missing_columns(dataframe_a, dataframe_b):
    """ Add missing columns after comparing the two dataframe column names
    :param dataframe_a: a standard dataframe
    :param dataframe_b: the second standard dataframe
    :return: both data frames with matching columns
    """
    missing_columns, length_difference = match_up_columns(dataframe_a, dataframe_b)
    print missing_columns, type(missing_columns)

    # Check if and which data frame needs missing columns
    if length_difference < 0 and len(missing_columns) != 0:
        dataframe_a[missing_columns] = ""
    elif length_difference > 0 and len(missing_columns) != 0:
        dataframe_b[missing_columns] = ""
    else:
        raise ValueError + 'Something is wrong here. '


def rename_columns(data_frame):

    # Convert column names.
    data_frame.rename(columns={ 'REQUESTMODE': 'MODE',
                                'RESOLVEDTIME': 'RESOLUTIONLASTUPDATEDTIME',
                                'RESPONDEDDATE': 'RESPONDEDTIME',
                                'RESOLUTIONADDEDTIME': 'RESOLUTIONLASTUPDATEDTIME',
                                'LASTUPDATETIME': 'RESOLUTIONLASTUPDATEDTIME',
                                'REQUESTSTATUS': 'STATUS',
                                'TIMEELAPSED': 'TIMEELAPSED',
                                'HIGHLEVELDEPARTMENT': 'Department_Group',
                                'HIGH-LEVELDEPARTMENT': 'Department_Group',
                                'HIGHLEVELDEPT': 'Department_Group',
                                'DEPARTMENT_GROUP': 'Department_Group',
                                'SYSTEMNAME': 'System',
                                'SYSTEM': 'System',
                                # 'CREATEDDATE': 'CREATEDTIME',
                                # 'COMPLETEDDATE': 'COMPLETEDTIME',
                                'RESOLUTIONADDEDBY': 'RESOLVER',
                                'REQUESTERNAME': 'REQUESTER',
                                'ASSIGNEDTO': 'TECHNICIAN',
                                'ID': 'WORKORDERID'}, inplace=True)

    # TODO- Add user interaction to deal with columns not found.

    return data_frame


def standerdize_data(data_frame):
    """ Reorganize the date so that the column names are the same and as the template dataframe"""
    try:
        data_frame = pd.read_pickle(data_frame)
    except:
        print 'Trying csv.'
        try:
            data_frame = pd.read_csv(data_frame, quotechar='"', quoting=1, low_memory=False)
        except:
            try:
                data_frame = pd.read_csv(data_frame + '.csv', quotechar='"', quoting=1)
            except:
                error_result = "Unexpected error 1TL: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
                print error_result

    data_frame.rename(columns=lambda x: str(x).upper().replace(' ', ''), inplace=True)

    data_frame = rename_columns(data_frame)

    # try:
    #     data_frame.drop(['Created Date', 'Completed Date', 'Resolved Date'], axis=1, inplace=True)
    # except ValueError:
    #     pass

    # print data_frame['CREATEDTIME']
    # print data_frame['CREATEDTIME'].iloc[0], type(data_frame['CREATEDTIME'].iloc[0])

    return data_frame


def apply_date(element):
    # print element
    element.date()
    return element


def create_date_columns(data_frame):
    data_frame = correct_date_dtype(data_frame, '%Y-%m-%d %H:%M:%S')
    data_frame['Created Date'] = data_frame['CREATEDTIME'].apply(lambda x: x.date())
    data_frame['Completed Date'] = data_frame['COMPLETEDTIME'].apply(lambda x: x.date())
    data_frame['Resolved Date'] = data_frame['RESOLUTIONLASTUPDATEDTIME'].apply(lambda x: x.date())

    return data_frame


def reduce_whitespace(df):
    try:
        regex = re.compile(r'[\"%\']')
        # clean_value = strip_tags(df)
        clean_value = regex.sub(' ', df)
        clean_value = ' '.join(clean_value.split())
        if len(clean_value) > 1000:
            clean_value = clean_value[:1000]
        return clean_value
    except:
        return df


def main():
    a = '/Users/martin.valenzuela/Box Sync/Documents/Austin Office/BizReqs/Monthly_Release_Docs/HDT_History_00465111/a_b_to_2016-10-24_take_3'
    b = '/Users/martin.valenzuela/Box Sync/Documents/Austin Office/BizReqs/Monthly_Release_Docs/HDT_History_00465111/f_clean_and_ready'
    # a = '/Users/martin.valenzuela/Box Sync/Documents/Austin Office/BizReqs/Monthly_Release_Docs/HDT_History_00465111/aa_short_clean_and_ready'
    # b = '/Users/martin.valenzuela/Box Sync/Documents/Austin Office/BizReqs/Monthly_Release_Docs/HDT_History_00465111/b_clean_and_ready_Historical_Full_tickets_2015-11-02_5-4'
    # c = '/Users/martin.valenzuela/Box Sync/Documents/Austin Office/BizReqs/Monthly_Release_Docs/HDT_History_00465111/c_clean_and_ready'
    # d = '/Users/martin.valenzuela/Box Sync/Documents/Austin Office/BizReqs/Monthly_Release_Docs/HDT_History_00465111/d_clean_and_ready'
    # e = '/Users/martin.valenzuela/Box Sync/Documents/Austin Office/BizReqs/Monthly_Release_Docs/HDT_History_00465111/e_clean_and_ready'

    file_list = [a, b]
    dataframe_list = []
    for i, each in enumerate(file_list):
        # Standerdize the data sets.
        dataframe_a = standerdize_data(each)
        print "DF %s: %s" % (i, dataframe_a.columns.sort_values().tolist())
        print dataframe_a
        dataframe_list.append(dataframe_a)

        # dataframe_a, dataframe_b = add_missing_columns(dataframe_a, dataframe_b)

    unique_id = 'WORKORDERID'#raw_input("What is the name of the unique id Column? ")
    second_index = 'Created Date'  # raw_input("What is the name of the second index point? ")

    # Create the frame of a new dataframe based on the first data frame in the dataframe list.
    dataframe_c = pd.DataFrame(columns=dataframe_list[0].columns.tolist())
    for i, data_frame in enumerate(dataframe_list):
        print i
        # print "DF A: %s" % dataframe_a.CREATEDTIME.sort_values()
        # print "DF B: %s" % dataframe_b.CREATEDTIME.sort_values()
        # print data_frame[data_frame['CREATEDTIME'] != 'Business Applications']
        # for each in data_frame['CREATEDTIME'].tolist():
        #     if type(each) != pd.tslib.Timestamp:
                # print type(each)
        data_frame = create_date_columns(data_frame)
        # print data_frame
        dataframe_c = merge_dataframes(dataframe_c, data_frame, unique_id, second_index)

    dataframe_c.replace(to_replace=['0', 'NA', '-1', '-', 'Not Assigned'], value='NA', inplace=True)
    # dataframe_c.replace(to_replace=['\"', '%'], value='', inplace=True)
    # print "DF C: %s" % dataframe_c.CREATEDTIME.sort_values()
    now = dt.datetime.now().strftime('%Y-%m-%d')
    # print dataframe_c[['Requestid', 'Created Time', 'Completed Time', 'Resolved Time']]
    # print dataframe_c[dataframe_c['Requestid']==7441]
    # cut_off_date = dt.datetime.strptime('2015-11-01', '%Y-%m-%d').date()
    # dataframe_c = dataframe_c[dataframe_c['Created Time']>=cut_off_date]
    alert_homer()
    dataframe_c = dataframe_c.applymap(reduce_whitespace)
    print dataframe_c
    dataframe_c.to_csv(
        '/Users/martin.valenzuela/Box Sync/Documents/Austin Office/BizReqs/Monthly_Release_Docs/HDT_History_00465111/a_to_f_2.csv', index=False, quoting=2, quotechar='"')
    dataframe_c.to_pickle(
        '/Users/martin.valenzuela/Box Sync/Documents/Austin Office/BizReqs/Monthly_Release_Docs/HDT_History_00465111/a_to_f_2')


if __name__ == '__main__':
    main()


