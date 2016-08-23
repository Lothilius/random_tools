__author__ = 'Lothilius'

import pandas as pd
import datetime as dt
import numpy as np

pd.set_option('display.width', 180)
pd.set_option('display.max_columns', None)


def merge_dataframes(dataframe_a, dataframe_b, unique_id, second_index):
    """
    :param dataframe_a: A pandas dataframe
    :param dataframe_b: A pandas dataframe
    :return: A pandas dataframe that combines the two dataframes and enforces a uniqueness on an index provided.
    """
    frames = [dataframe_a, dataframe_b]
    dataframe_c = pd.concat(frames, ignore_index=True)
    dataframe_c.drop_duplicates(subset=[unique_id, second_index], keep='first', inplace=True)

    return dataframe_c

def standerdize(value):
    value = value.replace(' ', '')
    value = value.replace('_', '')
    value = value.lower()

    return value

def match_up_columns(dataframe_a, dataframe_b):
    df_a_columns = pd.Series(dataframe_a.columns)
    df_b_columns = pd.Series(dataframe_b.columns)

    df_a_columns = df_a_columns.apply(standerdize)
    df_b_columns = df_b_columns.apply(standerdize)

    print df_b_columns[df_b_columns.isin(df_a_columns)]
    # print df_a_columns

def convert_datetime_to_date(the_datetime):
    # print the_datetime
    try:
        # if str(the_datetime) == str(np.nan):
        #     print the_datetime
        # print type(the_datetime), the_datetime
        if isinstance(the_datetime, dt.date):
            return the_datetime
        elif the_datetime == '2000-01-01 00:00:00' or the_datetime == None or str(the_datetime) == str(np.nan)\
                or the_datetime == 'None':
            the_datetime = dt.datetime.strptime('2000-01-01 00:00:00', '%Y-%m-%d %H:%M:%S').date()
            return the_datetime
        elif the_datetime == 'Not Assigned' or the_datetime == '-':
            the_datetime = dt.datetime.strptime('2000-01-01 00:00:00', '%Y-%m-%d %H:%M:%S').date()
            return the_datetime
        else:
            the_datetime = dt.datetime.strptime(the_datetime, '%Y-%m-%d %H:%M:%S').date()
            return the_datetime
    except ValueError:
        try:
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
                    try:
                        the_datetime = dt.datetime.strptime(the_datetime, '%m/%d/%y %H:%M').date()
                        return the_datetime
                    except ValueError, e:
                        try:
                            the_datetime = dt.datetime.strptime(the_datetime, '%b %d, %Y %H:%M %p').date()
                            return the_datetime
                        except ValueError, e:
                            print e
    except TypeError:
        try:
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
                    print e

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

def main():
    dataframe_a = '/Users/martin.valenzuela/Box Sync/Documents/Austin Office/HDT/year_to_date_7-31-2016.csv' #raw_input("Where is the frist csv? ")
    dataframe_b = '/Users/martin.valenzuela/Box Sync/Documents/Austin Office/HDT/ArchiveRequestsView_8_3_16.csv' #raw_input("Where is the second csv? ")

    dataframe_a = pd.read_csv(dataframe_a)
    # print "DF A: %s" % dataframe_a[['WORKORDERID', 'CREATEDTIME', 'COMPLETEDTIME', 'RESOLUTIONLASTUPDATEDTIME']]


    dataframe_a.rename(columns={'WORKORDERID': 'RequestID', 'ID': 'RequestID', 'STATUS': 'Request Status',
                                'System': 'System Name', 'Department_Group': 'High-Level Department'}, inplace=True)
    dataframe_a['Created Time'] = dataframe_a['CREATEDTIME'].apply(convert_datetime_to_date)
    dataframe_a['Completed Time'] = dataframe_a['COMPLETEDTIME'].apply(convert_datetime_to_date)
    dataframe_a['Resolved Time'] = dataframe_a['RESOLUTIONLASTUPDATEDTIME'].apply(convert_datetime_to_date)
    dataframe_a.columns = map(str.title, dataframe_a.columns)
    remove_description_columns(dataframe_a)


    dataframe_b = pd.read_csv(dataframe_b)
    dataframe_b = dataframe_b[dataframe_b['Group'].str.contains("BizApps")]
    print "DF B: %s" % dataframe_b.columns
    dataframe_b.rename(columns={'Id': 'RequestID', 'Created Date':'Created Time', 'Status': 'Request Status',
                                'Completed Date':'Completed Time', 'System': 'System Name',
                                'Requester': 'Requester Name', 'Due By': 'Duebytime'}, inplace=True)
    dataframe_b['Created Time'] = dataframe_b['Created Time'].apply(convert_datetime_to_date)
    dataframe_b['Completed Time'] = dataframe_b['Completed Time'].apply(convert_datetime_to_date)
    dataframe_b['Resolved Time'] = dataframe_b['Completed Time'].apply(convert_datetime_to_date)
    dataframe_b.columns = map(str.title, dataframe_b.columns)
    remove_description_columns(dataframe_b)


    # match_up_columns(dataframe_a, dataframe_b)

    print "DF A: %s" % dataframe_a.columns
    print "DF B: %s" % dataframe_b.columns
    unique_id = 'Requestid'#raw_input("What is the name of the unique id Column? ")
    second_index = 'Created Time'#raw_input("What is the name of the second index point? ")

    dataframe_c = merge_dataframes(dataframe_a, dataframe_b, unique_id, second_index)
    now = dt.datetime.now().strftime('%Y-%m-%d')
    # print dataframe_c[['Requestid', 'Created Time', 'Completed Time', 'Resolved Time']]
    # print dataframe_c[dataframe_c['Requestid']==7441]
    # cut_off_date = dt.datetime.strptime('2015-11-01', '%Y-%m-%d').date()
    # dataframe_c = dataframe_c[dataframe_c['Created Time']>=cut_off_date]

    print dataframe_c
    dataframe_c.to_csv('/Users/martin.valenzuela/Box Sync/Documents/Austin Office/HDT/full_full_%s.csv' % now)#, index=False)

if __name__ == '__main__':
    main()


