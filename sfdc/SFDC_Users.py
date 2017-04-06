__author__ = 'Lothilius'

from sfdc.SFDC import SFDC
import pandas as pd

pd.set_option('display.width', 340)

class SFDC_Users(object):
    """ Users from SFDC. When called, active internal users are retrieved from SFDC in a panda dataframe.
    """
    def __init__(self):
        self.users = self.get_user_list()

    def __str__(self):
        return str(self.users)

    def users_list(self):
        return self.users

    @staticmethod
    def get_user_list():
        sf = SFDC.connect_to_SFDC('prod')
        results = sf.query_all("SELECT Id, Email, Name, Employee_ID__c, Role__c  FROM User Where isActive=true "
                               "AND UserType = 'Standard'")
        result_list = []

        for each in results['records']:
            result_list.append([each['Id'], each['Email'], each['Name'],
                                each['Employee_ID__c'], each['Role__c'], each['Title']])
        results_panda = pd.DataFrame(result_list, columns=['Id', 'Email', 'Name', 'Employee_ID__c', 'Role__c'])

        return results_panda

if __name__ == '__main__':
    the_list = SFDC_Users()
    hello = the_list.users_list()
    print hello