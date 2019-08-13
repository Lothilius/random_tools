__author__ = 'Lothilius'


import requests
import json
from okta.Okta_Connection import Okta_Connection as okta_connect
from okta.Okta_Users import Okta_Users as okta_users
from bv_authenticate.Authentication import Authentication as auth
from send_email.OutlookConnection import OutlookConnection as outlook
import smtplib
import sys
import pandas as pd

pd.set_option('display.width', 260)
pd.set_option('display.max_columns', 20)


class Okta_Application(object):
    """ Application list from Okta. When called, list of applications are retrieved from Okta in a panda dataframe.
        """

    def __init__(self, app_name=''):
        self.primary_object = self.get_app_id(app_name=app_name)
        self.details = okta_connect(primary_object=self.primary_object)
        self.app_users = okta_users(app_id=self.primary_object).users

    def __str__(self):
        return str(self.licenses)

    def licenses(self):
        return self.licenses

    def get_app_id(self, app_name):
        """ Retrieve the app Id given the app name.
        :param app_name: Okta label for the tile
        :return: string of 'apps/<id>/'
        """
        try:
            primary_object = 'apps/'
            if app_name == '':
                return primary_object
            else:
                apps_list = okta_connect(primary_object=primary_object, limit=200).fetch_from_okta()
                id_label_list = pd.read_json(path_or_buf=json.dumps(apps_list), encoding='str')[['id', 'label']]
                apps_id_label = id_label_list[id_label_list['label'].str.lower() == app_name.lower()]
                primary_object = primary_object + str(apps_id_label.id.iloc[0])
                return primary_object
        except:
            error_result = "Unexpected error 1TL: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
            print error_result

    def set_user_name(self, user_id, user_name):
        """ Once an app object is created user name can be set by passing the user id and user name.
        :param user_id: 20 character okta id should be passed as a string.
        :param user_name: New user name for the user id passed in.
        :return: DataFrame of new Profile for App
        """
        primary_object = self.primary_object + '/users/' + user_id
        data = {"credentials": {"userName": user_name}}

        user_app_profile = okta_connect(primary_object=primary_object, limit='', filter='',
                                        data=json.dumps(data)).fetch_from_okta(query_type='POST')
        users_app_profile_df = pd.read_json(path_or_buf=json.dumps(user_app_profile), orient='records', lines=True)

        return users_app_profile_df


if __name__ == '__main__':
    okta_jira_dev2 = Okta_Application(app_name='Jira Dev2 with a vengeance')
    print okta_jira_dev2.app_users
    print okta_jira_dev2.set_user_name(user_id='00u10jnv36zOZECFCYHB', user_name='mvalenzuela_local')
    print 'done'