# coding: utf-8
__author__ = 'Lothilius'

from SFDC_Connection import SFDC_Connection
from SFDC_User_Licenses import SFDC_Package_Licenses
from SFDC_Permission_Sets import SFDC_Permission_Sets
import pandas as pd
import collections

pd.set_option('display.width', 295)
# ToDo - Everything!!!!!!
class SFDC_Holidays(object):
    """ Users from SFDC. When called, active internal user are retrieved from SFDC in a panda dataframe.
    """
    def __init__(self):
        self.holidays = self.get_holiday_list()

    def __str__(self):

        return str(self.holidays)

    def users_list(self):
        return self.users

    def get_holiday_list(self):
        """ Get Active standard user list from Salesforce.
        :return: panda Dataframe of the user with the Username as the Email!!! ---Warning----
        """
        sf = SFDC_Connection.connect_to_SFDC('prod')
        results = sf.query_all("SELECT Id, Description, LastModifiedDate,Name,RecurrenceDayOfMonth,"
                               "RecurrenceDayOfWeekMask,RecurrenceInstance,RecurrenceMonthOfYear,RecurrenceStartDate,"
                               "RecurrenceType,ActivityDate,CreatedDate FROM Holiday")
        results_panda = self.flaten_dictionary(results_od=results['records'])

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
            each['HolidayName'] = each.pop('Name')
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
    the_list = SFDC_Holidays()
    print the_list
    # hello.to_csv('/Users/martin.valenzuela/Downloads/employees_with_license_and_perm_sets.csv', index=False, encoding="utf-8")
