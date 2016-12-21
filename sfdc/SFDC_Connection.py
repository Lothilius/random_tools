__author__ = 'Lothilius'

import requests
import json
from bv_authenticate.Authentication import Authentication as auth
import sys
import pandas as pd
from simple_salesforce import Salesforce

pd.set_option('display.width', 160)

class SFDC_Connection(object):
    """ Salesforce connector that help create the sf connection and the query.
    """
    @staticmethod
    def connect_to_SFDC(environment='prod'):
        """ Create the main SFDC connecting object.
        :param environment: the SFDC environment you wish to access
        :return: salesforce connection object using simple salesforce.
        """
        user_name, pw, token, sandbox = auth.sfdc_login(environment)
        sf = Salesforce(username=user_name, password=pw, security_token=token, sandbox=sandbox)

        return sf

    @staticmethod
    def build_query(sf_object='Case', type='01250000000Hnex', status='In Progress', sub_status='', technician='',
                    columns=''):
        if 'biz' in columns:
            columns = '%s' % ('RecordTypeId,Status,ClosedDate,OwnerId,CreatedDate,Requestor__c,Release_Date_Change_Reason__c,Release_Target__c, Release_Actual__c,Release_Month__c,Project_Type__c, Case_Type__c, Department_Requesting__c, Estimated_Hours_To_Complete__c,SOX_Approval_Status__c, Approved_Date__c, Testing_Status_Pre_Prod__c, SOX_Post_Mortem_Review__c,Project__c, Requirement_Name__c, Work_Package_Name__c, Release_Date__c, Helpdesk_ID__c, Sub_Status__c,UAT_Status__c, UAT_Date__c, UAT_Tester_s_Name__c, SOX_Requirement__c')
        elif columns == '':
            columns = 'Id'

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

        if type == '':
            pass
        else:
            type = " WHERE RecordTypeId =  '%s'" % type

        # print columns
        query = "Select %s FROM %s " \
                "%s%s%s%s" % (columns, sf_object, type, status, sub_status, technician)

        return query

    def get_count(self, result):
        return result['totalSize']