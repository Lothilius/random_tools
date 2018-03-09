__author__ = 'Lothilius'

import pandas as pd
from sfdc.SFDC_Connection import SFDC_Connection
from helper_scripts.misc_helpers.data_manipulation import create_feature_vector_dataframe
import collections

pd.set_option('display.width', 195)


class SFDC_Package_Licenses(object):
    """ Package_License from SFDC. When called, package licenses are retrieved from SFDC in a panda dataframe.
    """
    def __init__(self):
        self.package_licence_key = ''
        self.licenses = self.get_license_vector()

    def __str__(self):
        return str(self.licenses)

    def licenses(self):
        return self.licenses

    def get_license_list(self):
        sf = SFDC_Connection.connect_to_SFDC('prod')
        results = sf.query_all("SELECT PackageLicenseId,PackageLicense.NamespacePrefix,UserId FROM UserPackageLicense")

        # Flatten the results from nested ordered dicts and convert to pandas dataframe
        results_panda = self.flaten_dictionary(results['records'])
        final_panda = results_panda.fillna(value='na', inplace=False)

        self.set_permission_key_df(final_panda[['NamespacePrefix', 'PackageLicenseId']])

        return final_panda

    def set_permission_key_df(self, package_licence):
        """ The the license key parameter with the licenses in use with their Id's
        :param package_licence: Dataframe
        :return: None
        """
        df_group = package_licence.groupby(by=['NamespacePrefix', 'PackageLicenseId'], as_index=False).size()
        df = pd.DataFrame(df_group, columns=['Count']).reset_index()
        df.drop(labels=['Count'], axis=1, inplace=True)

        self.package_licence_key = pd.DataFrame(data=[df['PackageLicenseId'].tolist()],
                                               columns=df['NamespacePrefix'].tolist())

    @staticmethod
    def get_package_licence_key():
        permissions = SFDC_Package_Licenses()
        return permissions.package_licence_key

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
        license_vector_dataframe = create_feature_vector_dataframe(user_list, 'UserId', 'NamespacePrefix', suffix='_lic')

        return license_vector_dataframe

if __name__ == '__main__':
    print SFDC_Package_Licenses().get_package_licence_key()