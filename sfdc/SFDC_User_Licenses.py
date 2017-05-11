__author__ = 'Lothilius'

import pandas as pd
from sfdc.SFDC import SFDC
from helper_scripts.misc_helpers.data_manipulation import create_feature_vector_dataframe
import collections


class SFDC_Package_Licenses(object):
    """ Package_License from SFDC. When called, package licenses are retrieved from SFDC in a panda dataframe.
    """
    def __init__(self):
        self.licenses = self.get_license_vector()

    def __str__(self):
        return str(self.licenses)

    def licenses(self):
        return self.licenses

    def get_license_list(self):
        sf = SFDC.connect_to_SFDC('prod')
        results = sf.query_all("SELECT Id,PackageLicense.NamespacePrefix,UserId FROM UserPackageLicense")

        # Flatten the results from nested ordered dicts and convert to pandas dataframe
        results_panda = self.flaten_dictionary(results['records'])
        results_panda.fillna(value='na', inplace=True)

        return results_panda

    @staticmethod
    def flaten_dictionary(results_od):
        """ Create a flat dictionary that can be converted in to a Pandas Dataframe. Removes junk from Salesforce.
        :param results_od: Ordered dict of the results from Salesforce
        :return: a flattened dictionary of the reasults_od data
        """
        data = {}
        for each in results_od:
            del each['attributes']
            del each['PackageLicense']['attributes']
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

    def get_license_vector(self):
        user_list = self.get_license_list()
        license_vector_dataframe = create_feature_vector_dataframe(user_list, 'UserId', 'NamespacePrefix')

        return license_vector_dataframe

if __name__ == '__main__':
    print SFDC_Package_Licenses()