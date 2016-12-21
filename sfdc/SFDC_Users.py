__author__ = 'Lothilius'

from sfdc.SFDC import SFDC
import pandas as pd


class SFDC_Users(object):
    """ Users from SFDC. When called, active internal users are retrieved from SFDC in a panda dataframe.
    """
    def __int__(self):
        self.users = self.get_user_list()

    def __str__(self):
        return str(self.users)

    def users(self):
        return self.users

    @staticmethod
    def get_user_list():
        sf = SFDC.connect_to_SFDC('prod')
        results = sf.query_all("SELECT Id, Email, Name  FROM User Where isActive=true AND UserType = 'Standard'")
        result_list = []

        for each in results['records']:
            result_list.append([each['Id'], each['Email'], each['Name']])
        results_panda = pd.DataFrame(result_list, columns=['Id', 'Email', 'Name'])

        return results_panda

if __name__ == '__main__':
    the_list = SFDC_Users()
    print the_list.users()