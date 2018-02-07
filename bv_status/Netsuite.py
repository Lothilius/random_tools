__author__ = 'Lothilius'

import requests
import json
from bs4 import BeautifulSoup
from selenium import webdriver
import sys
from Status import Status
import os


class Netsuite(Status):
    """ Extend Status class for Helpdesk.
    """

    def get_error(self, soup_status_page):
        """
        :param soup_status_page:
        :return:
        """
        try:
            recent_message = soup_status_page.find('div', id='recent-posts')
            recent_date = recent_message.div.div.string

            recent_message = recent_message.find('div', class_='post-update').p.string

            status_message = recent_date + ' ' + recent_message

            if len(status_message) > 56:
                status_message = status_message[:56] + "..."

            return status_message
        except:
            error_result = "Unexpected error 3: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
            self.set_error_message(error_result)
            recent_message = soup_status_page.find('div', id='no-recent-posts')
            status_message = recent_message.string
            return status_message

    def explore_page(self, status_page):
        """  Parse the status_page and return only the needed amount of text for determining the status.
        :return: minimal text requested associated with checking status.
        """
        soup = BeautifulSoup(status_page, 'html.parser')

        # Find the left portion of the status table and get the rows of the table separated.
        left_table = soup.find('table', id='current-status-left')

        left_table = left_table.find_all('tr')

        # Find the left portion of the status table and get the rows of the table separated.
        right_table = soup.find('table', id='current-status-right')
        right_table = right_table.find_all('tr')

        # Join results in to a list.
        status_table = []
        for each in left_table:
            status_table.append([each.td.string, '%s' % each.use])

        for each in right_table:
            status_table.append([each.td.string, '%s' % each.use])

        status_message = self.get_error(soup)

        return status_table, status_message

    def get_status(self):
        # Get NetSuite Status from Status page using headless Webkit so that javascript is rendered.
        try:
            browser = webdriver.PhantomJS(executable_path=os.environ['PHANTOM_JS'])
            browser.get("https://status.netsuite.com/#dtc=se4#")
            browser.implicitly_wait(2)
            netsuite_reply = browser.page_source
            browser.quit()

            status_list, status_message = self.explore_page(netsuite_reply)

            # Iterate through status list to make sure all components of NetSuite are up.
            up_count = 0
            if len(status_list[0]) == 2:
                for each in status_list:
                    if "icon-icon_messaging_available" in each[1] or each[0] == None:
                        up_count = up_count + 1
                    else:
                        pass
            if up_count == len(status_list):
                if status_message == 'No recent posts':
                    self.set_status_message('Functioning normally')
                else:
                    self.set_status_message(status_message)
                return 1
            else:
                self.set_status_message(status_message)
                return 0
        except:
            error_result = "Unexpected error 2: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
            self.set_error_message(error_result)
            return 2

    def get_all_tickets(self):
        try:
            # self.set_status_message('Functioning normally')
            self.set_error_message('No Errors Reported.')
            self.set_status(self.get_status())

            return -1
        except:
            error_result = "Unexpected error 1: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
            self.set_error_message(error_result)

            return -1

if __name__ == '__main__':
    status = Netsuite()
    print status
