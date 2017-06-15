__author__ = 'Lothilius'

import requests
import json
from Okta_Connection import Okta_Connection as okta_connect
from bv_authenticate.Authentication import Authentication as auth
from send_email.OutlookConnection import OutlookConnection as outlook
import smtplib
import sys
import pandas as pd


class Okta_Users(object):
    """ User list from Okta. When called, list of users are retrieved from Okta in a panda dataframe.
        """

    def __init__(self, app_id=''):
        """ Creation of instance of Okta users
        :param app_id: Should be in the format of 'app/<id>'
        """
        primary_object = app_id + '/users'
        self.users = self.create_panda(primary_object)

    def __str__(self):
        return str(self.users)

    def create_panda(self, primary_object):
        users = okta_connect(primary_object=primary_object, limit=500, filter='').fetch_from_okta()
        users_profile_list = pd.read_json(path_or_buf=json.dumps(users), encoding='str')
        # print json.dumps([reponse_headers], indent=4, sort_keys=True)
        self.users = pd.DataFrame(users_profile_list['profile'].tolist())

        return self.users

    def okta_users(self):
        return self.users


if __name__ == '__main__':
    user = Okta_Users(app_id='apps/0oada9tueRHDXFSYNVMT').users
    reduced_user_info = user[['lastName', 'firstName', 'employeeID', 'email', 'businessTitle', 'managerUserName',
                              'supervisoryOrg', 'accountType']]

    print reduced_user_info