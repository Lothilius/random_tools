__author__ = 'Lothilius'

import requests
import json
from okta.Okta_Connection import Okta_Connection as okta_connect
from bv_authenticate.Authentication import Authentication as auth
from send_email.OutlookConnection import OutlookConnection as outlook
import smtplib
import sys
import pandas as pd


class Okta_Users(object):
    """ User list from Okta. When called, list of user are retrieved from Okta in a panda dataframe.
        """

    def __init__(self, app_id='', query=''):
        """ Creation of instance of Okta user
        :param app_id: Should be in the format of 'app/<id>'
        """
        if query != '' and '?' not in query:
            query = '?' + query
        self.primary_object = app_id + '/users' + query
        self.raw_users = None
        self.users = self.create_panda(self.primary_object)

    def __str__(self):
        return str(self.users)

    def create_panda(self, primary_object):
        users = okta_connect(primary_object=primary_object, limit=500, filter='').fetch_from_okta()
        users_profile_list = pd.read_json(path_or_buf=json.dumps(users), encoding='str')
        # print json.dumps([reponse_headers], indent=4, sort_keys=True)
        self.raw_users = users_profile_list
        try:
            okta_id = pd.DataFrame(self.raw_users['id'])
            okta_status = pd.DataFrame(self.raw_users['status'])


            self.users = pd.DataFrame(users_profile_list['profile'].tolist()).join(okta_id)
            self.users = self.users.join(okta_status)
            try:
                okta_credentials = pd.DataFrame(self.raw_users['credentials'].tolist())
                self.users = self.users.join(okta_credentials)
            except:
                pass

            return self.users
        except Exception, e:
            print e
            return pd.DataFrame()

    def okta_users(self):
        return self.users

    @staticmethod
    def get_okta_id_from_email(query=''):
        if query != '':
            query = '?q=' + query
        user_data = Okta_Users(query=query)
        if user_data == []:
            return 'User Not found'
        try:
            if len(user_data.users['id']) == 1:
                return user_data.users['id'][0]
            else:
                raise Exception("More than one user ID found with same Email.")
        except Exception, e:
            return e

    @staticmethod
    def deactivate_user(user_id):
        try:
            if '@' in user_id:
                    user_id = Okta_Users.get_okta_id_from_email(query=user_id)
            else:
                user_id = user_id
            primary_object = 'user/' + user_id + '/lifecycle/deactivate'
            return okta_connect(primary_object=primary_object, limit='', filter='').fetch_from_okta(query_type='POST')
        except Exception, e:
            return e


if __name__ == '__main__':
    user = Okta_Users.get_okta_id_from_email(query='martin.valenzuela@bazaarvoice.com')
    # reduced_user_info = user[['lastName', 'firstName', 'employeeID', 'email', 'businessTitle', 'managerUserName',
    #                           'supervisoryOrg', 'accountType']]

    print user