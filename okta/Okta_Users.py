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
        primary_object = 'apps/' + app_id + '/users/'
        self.users = self.create_panda(primary_object)

    def __str__(self):
        return str(self.users)

    def create_panda(self, primary_object):
        users = okta_connect(primary_object=primary_object, limit=1000, filter='accountType eq \"EMPLOYEE\"').fetch_from_okta()
        print users
        users_profile_list = pd.read_json(path_or_buf=json.dumps(users), encoding='str')
        print json.dumps(users_profile_list, indent=4, sort_keys=True)
        self.users = pd.DataFrame(list(users_profile_list['profile']))
        return self.users

    def okta_users(self):
        return self.users


if __name__ == '__main__':
    print Okta_Users(app_id='0oada9tueRHDXFSYNVMT').users
