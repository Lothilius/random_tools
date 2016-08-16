__author__ = 'Lothilius'

import dateutil
import csv
import pandas as pd
from datetime import datetime

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


# Set Date columns as the datetime dtype
def correct_date_dtype(data_frame, date_time_format=''):
    """
    :param data_frame: Pandas dataframe
    :return: a pandas data frame
    """
    date_time_columns = ['CREATEDTIME',
                         'DUEBYTIME',
                         'COMPLETEDTIME',
                         'RESOLUTIONLASTUPDATEDTIME',
                         'RESPONDEDTIME',
                         'Extract_Timestamp']
    columns = data_frame.columns
    data_frame.fillna('0', inplace=True)
    for each in columns.tolist():
        if each in date_time_columns:
            data_frame[each].replace(to_replace=['0', 'NA', '-1', '-'], value='2000-01-01 00:00:00', inplace=True)
            # data_frame[each].replace(to_replace='NA', value='2000-01-01 00:00:00', inplace=True)
            data_frame[each] = pd.to_datetime(data_frame[each], format=date_time_format)

    return data_frame



if __name__ == '__main__':
    now = datetime.now()
    today = datetime.today()
    test = pd.DataFrame(columns=['col1', 'col2', 'col3', 'CREATEDTIME'], data=[[1, 2.3, 'a', None],
                                                                        [2, 3.3, 'b', '2016-07-06']])
    print test
    print correct_date_dtype(test)