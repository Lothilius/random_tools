__author__ = 'Lothilius'

from sfdc.SFDC_Connection import SFDC_Connection
from sfdc.SFDC_Users import SFDC_Users
from helper_scripts.misc_helpers.data_manipulation import create_feature_vector_dataframe
import pandas as pd
from okta.Okta_Application import Okta_Application
from helper_scripts.notify_helpers import Notifier
import collections


class SFDC_Platform_Users(SFDC_Users):
    def get_user_list(self, user_type='PowerCustomerSuccess'):
        """ Get Active Portal user list from Salesforce.
        :return: panda Dataframe of the user with the Username as the Email!!! ---Warning----
        """
        sf = SFDC_Connection.connect_to_SFDC('prod')
        results = sf.query_all("SELECT Id, Username, Email, Name, Employee_ID__c, Role__c, LastLoginDate, UserType, "
                               "Account.Name, Profile.Name, isActive  FROM User "
                               "Where UserType = '%s' AND isActive = true" % user_type)
        results_panda = self.flaten_dictionary(results_od=results['records'])
        results_panda.rename(columns={'Id': 'UserId', 'Name': 'Profile_Name', 'Email': 'true_email',
                                      'Username': 'Email', }, inplace=True)

        return results_panda

    @staticmethod
    def flaten_dictionary(results_od):
        """ Create a flat dictionary that can be converted in to a Pandas Dataframe. Removes junk from Salesforce.
        :param results_od: Ordered dict of the results from Salesforce
        :return: a flattened dictionary of the reasults_od data
        """
        data = {}
        # print results_od
        for each in results_od:
            # print each
            del each['attributes']
            del each['Profile']['attributes']
            del each['Account']['attributes']
            each['Account'] = each['Account'].pop('Name')
            each['UserName'] = each.pop('Name')
            for k, v in each.items():
                # print type(k), k, v
                if type(v) == collections.OrderedDict:
                    for l, m in v.items():
                        data.setdefault(l, []).append(m)
                else:
                    data.setdefault(k, []).append(v)
        flat_df = pd.DataFrame.from_dict(data)
        return flat_df



if __name__ == '__main__':
    this_thing = SFDC_Platform_Users('PowerCustomerSuccess')
    print this_thing
    this_thing.users.to_csv('/Users/martin.valenzuela/Downloads/portal_users.csv')