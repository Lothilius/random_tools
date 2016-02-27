__author__ = 'Lothilius'

import requests
import json
from bv_authenticate.Authentication import Authentication as auth
import sys
from bv_status.Status import Status
from simple_salesforce import Salesforce


class SFDC(Status):
    """ Extend Status class for Helpdesk.
    """

    def get_status(self):
        # Get SFDC Status from Status page.
        sfdc = requests.get("http://trust.salesforce.com/trust/instances/NA3")
        sfdc_reply = sfdc.content
        status = "This instance is available and fully functional." in sfdc_reply
        if status:
            return 1
        else:
            return 0

    def get_error(self):
        #     TODO - Parse site for the error message.
        pass

    def aggregate_tickets(self, ticket_list_a, ticket_list_b):
        """ Join to lists of helpdesk tickets.

        :param ticket_list_a: list
        :param ticket_list_b: list
        :return: list - helpdesk_tickets
        """
        helpdesk_tickets = ticket_list_a + ticket_list_b

        return helpdesk_tickets

    @staticmethod
    def build_query(sf_object='Case', type='01250000000Hnex', status='In Progress', sub_status='', technician=''):
        if technician == '':
            pass
        else:
            technician = " And OwnerId = '%s'" % technician

        if status == '':
            pass
        else:
            status = " And Status = '%s'" % status

        if sub_status == '':
            pass
        else:
            sub_status = " And Sub_Status__c = '%s'" % sub_status

        query = "SELECT Id FROM %s " \
                "WHERE RecordTypeId = '%s' " \
                "'%s'%s%s" % (sf_object, type, status, sub_status, technician)

        return query

    def get_count(self, result):
        return result['totalSize']

    @staticmethod
    def get_sfdc_data(environment='staging',
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
    def connect_to_SFDC(environment='staging'):
        user_name, pw, token, sandbox = auth.sfdc_login(environment)
        sf = Salesforce(username=user_name, password=pw, security_token=token, sandbox=sandbox)

        return sf

    def get_all_tickets(self):
        try:
            cases = self.get_sfdc_data(environment='prod')
            number_of_cases = self.get_count(cases)
            self.set_status(self.get_status())
            self.set_status_message('Functioning normally')
            self.set_error_message('No Error Reported.')

            return number_of_cases
        except:
            error_result = "Unexpected error 1: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
            self.set_error_message(error_result)

            return -1


if __name__ == '__main__':
    status = SFDC()
    print status
