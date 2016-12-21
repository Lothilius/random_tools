__author__ = 'Lothilius'

import requests
import json
from sfdc.SFDCConnection import SFDCConnection as sfdc_connect
import sys
import pandas as pd
from simple_salesforce import Salesforce

pd.set_option('display.width', 160)

class SFDCCases(object):
    """ Extend Status class fot Salesforce.
    """
    def __init__(self):
        self.cases = self.get_bizreq_cases()

    def __getitem__(self, item):
        return self.tickets[item]

    def __str__(self):
        return str(self.tickets)

    def get_count(self, result):
        return result['totalSize']

    @staticmethod
    def get_sfdc_data(environment='staging', columns='biz'):
        """ Get Salesforce tickets for the respective que 100 at a time.
        :return: OrderedDict that contains totalsize, done, and records. Records in turn is also given as an
                OrderedDict with the actualrecords data.
        """
        sf = sfdc_connect.connect_to_SFDC(environment='prod')
        result = sf.query_all(sfdc_connect.build_query(columns=columns))

        return result


    def get_bizreq_cases(self):
        try:
            cases = self.get_sfdc_data()

            case_list = pd.DataFrame(cases["records"])
            case_list.drop('attributes', axis=1, inplace=True)
            return case_list
        except:
            error_result = "Unexpected error 1: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
            print error_result

            return -1


if __name__ == '__main__':
    sfdc = SFDCCases()
    case_list = sfdc.get_bizreq_cases()
    print case_list