__author__ = 'Lothilius'

import requests
import json
from bv_authenticate.Authentication import Authentication as auth
import time
import sys

def wait(seconds=5):
    time.sleep(seconds)

class HelpdeskConnection(object):
    @staticmethod
    def create_api_request(helpdesk_que='7256000001457777_MyView_7256000001457775', from_value=1):
        """ Create the api request for HD. At the moment very minimal
            but can be expanded in the future for creating more specific and different types of requests.
        :param helpdesk_que: This is the view name that can be created in the requests page
        :param from_value: Sets the beginning value in the list returned
        :param filter_request: Defines if the request is for the list of filters.
        :return: string of the URL, dict of the query, and a dict of the header
        """
        # Main HDT api URL
        url = "https://sdpondemand.manageengine.com/api/json/request"
        # Query values go in this json structure
        querystring = {"scope":"sdpodapi",
                       "authtoken": auth.hdt_token(),
                       "OPERATION_NAME": "GET_REQUESTS",
                       "INPUT_DATA": "{operation:{"
                                    "Details:{"
                                    "FILTERBY:'%s', FROM:%s, LIMIT:100}}}" % (helpdesk_que, from_value) }

        # Header information
        headers = {
            'cache-control': "no-cache",
            }
        return url, querystring, headers

    @staticmethod
    def fetch_from_helpdesk(url, querystring, headers):
        """ Makes the actual call to the help desk server.
        :param url: Send in the base url for the REST Call
        :param querystring:
        :param headers:
        :return: Return a data frame of the
        """
        try:
            wait(1)
            # Create the request and capture the response.
            response = requests.request("POST", url, headers=headers, params=querystring)
            # print response.txt
            # Load the response to the request as a json object.
            helpdesk_tickets = json.loads(response.text)
        except AttributeError:
            error_result = "Unexpected error 2: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
            print error_result
            print helpdesk_tickets["operation"]
            wait(3)
            HelpdeskConnection.fetch_from_helpdesk(url, querystring, headers)

        # print(json.dumps(helpdesk_tickets["operation"]["Details"], indent=4))
        try:
            return helpdesk_tickets["operation"]["Details"]
        except KeyError:
            return helpdesk_tickets["operation"]["result"]
        except:
            error_result = "Unexpected error 1: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
            print error_result
            print helpdesk_tickets["operation"]
            wait(2)
            HelpdeskConnection.fetch_from_helpdesk(url, querystring, headers)

    # @staticmethod
    # def get_view_id(view_name=''):
    #     try:
    #         # Get the view ID for the pending view HD
    #         filters = pd.DataFrame(TicketList.get_filter_list())
    #         view__id = filters[filters.VIEWNAME == 'Pending'].VIEWID.iloc[0]
    #
    #         return view__id
    #     except ValueError:
    #         view_name = raw_input('Please enter valid view name: ')
    #         get_view_id(view_name)
    #     except:
    #         error_result = "Unexpected error 1: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
    #         print error_result

