__author__ = 'Lothilius'

import requests
import json
import sys
import bv_authenticate.Authentication as auth
from Status import Status
import time


def wait(seconds=5):
    time.sleep(seconds)

class Okta(Status):
    """ Extend Status class for Okta.
    """
    def get_status(self):
        # One possibility in to poll their twitter account or check load time for loading a HD page.
        if True:
            return 1

    def count_tickets(self, helpdesk_tickets):
        """Count total unassigned"""
        tickets_total = 0
        for each in helpdesk_tickets:
            tickets_total += 1

        if tickets_total != 0:
            self.set_status(0)
            self.set_status_message('Please address in Salesforce.')

        return tickets_total

    def aggregate_tickets(self, ticket_list_a, ticket_list_b):
        """ Join to lists of helpdesk tickets.

        :param ticket_list_a: list
        :param ticket_list_b: list
        :return: list - helpdesk_tickets
        """
        helpdesk_tickets = ticket_list_a + ticket_list_b

        return helpdesk_tickets

    def create_api_request(self, helpdesk_que='7256000002227583_MyView_7256000002227577', from_value=1):
        """ Create the api request for HD. At the moment very minimal
            but can be expanded in the future for creating more specific and different types of requests.
        :param helpdesk_que: This is the view name that can be created in the requests page
        :param from_value: Sets the beginning value in the list returned
        :return: string of the URL, dict of the query, and a dict of the header
        """
        # Main HDT api URL
        url = "https://sdpondemand.manageengine.com/api/json/request"

        # Query values go in this json structure
        querystring = {"scope":"sdpodapi",
                       "authtoken":auth.hdt_token(),
                       "OPERATION_NAME":"GET_REQUESTS",
                       "INPUT_DATA":"{operation:{"
                                    "Details:{"
                                    "FILTERBY:'%s', FROM:%s, LIMIT:100}}}" % (helpdesk_que, from_value) }

        # Header information
        headers = {
            'cache-control': "no-cache",
            }
        return url, querystring, headers


    def get_100_tickets(self, helpdesk_que='7256000002227583_MyView_7256000002227577', from_value=1):
        """ Get helpdesk tickets for the respective que 100 at a time.
        :return: list of dicts - helpdesk_tickets
        """
        url, querystring, headers = self.create_api_request(helpdesk_que, from_value)

        # Create the request and capture the response.
        response = requests.request("POST", url, headers=headers, params=querystring)

        # Load the response to the request as a json object.
        helpdesk_tickets = json.loads(response.text)

        return helpdesk_tickets["operation"]["Details"]

        # print(json.dumps(helpdesk_tickets["operation"]["Details"], indent=4))

    def get_all_tickets(self):
        try:
            from_value = 1
            # Get first 100 ticket from helpdesk
            helpdesk_tickets = self.get_100_tickets()

            # Check if more than 100 exist and need to be aggregated.
            if len(helpdesk_tickets) == 100:
                # TODO - Make this a recursive method!!!
                while len(helpdesk_tickets) % 100 == 0:
                    from_value = from_value + 100
                    helpdesk_tickets = self.aggregate_tickets(
                        helpdesk_tickets, self.get_100_tickets(from_value=from_value))
            self.set_status(self.get_status())
            self.set_status_message('Functioning normally')
            self.set_error_message('No Error Reported.')

            return self.count_tickets(helpdesk_tickets)
        except:
            error_result = "Unexpected error 1: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
            self.status = 2
            self.set_status_message('Error Loading')
            # TODO -Fix this issue so that error_message is populated!
            self.error_message = error_result

            return -1

if __name__ == '__main__':
    status = Okta()
    print status
