__author__ = 'Lothilius'

import dateutil
import csv
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