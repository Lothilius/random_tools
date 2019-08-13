__author__ = 'Lothilius'

from se_helpers.actions import go_to_jira_login_page
from se_helpers.actions import jira_login, jira_check_login
from se_helpers.actions import wait
import pandas as pd
import sys

pd.set_option('display.width', 290)

if __name__ == '__main__':
    # file_location = raw_input('Hello where is the file of user: ')
    # employee_list = pd.read_csv(file_location)
    # file_location = raw_input('Where is the file: ')
    # employee_term = pd.read_csv(file_location)

    employee_list = pd.read_csv('/Users/martin.valenzuela/Downloads/PROD CWD_USER LIST.csv')

    # print employee_list
    for each in employee_list['user_name'].to_list():
        try:
            browser = go_to_jira_login_page()
            jira_login(browser, str(each), 'qwerty123') #str(each[1]))
            # jira_check_login(browser)
            print str(each[0]) + "done"
            wait(.5)
            browser.close()
        except:
            print each[2], " Unexpected error 1:", sys.exc_info()[0], sys.exc_info()[1]