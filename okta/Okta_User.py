__author__ = 'Lothilius'

import requests
import json
from okta.Okta_Connection import Okta_Connection as okta_connect
from bv_authenticate.Authentication import Authentication as auth
from send_email.OutlookConnection import OutlookConnection as outlook
import smtplib
import sys
import pandas as pd

pd.set_option('display.width', 340)
pd.set_option('display.max_columns', 50)

class Okta_User(object):
    """ User list from Okta. When called, list of user are retrieved from Okta in a panda dataframe.
        """

    def __init__(self, user_id='', query=''):
        """ Creation of instance of Okta user
        :param user_id: Should be in the format of 'app/<id>'
        """
        if query != '' and '?' not in query:
            query = '?' + query
        self.primary_object = 'users/' + user_id + query
        self.raw_user = None
        self.user = self.create_panda(self.primary_object)

    def __str__(self):
        return str(self.user)

    def create_panda(self, primary_object):
        self.raw_user = okta_connect(primary_object=primary_object, limit=500, filter='').fetch_from_okta()
        print self.raw_user
        # users_profile_list = pd.read_json(path_or_buf=json.dumps(self.raw_user), encoding='str', orient='columns')
        # users_profile_list json.dumps([reponse_headers], indent=4, sort_keys=True)
        try:

            self.user = pd.DataFrame([self.raw_user])
            self.user = pd.DataFrame(self.user['profile'].tolist()).join(self.user)

            return self.user
        except Exception, e:
            print e
            return pd.DataFrame()

    def okta_users(self):
        return self.user

    @staticmethod
    def get_email_from_okta_id(query=''):
        if query != '':
            query = '?q=' + query
        user_data = Okta_User(query=query)
        if user_data == []:
            return 'User Not found'
        try:
            if len(user_data.user['id']) == 1:
                return user_data.user['id'][0]
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
    user = Okta_User(user_id='00u10jnv36zOZECFCYHB')
    # reduced_user_info = user[['lastName', 'firstName', 'employeeID', 'email', 'businessTitle', 'managerUserName',
    #                           'supervisoryOrg', 'accountType']]

    print user