__author__ = 'Lothilius'
# coding: utf-8

import json
import requests
from bv_authenticate.Authentication import Authentication as auth

class Okta_Connection(object):
    """ Salesforce connector that help create the sf connection and the query.
    """
    def __init__(self, primary_object='', query=''):
        self.headers = auth.okta_authentication()
        self.primary_object = primary_object
        self.query = query
        self.api_url = 'https://bazaarvoice.okta.com/api/v1/' + self.primary_object + '?'

    def get_url(self):
        return self.api_url

    def set_primary_object(self, object):
        self.primary_object = object
        self.api_url = 'https://bazaarvoice.okta.com/api/v1/' + self.primary_object + '?'

    def set_query(self, query):
        self.query = query

    def query_okta(self):
        """ Create the main Okta connecting object.
        :return: Okta query result as json object.
        """
        # Send the request
        response = requests.request("GET", url=self.api_url, headers=self.headers, params=self.query)
        # Place response in to a json object
        okta_json = json.loads(response.text)

        return okta_json

