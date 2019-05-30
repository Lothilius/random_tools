# -*- coding: utf-8 -*-
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
    def create_api_request(from_value=1, query=''):
        """ Create the api request for HD. At the moment very minimal
            but can be expanded in the future for creating more specific and different types of requests.
        :param query: This is email that is being serached for.
        :param from_value: Sets the beginning value in the list returned
        :return: string of the URL, dict of the query, and a dict of the header
        """
        # print from_value
        # Main HDT api URL
        url = "https://sdpondemand.manageengine.com/app/itdesk/api/v3/requests"

        query_first_part = "{'list_info':{""'start_index':%s," \
                           "'get_total_count':'true'," \
                           "'row_count':100," \
                           "'fields_required':['id','display_id','subject', 'status','attachments'," \
                           "'has_notes','site', 'responded_time','deleted_on','time_elapsed ','created_time'," \
                           "'category', 'group','approval_status','first_response_due_by_time'," \
                           "'created_by','priority','due_by_time','template','department'," \
                           "'display_id','description','completed_time','has_attachments'," \
                           "'requester','technician','mode','sla','udf_fields']," % from_value

        query_for_email = "'field':'requester.email_id'," \
                          "'condition':'is'," \
                          "'values':['%s']," \
                          "'logical_operator': 'AND'," \
                          "'children':[{'field':'status.in_progress','condition': 'is','value': 'true'," \
                          "'logical_operator': 'AND'}]}]}}" % query

        query_for_group = "'field':'group.name','condition':'is','values':%s}]}}" % str(query)

        if '@' in query:
            search_criteria = query_for_email
        else:
            search_criteria = query_for_group

        # Query values go in this json structure
        query_string = {
            "input_data": query_first_part + "'search_criteria':[{" + search_criteria
        }

        # Header information
        headers = {
            'Accept': "application/vnd.manageengine.sdp.v3+json",
            'Authorization': auth.hdt_token()
        }
        return url, query_string, headers

    @staticmethod
    def fetch_from_helpdesk(url, querystring, headers, attempts=3):
        """ Makes the actual call to the help desk server.
        :param attempts: Number of attempts before giving up.
        :param url: Send in the base url for the REST Call
        :param querystring:
        :param headers:
        :return: Return a data frame of the
        """
        try:
            wait(1)
            # Create the request and capture the response.
            response = requests.request("GET", url, headers=headers, params=querystring)

            # print response.url
            # Load the response to the request as a json object.
            helpdesk_tickets = json.loads(response.text.encode(encoding='utf-8'))
        except AttributeError:
            attempts -= 1
            error_result = "Unexpected error 2: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])

            print error_result
            # print helpdesk_tickets["operation"]
            wait(3)
            if attempts >= 0:
                helpdesk_tickets = HelpdeskConnection.fetch_from_helpdesk(url, querystring, headers, attempts=attempts)
                return helpdesk_tickets
        except requests.exceptions.ConnectionError:
            attempts -= 1
            print attempts
            error_result = "Unexpected error 3: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])

            print error_result
            wait(3)
            if attempts >= 0:
                helpdesk_tickets = HelpdeskConnection.fetch_from_helpdesk(url, querystring, headers, attempts=attempts)

                return helpdesk_tickets

        # print(json.dumps(helpdesk_tickets["operation"]["Details"], indent=4))
        try:
            return helpdesk_tickets["requests"], helpdesk_tickets['list_info']
        except KeyError:
            print response
            # print(json.dumps(helpdesk_tickets["operation"], indent=4))
            # print type(helpdesk_tickets["operation"]["result"])
            try:
                return helpdesk_tickets["list_info"]
            except KeyError:
                return helpdesk_tickets["response_status"]
        except:
            error_result = "Unexpected error 1: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
            print error_result
            # print helpdesk_tickets["operation"]
            wait(2)
            # helpdesk_tickets = HelpdeskConnection.fetch_from_helpdesk(url, querystring, headers)

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
