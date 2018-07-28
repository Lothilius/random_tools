__author__ = 'Lothilius'

import dateutil
import csv
import pandas as pd
from datetime import datetime
from dateutil.parser import *
import numpy as np

def reformat_date_time(date_time_string):
    """
    :param date_time_string: Date time string from Salesfroce mainly in the format -> 2016-01-22T19:57:53.000Z
    :return: string of the year month and day ie '2016-01-22'
    """
    new_date_time = dateutil.parser.parse(date_time_string)
    return new_date_time.strftime('%Y-%m-%d')

# Get user information from CSV file
def array_from_file(filename):
    """Given an external file containing data,
            create an array from the data.
            The assumption is the top row contains column
            titles.
    """
    data_array = []
    with open(filename, 'rU') as csv_file:
        spam_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
        for row in spam_reader:
            data_array.append(row)

    data_array = np.array(data_array)

    return data_array

def correct_datetime_format(value):
    try:
        value = value.replace('T', ' ')
    except:
        pass
    try:
        # print value, type(value)
        value = parse(value).strftime('%Y-%m-%d %H:%M:%S')
        return value
    except:
        return value



# Set Date columns as the datetime dtype
def correct_date_dtype(data_frame, date_time_format='', date_time_columns={'CREATEDTIME',
                                                                           'DUEBYTIME',
                                                                           'COMPLETEDTIME',
                                                                           'RESOLUTIONLASTUPDATEDTIME',
                                                                           'RESPONDEDTIME',
                                                                           'Extract_Timestamp',
                                                                           'RESOLVEDDATE',
                                                                           'Created Date',
                                                                           'Completed Date',
                                                                           'Resolved Date'}):
    """
    :param data_frame: Pandas dataframe
    :return: a pandas data frame
    """
    columns = data_frame.columns
    final_df = data_frame.fillna('-')
    for column_name in columns.tolist():
        if column_name in date_time_columns:
            try:
                final_df[column_name] = final_df[column_name].apply(correct_datetime_format)
                final_df[column_name].replace(to_replace=['0', 'NA', '-1', '-', 'Not Assigned', np.nan],
                                              value='2000-01-01 00:00:00', inplace=True)
                # data_frame[column_name].replace(to_replace='NA', value='2000-01-01 00:00:00', inplace=True)
                # print data_frame.columns
                final_df[column_name] = pd.to_datetime(final_df[column_name], format=date_time_format, errors='coerce')
                # print data_frame[column_name].iloc[0], type(data_frame[column_name].iloc[0])
                # data_frame[column_name] = data_frame[column_name].apply(lambda x: x.date())
            except IOError:
                pass

    return final_df


def create_feature_vector_dataframe(dataframe, feature_index_column, feature_column, suffix=''):
    """
    :param dataframe:
    :param feature_index_column:
    :param feature_column:
    :return:
    """
    grouped_features = dataframe.groupby([feature_index_column, feature_column]).count().reset_index()
    feature_vector_dataframe = grouped_features.pivot(
        index=feature_index_column, columns=feature_column, values=feature_column).reset_index()

    if suffix != '':
        try:
            column_names = pd.Series(data=[element + suffix for element in feature_vector_dataframe.columns.tolist()],
                                     index=feature_vector_dataframe.columns.tolist())
        except TypeError:
            column_names = pd.Series(data=[(element[0] + suffix, element[1]) for element in feature_vector_dataframe.columns.tolist()],
                                     index=feature_vector_dataframe.columns.tolist())
        column_names.drop(feature_index_column, inplace=True)

        feature_vector_dataframe.rename(columns=column_names.to_dict(), inplace=True)

    return feature_vector_dataframe


def create_feature_dataframe(df, id_column, feature_column):
    """ Create a dataframe of the id and feature column of a data frame.
    The elements in the feature column are expected to contain a dict.

    :param df: dataframe
    :param id_column: the name of the column that has the id for the record row
    :param feature_column: the column name of features held as a dict.
    :return: dataframe
    """
    # Create Copy of dataframe for changes
    content = df[[feature_column, id_column]].copy(deep=True)
    # Convert Dict elements in to dataframes and

    feature_df = pd.DataFrame()

    # iterate over the feature dataframe to peal out all the features in the single column
    for row in content.iterrows():
        if isinstance(row[1][feature_column], list):
            df_feature_values = pd.DataFrame(row[1][feature_column])
        else:
            df_feature_values = pd.DataFrame([row[1][feature_column]])

        df_feature_values[id_column] = row[1][id_column]

        feature_df = pd.concat([feature_df, df_feature_values])

    return feature_df


def aggregate_for_table_pivot(value_list):
    for i, values in enumerate(value_list):
        if isinstance(values, (int, long, float)):
            value_list[i] = str(values)
        else:
            value_list[i] = values.encode("utf-8", errors="replace")
    return ', '.join(value_list)


def expand_nested_fields_to_dataframe(df, id_column, feature_column, value_column):
    """Create a dataframe of the id and feature column of a data frame.
    The elements in the feature column are expected to contain a dict.

    :param id_column:
    :param feature_column:
    :param value_column:
    :return:
    """
    # Create Copy of dataframe for changes
    content = df[[feature_column, value_column, id_column]].copy(deep=True)
    content.fillna('-', inplace=True)

    # Create a pivoted table of values in columns form.
    feature_df = pd.pivot_table(content, index=id_column, columns=feature_column, values=value_column, fill_value='-',
                                aggfunc=aggregate_for_table_pivot)
    feature_df.reset_index(inplace=True)
    feature_df.fillna('-', inplace=True)

    return feature_df


def multiply_by_multiselect(dataframe, feature_index_column, feature_column):
    columns = dataframe.columns.tolist()
    # print dataframe.set_index(columns)
    dataframe_reformated = dataframe.apply(lambda x: pd.Series(x[feature_column]), axis=1).stack().reset_index(level=1, drop=True)
    dataframe_reformated.name = feature_column + "_as_feature_column"
    dataframe_reformated = dataframe.join(dataframe_reformated)
    # dataframe_reformated.name = feature_column
    return dataframe_reformated


def convert_sfdc_datetime_to_datetime(the_datetime):
    if the_datetime is not None:
        the_datetime = the_datetime.split('T')
        the_datetime = dt.datetime.strptime(the_datetime[0], '%Y-%m-%d').date()
        return the_datetime
    else:
        return dt.datetime.strptime('2000-01-01', '%Y-%m-%d').date()


if __name__ == '__main__':
    now = datetime.now()
    today = datetime.today()
    test = pd.DataFrame(columns=['col1', 'col2', 'col3', 'CREATEDTIME'], data=[[1, 2.3, 'a', None],
                                                                        [2, 3.3, 'b', '2016-07-06']])
    print test
    print correct_date_dtype(test)