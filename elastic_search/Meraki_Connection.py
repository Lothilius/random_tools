__author__ = 'Lothilius'

import requests
import json
from bv_authenticate.Authentication import Authentication as auth
import sys
import pandas as pd
from simple_salesforce import Salesforce
from datetime import datetime
from elasticsearch import Elasticsearch, RequestsHttpConnection

pd.set_option('display.width', 160)

class Elastic_Search_Connection(object):
    """  connector that help create the sf connection and the query.
    """
    @staticmethod
    def connect_to_aws_elastic_search(host, environment='prod'):
        """ Create the main AWS elastic search connecting object.
        :param environment: the AWS environment you wish to access
        :return: aws elastic search object.
        """
        awsauth = auth.aws_connect()
        es = Elasticsearch(
            hosts=[{'host': host, 'port': 443}],
            http_auth=awsauth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection
        )

        return es

    @staticmethod
    def build_query():

        return query

    def get_count(self, result):
        return result['totalSize']