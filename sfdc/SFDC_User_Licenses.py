__author__ = 'Lothilius'

import pandas as pd
from sfdc.SFDC import SFDC
from sfdc.SFDC_Users import SFDC_Users


class SFDC_Package_License(SFDC_Users):
    """ Package_License from SFDC. When called, package licenses are retrieved from SFDC in a panda dataframe.
    """
    def __int__(self):
        self.licenses = self.get_license_list()

    def __str__(self):
        return str(self.licenses)

    def licenses(self):
        return self.licenses

    @staticmethod
    def get_license_list():
        sf = SFDC.connect_to_SFDC('prod')
        results = sf.query_all("SELECT Id,PackageLicenseId,UserId FROM UserPackageLicense")
        result_list = []

        for each in results['records']:
            result_list.append([each['Id'], each['PackageLicenseId'], each['UserId']])
        results_panda = pd.DataFrame(result_list, columns=['Id', 'PackageLicenseId', 'UserId'])

        return results_panda
