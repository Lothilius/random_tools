# coding: utf-8
__author__ = 'Lothilius'

from SFDC_Connection import SFDC_Connection
from SFDC_User_Licenses import SFDC_Package_Licenses
from SFDC_Permission_Sets import SFDC_Permission_Sets
import pandas as pd
import collections

pd.set_option('display.width', 195)

class SFDC_Users(object):
    """ Users from SFDC. When called, active internal user are retrieved from SFDC in a panda dataframe.
    """
    def __init__(self, user_type='Standard', include_licenses=False, include_permissions=False):
        self.users = self.get_user_list(user_type)
        self.licenses = ''
        self.permissions = ''
        if include_licenses:
            self.include_licenses()
        if include_permissions:
            self.include_permissions()

    def __str__(self):

        return str(self.users)

    def users_list(self):
        return self.users

    def get_user_list(self, user_type='Standard'):
        """ Get Active standard user list from Salesforce.
        :return: panda Dataframe of the user with the Username as the Email!!! ---Warning----
        """
        sf = SFDC_Connection.connect_to_SFDC('prod')
        results = sf.query_all("SELECT Id, Username, Email, Name, Employee_ID__c, Role__c, Profile.Name, ForecastEnabled, "
                               "UserPermissionsKnowledgeUser, UserPermissionsLiveAgentUser, "
                               "UserPermissionsMarketingUser, UserPermissionsSFContentUser, "
                               "UserPermissionsSupportUser, isActive  FROM User Where UserType = '%s'" % user_type)
        results_panda = self.flaten_dictionary(results_od=results['records'])
        results_panda.rename(columns={'Id': 'UserId', 'Name': 'Profile_Name', 'Email': 'true_email',
                                      'Username': 'Email', }, inplace=True)

        return results_panda

    def include_licenses(self):
        self.licenses = SFDC_Package_Licenses()

    def include_permissions(self):
        self.permissions = SFDC_Permission_Sets()

    def users_with_licenses(self):
        users_with_license_vector = \
            self.users.merge(self.licenses.licenses, left_on='UserId', right_on='UserId',
                             suffixes=['_user', '_license'], how='left')
        users_with_license_vector.fillna(value='na', inplace=True)
        return users_with_license_vector

    def users_with_licenses_permissions(self):
        users_with_license__vector = self.users_with_licenses()
        users_with_license_permissions_vector = \
            users_with_license__vector.merge(self.permissions.permission_sets, left_on='UserId', right_on='UserId',
                             suffixes=['_user', '_license'], how='left')
        users_with_license_permissions_vector.fillna(value='na', inplace=True)

        return users_with_license_permissions_vector

    @staticmethod
    def flaten_dictionary(results_od):
        """ Create a flat dictionary that can be converted in to a Pandas Dataframe. Removes junk from Salesforce.
        :param results_od: Ordered dict of the results from Salesforce
        :return: a flattened dictionary of the reasults_od data
        """
        data = {}
        for each in results_od:
            del each['attributes']
            del each['Profile']['attributes']
            each['UserName'] = each.pop('Name')
            for k, v in each.items():
                # print type(k), v
                if type(v) == collections.OrderedDict:
                    for l, m in v.items():
                        data.setdefault(l, []).append(m)
                else:
                    data.setdefault(k, []).append(v)
        flat_df = pd.DataFrame.from_dict(data)
        return flat_df

if __name__ == '__main__':
    the_list = SFDC_Users()
    hello = the_list.users
    print hello