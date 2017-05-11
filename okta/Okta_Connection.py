__author__ = 'Lothilius'
# coding: utf-8

import json
import requests
from bv_authenticate.Authentication import Authentication as auth
import pandas as pd

pd.set_option('display.width', 260)

class Okta_Connection(object):
    """ Okta connector that help create the okta connection and the query.
    """
    def __init__(self, primary_object='', limit='100', filter='status eq \"ACTIVE\"'):
        self.headers = auth.okta_authentication()
        self.primary_object = primary_object
        self.query = {"limit": limit,
                      "filter": filter}
        if self.query['filter'] == '':
            del self.query['filter']
        self.api_url = 'https://bazaarvoice.okta.com/api/v1/' + self.primary_object

    def get_url(self):
        return self.api_url

    def set_primary_object(self, object):
        self.primary_object = object
        self.api_url = 'https://bazaarvoice.okta.com/api/v1/' + self.primary_object

    def set_query(self, query):
        self.query = query

    def fetch_from_okta(self):
        """ Create the main Okta connecting object.
        :return: Okta query result as json object.
        """
        # Send the request
        response = requests.request("GET", url=self.api_url, headers=self.headers, params=self.query)
        print response.url
        # Place response in to a json object
        okta_json = json.loads(response.text)
        # print okta_json[11]['profile']
        # print json.dumps(okta_json, indent=4, sort_keys=True)
        return okta_json

if __name__ == '__main__':
    okta_title = Okta_Connection(primary_object='apps', limit='200')
    print pd.read_json(path_or_buf=json.dumps(okta_title.fetch_from_okta()), encoding='str')
