__author__ = 'Lothilius'

import requests
import json
from bs4 import BeautifulSoup
from selenium import webdriver
import sys
from Status import Status

class Concur(Status):
    """ Extend Status class for Helpdesk.
    """

    def get_error(self, soup_status_page):
        """
        :param soup_status_page:
        :return:
        """
        try:
            recent_message = soup_status_page.find('td', id='product-name')
            status_message = recent_message.string
            return status_message
        except:
            recent_message = soup_status_page.find('div', id='recent-posts')
            recent_date = recent_message.div.div.string
            print recent_date
            recent_message = recent_message.find('div', class_='post-update').p.string

            recent_p = recent_message.find('p')
            print recent_p
            recent_time = recent_p.find_all('span').string

            time_string = ''
            for each in recent_time:
                time_string = time_string + ' ' + each

            status_message = recent_date + ' ' + recent_message + ' ' + recent_time

            return status_message

    def explore_page(self, status_page):
        """  Parse the status_page and return only the needed amount of text for determining the status.
        :return: minimal text requested associated with checking status.
        """
        soup = BeautifulSoup(status_page, 'html.parser')

        # Find the product name column in the status table and get the rows of the table separated.
        product_table = soup.find('div', id='us_content').find_all('td', class_='product-name')
        status_table = []
        status_message = ''
        row = range(0, len(product_table))
        for i, each in enumerate(product_table):
            product = each.string
            icon = soup.find_all('td',
                                 attrs={'class':'icon blue-stripe chart',
                                        'data-reactid': '.1.1.0.1.$%s%s.0'
                                                        % (product, row[i])})

            status_table.append([product, '%s' % icon])

            # TODO - Create Better message creation
            if "NORMAL symbol " in str(icon[0]):
                pass
            else:
                try:
                    link = icon[0].a
                    status_message = status_message + 'http://concuropenstatus.concur.com/%s ' % link.get('href')
                except:
                    error_result = "Unexpected error 3: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
                    self.set_error_message(error_result)
                    return 2



        return status_table, status_message

    def get_status(self):
        # Get NetSuite Status from Status page using headless Webkit so that javascript is rendered.
        try:
            browser = webdriver.PhantomJS(executable_path=
                                          '/Users/martin.valenzuela/Dropbox/Coding/BV/'
                                          'phantomjs-2.0.0-macosx/bin/phantomjs') # Might need executable_path=
            browser.get("http://concuropenstatus.concur.com/#us")
            concur_reply = browser.page_source
            browser.quit()

            status_list, status_message = self.explore_page(concur_reply)
            if status_message == '':
                self.set_status_message('Functioning normally')
            else:
                self.set_status_message(status_message)

            # Iterate through status list to make sure all components of Concur are up.
            up_count = 0
            if len(status_list[0]) == 2:
                for each in status_list:
                    if "NORMAL symbol " in each[1]:
                        up_count = up_count + 1
                    elif str(each[0]) == each[1]:
                        up_count = up_count + 1
                    else:
                        pass
            if up_count == len(status_list):
                return 1
            else:
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
    status = Concur()
    print status
