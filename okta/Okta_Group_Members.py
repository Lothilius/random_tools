__author__ = 'Lothilius'

import requests
import json
from okta.Okta_Connection import Okta_Connection as okta_connect
from okta.Okta_Users import Okta_Users as okta_user
from helper_scripts.misc_helpers.data_manipulation import create_feature_dataframe
from bv_authenticate.Authentication import Authentication as auth
from send_email.OutlookConnection import OutlookConnection as outlook
import smtplib
import sys
import pandas as pd


class Okta_Group_Members(object):
    """ Group list from Okta. When called, list of groups are retrieved from Okta in a panda dataframe.
        """

    def __init__(self, group_id='00gcy0wldkSLIQJLRDDU', query=''):
        """ Creation of instance of Okta users
        :param app_id: Should be in the format of 'app/<id>'
        """
        if query != '' and '?' not in query:
            query = '?q=' + query
            self.primary_object = 'groups' + query
            self.groups = self.create_panda(self.primary_object)
        elif group_id != '':
            self.primary_object = 'groups/' + group_id + '/users'
            self.group_members = self.create_panda(self.primary_object)

    def __str__(self):
        return str(self.group_members)

    @staticmethod
    def get_groups(query=''):
        if query != '':
            query = '?q=' + query
        user_data = Okta_Group_Members(query=query)

        try:
            return user_data.group_members['id'][0]
        except Exception, e:
            return e

    def add_user_to_group(self, user_email, user_id=''):
        """Provide the user id(s) or user email(s) to add to the group.

        :param user_id: Tuple of Alpha numeric ids for Okta user objects.
        :param user_email: Tuple of Emails
        :return:
        """
        try:
            if user_id == '':
                user_value = okta_user.get_okta_id_from_email(user_email)
            else:
                user_value = user_id

            add_to_group_url = self.primary_object + '/' + str(user_value)
            result = okta_connect(primary_object=add_to_group_url, limit='', filter='').fetch_from_okta(query_type='PUT')
        except Exception, e:
            result = e
        return result


    def create_panda(self, primary_object):
        users = okta_connect(primary_object=primary_object, limit=500, filter='').fetch_from_okta()
        users_profile_list = pd.read_json(path_or_buf=json.dumps(users), encoding='str')
        if users_profile_list.empty:
            group_response = users_profile_list
        else:
            group_response = pd.DataFrame(users_profile_list[['profile', 'id']])
            group_response = create_feature_dataframe(group_response, 'id', 'profile')

        return group_response

    def okta_users(self):
        return self.group_members


if __name__ == '__main__':
    user = Okta_Group_Members(query='WD-Active')
    # data = pd.read_csv("/Users/martin.valenzuela/Downloads/mfa-users.csv")
    print user.group_members