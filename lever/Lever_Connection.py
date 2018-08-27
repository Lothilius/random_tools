# -*- coding: utf-8 -*-
__author__ = 'Lothilius'

import requests
import json
from bv_authenticate.Authentication import Authentication as auth
import time
import sys
import traceback

def wait(seconds=5.0):
    time.sleep(seconds)

class LeverConnection(object):
    @staticmethod
    def create_api_request(object='requisitions', offset='', record_id='', **kwargs):
        """ Create the api request for Lever. At the moment very minimal
            but can be expanded in the future for creating more specific and different types of requests.
        :param object: This is the object name from the lever api
        :param offset: Sets the beginning value in the list returned
        :param record_id: Defines a specific id to retrieve on ly that record.
        :return: string of the URL, dict of the query, and a dict of the header
        """
        if record_id != '':
            record_id = '/' + record_id

        # Main Lever api URL
        url = "https://api.lever.co/v1/%s%s" % (object, record_id)

        querystring = {"includedeactivated": "true", "limit": "100"}

        if offset != '':
            # Query values go in this json structure
            querystring['offset'] = offset
        else:
            pass

        for key, value in kwargs.iteritems():
            querystring[key] = value

        # Header information
        headers = {
            'authorization': "Basic %s" % auth.lever_token(),
            'cache-control': "no-cache",
        }
        return url, querystring, headers

    @staticmethod
    def fetch_from_lever(url, querystring, headers):
        """ Makes the actual call to the help desk server.
        :param url: Send in the base url for the REST Call
        :param querystring:
        :param headers:
        :return: Return a data frame of the
        """
        try:
            wait(.11)
            # print querystring
            # Create the request and capture the response.
            response = requests.request("GET", url, headers=headers, params=querystring)
            # print response.status_code
            # print response.url
            # print response.content
            # print type(response.text)
            # print "before"

            # Load the response to the request as a json object.
            lever_records = json.loads(response.text.encode(encoding='utf-8', errors="replace"))

            # print "after"
            # print(json.dumps(lever_records, indent=4))
            # print lever_records['next']
        # except ValueError:
        #     exc_type, exc_value, exc_traceback = sys.exc_info()
        #     traceback.print_exception(exc_type, exc_value, exc_traceback)
        #     error_result = "Unexpected Error: %s, %s, %s" \
        #                    % (exc_type, exc_value, traceback.format_exc())
        #     print error_result
        #     print querystring
        #     print response.content
            # wait(2)
            # LeverConnection.fetch_from_helpdesk(url, querystring, headers)
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            error_result = "Unexpected Error: %s, %s, %s" \
                           % (exc_type, exc_value, traceback.format_exc())
            print error_result
            print querystring
            print response.content
            if response.status_code != 200:
                wait(3)
                print "Encountered error code: %s - %s" % (response.status_code, error_result)
                response.close()
                lever_records = LeverConnection.fetch_from_lever(url, querystring, headers)

        # print(json.dumps(lever_records["operation"]["Details"], indent=4))
        try:
            response.close()
            return lever_records
        except:
            error_result = "Unexpected error 1: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
            print error_result
            # wait(2)
            # LeverConnection.fetch_from_helpdesk(url, querystring, headers)


if __name__ == '__main__':
    reqs = LeverConnection()
    url, query, header = reqs.create_api_request(updated_at_start='1520002556')
    reqs.fetch_from_lever(url, query, header)