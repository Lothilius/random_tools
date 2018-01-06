__author__ = 'Lothilius'

import requests
import json
from bv_authenticate.Authentication import Authentication as auth
import sys
from bv_status.Status import Status
from simple_salesforce import Salesforce
import simple_salesforce.login
import time
import sys


def wait(seconds=5):
    time.sleep(seconds)

class SFDC(Status):
    """ Extend Status class for Helpdesk.
    """

    @staticmethod
    def status_api_request(instance='na3'):
        """
        """
        # Main SFDC api URL
        url = "http://api.status.salesforce.com/v1/instances/%s/status" % instance

        # Header information
        headers = {
            "Accept": "application/json"
        }
        return url, headers

    @staticmethod
    def fetch_status_jason(url, headers):
        """ Makes the actual call to the Salesforce Status API.
        :param url: Send in the base url for the REST Call
        :param headers: Set to accept Jason or other.
        :return: Return a Status
        """
        try:
            wait(1)
            # Create the request and capture the response.
            response = requests.request("GET", url, headers=headers)
            # print response.txt
            # Load the response to the request as a json object.
            raw_sfdc_status_jason = json.loads(response.text)
            status_message = raw_sfdc_status_jason['status']

            if len(raw_sfdc_status_jason['Incidents']) != 0:
                status_detail = raw_sfdc_status_jason['Incidents'][0]['id']
                status_detail = "%s: %s" % (status_detail, raw_sfdc_status_jason['Incidents'][0]['additionalInformation'])
            else:
                status_detail = 'No Error Reported.'

            return status_message, status_detail
        except AttributeError:
            error_result = "Unexpected error 3: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
            print error_result
            print raw_sfdc_status_jason["operation"]
            wait(3)
            raw_sfdc_status_jason.fetch_from_helpdesk(url, headers)

    def get_status(self):
        # Get SFDC Status from Status page using headless Webkit so that javascript is rendered.
        try:
            url, headers = self.status_api_request()
            status_list, status_message = self.fetch_status_jason(url=url, headers=headers)

            if status_list == 'OK':
                self.set_status_message('Functioning normally')
                self.set_error_message('No Error Reported.')
                return 1
            # Detect if non Major notice is posted.
            elif 'INFORMATIONAL' in status_list['status'] \
                    or 'MAINTENANCE' == status_list['status'] \
                    or 'MINOR' == status_list['status']:
                return 2
            else:
                self.set_status_message(status_message)
                return 0
        except:
            error_result = "Unexpected error 2: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
            self.set_error_message(error_result)
            return 2

    def get_error(self):
        #     TODO - Parse site for the error message.
        pass


    def get_count(self, result):
        return result['totalSize']

    def get_cases(self, environment='staging',
                  type='01250000000Hnex',
                  status='In Progress',
                  sub_status='In Development',
                  technician=''):
        """ Get helpdesk tickets for the respective que 100 at a time.
        :return: OrderedDict that contains totalsize, done, and records. Records in turn is also given as an
                OrderedDict with the actualrecords data.
        """
        sf = SFDC.connect_to_SFDC(environment)
        result = sf.query_all(SFDC.build_query())

        return result

    @staticmethod
    def connect_to_SFDC(environment='prod'):
        user_name, pw, token, sandbox = auth.sfdc_login(environment)
        sf = Salesforce(username=user_name, password=pw, security_token=token, sandbox=sandbox, version='32.0')

        return sf

    def get_all_tickets(self):
        try:
            cases = self.get_cases(environment='prod')
            number_of_cases = self.get_count(cases)
            self.set_status(self.get_status())

            return number_of_cases
        except simple_salesforce.login.SalesforceAuthenticationFailed:
            error_result = "Unexpected error 1a: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
            self.set_status_message('Fix SFDC BizApps Credentials')
            self.set_error_message(error_result)
            return -1
        except:
            error_result = "Unexpected error 1b: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
            self.set_error_message(error_result)

            return -1


if __name__ == '__main__':
    status = SFDC()
    print status
