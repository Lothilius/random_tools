__author__ = 'Lothilius'

import csv
from sfdc.SFDC import SFDC
from helper_scripts.misc_helpers.data_manipulation import create_feature_vector_dataframe
import pandas as pd
import collections
import ast


pd.set_option('display.width', 195)

class SFDC_Permission_Sets(object):
    """ Package_License from SFDC. When called, package licenses are retrieved from SFDC in a panda dataframe.
    """
    def __init__(self):
        self.permission_sets = self.get_permission_set_vector()

    def __str__(self):
        return str(self.permission_sets)

    def permission_sets(self):
        return self.permission_sets

    def get_permission_set_list(self):
        # Query SFDc for the assigned permissions sets and names
        sf = SFDC.connect_to_SFDC('prod')
        results = sf.query_all("SELECT AssigneeId,PermissionSet.Id, PermissionSet.Name FROM PermissionSetAssignment")

        # Flatten the results from nested ordered dicts and convert to pandas dataframe
        results_panda = self.flaten_dictionary(results['records'])
        results_panda.fillna(value='na', inplace=True)

        # Rename the columns of the results.
        results_panda.rename(columns={'AssigneeId': 'UserId', 'Id':'Permission_Set_Id', 'Name':'Permission_Set_Name'},
                             inplace=True)
        final_panda = results_panda[~results_panda['Permission_Set_Name'].str.startswith('X')].copy()

        return final_panda

    @staticmethod
    def flaten_dictionary(results_od):
        """ Create a flat dictionary that can be converted in to a Pandas Dataframe. Removes junk from Salesforce.
        :param results_od: Ordered dict of the results from Salesforce
        :return: a flattened dictionary of the reasults_od data
        """
        data = {}
        for each in results_od:
            del each['attributes']
            del each['PermissionSet']['attributes']
            for k, v in each.items():
                # print type(k), v
                if type(v) == collections.OrderedDict:
                    for l, m in v.items():
                        data.setdefault(l, []).append(m)
                else:
                    data.setdefault(k, []).append(v)
        # print data
        flat_df = pd.DataFrame.from_dict(data)
        return flat_df

    def get_permission_set_vector(self):
        user_list = self.get_permission_set_list()
        license_vector_dataframe = create_feature_vector_dataframe(user_list, 'UserId', 'Permission_Set_Name')

        return license_vector_dataframe

if __name__ == '__main__':
    a_thing = SFDC_Permission_Sets()
    print a_thing
