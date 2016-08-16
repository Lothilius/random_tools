__author__ = 'Lothilius'

from se_helpers.actions import concur_employee_deprecation
from se_helpers.actions import go_to_concur_user_page
import pandas as pd
import sys


if __name__ == '__main__':
    # file_location = raw_input('Hello where is the file of users: ')
    # employee_list = pd.read_csv(file_location)
    # file_location = raw_input('Where is the file: ')
    # employee_term = pd.read_csv(file_location)
    browser = go_to_concur_user_page()

    employee_list = pd.read_csv('/Users/martin.valenzuela/Downloads/Concur_removal.csv')
    for each in employee_list[['Employee ID', 'Employee Name', 'DOT']].itertuples():
        try:
            concur_employee_deprecation(browser, str(each[1]), str(each[2]), str(each[3]))
        except:
            print each[2], " Unexpected error 1:", sys.exc_info()[0], sys.exc_info()[1]