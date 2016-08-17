__author__ = 'Lothilius'

import csv

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

class Permissions():
    """Create a New Hire List object that holds the data of many
        Users and their permissions.
    """
    def __int__(self, title):
        self.permission = [ ]
