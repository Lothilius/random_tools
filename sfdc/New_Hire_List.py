__author__ = 'Lothilius'

import SFDC_User
import numpy as np


class NewHireList:
    """Create a New Hire List object that holds the data of many
        Users and their permissions.
    """
    def __int__(self):
        self._new_hire_list = np.array([])

    # Get user information from CSV file
    def array_from_file(self, filename):
        """Given an external file containing data,
                create an array from the data.
                The assumption is the top row contains column
                titles."""
        data_array = []
        with open(filename, 'rU') as csv_file:
            spam_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
            for row in spam_reader:
                data_array.append(row)

        data_array = np.array(data_array)

        return data_array

