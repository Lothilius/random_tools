# coding: utf-8
__author__ = 'Lothilius'

from SFDC_Connection import SFDC_Connection
from SFDC_User_Licenses import SFDC_Package_Licenses
from SFDC_Permission_Sets import SFDC_Permission_Sets
import pandas as pd
import collections

pd.set_option('display.width', 195)

class SFDC_Contacts(object):
    """ Contacts from SFDC. When called, active internal contacts are retrieved from SFDC in a panda dataframe.
    """
    def __init__(self, contact_type='Standard', include_licenses=False, include_permissions=False):
        self.contacts = self.get_contact_list(contact_type)
        self.licenses = ''
        self.permissions = ''
        if include_licenses:
            self.include_licenses()
        if include_permissions:
            self.include_permissions()

    def __str__(self):

        return str(self.contacts)

    def contacts_list(self):
        return self.contacts

    def get_contact_list(self, contact_type='Standard'):
        """ Get Active standard contact list from Salesforce.
        :return: panda Dataframe of the contacts with the Contactname as the Email!!! ---Warning----
        """
        sf = SFDC_Connection.connect_to_SFDC('prod')
        results = sf.query_all("SELECT Id,Email,FirstName,Full_Name__c,LastName,CreatedDate "
                               "FROM Contact "
                               "WHERE Email LIKE '%@bazaarvoice.com%'")
        results_panda = self.flaten_dictionary(results_od=results['records'])
        results_panda.rename(columns={'Id': 'ContactId', 'Name': 'Profile_Name', 'Email': 'true_email',
                                      'Contactname': 'Email', }, inplace=True)

        return results_panda

    def include_licenses(self):
        self.licenses = SFDC_Package_Licenses()

    def include_permissions(self):
        self.permissions = SFDC_Permission_Sets()

    def contacts_with_licenses(self):
        contacts_with_license_vector = \
            self.contacts.merge(self.licenses.licenses, left_on='ContactId', right_on='ContactId',
                             suffixes=['_contact', '_license'], how='left')
        contacts_with_license_vector.fillna(value='na', inplace=True)
        return contacts_with_license_vector

    def contacts_with_licenses_permissions(self):
        contacts_with_license__vector = self.contacts_with_licenses()
        contacts_with_license_permissions_vector = \
            contacts_with_license__vector.merge(self.permissions.permission_sets, left_on='ContactId', right_on='ContactId',
                             suffixes=['_contact', '_license'], how='left')
        contacts_with_license_permissions_vector.fillna(value='na', inplace=True)

        return contacts_with_license_permissions_vector

    @staticmethod
    def flaten_dictionary(results_od):
        """ Create a flat dictionary that can be converted in to a Pandas Dataframe. Removes junk from Salesforce.
        :param results_od: Ordered dict of the results from Salesforce
        :return: a flattened dictionary of the reasults_od data
        """
        data = {}
        for each in results_od:
            del each['attributes']
            each['ContactName'] = each.pop('Full_Name__c')
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
    the_list = SFDC_Contacts()
    hello = the_list.contacts
    print hello