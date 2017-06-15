__author__ = 'Lothilius'


import requests
import json
from Okta_Connection import Okta_Connection as okta_connect
from Okta_Users import Okta_Users as okta_users
from bv_authenticate.Authentication import Authentication as auth
from send_email.OutlookConnection import OutlookConnection as outlook
import smtplib
import sys
import pandas as pd

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
                apps_list= okta_connect(primary_object, limit=200, filter='').fetch_from_okta()
                id_label_list = pd.read_json(path_or_buf=json.dumps(apps_list), encoding='str')[['id', 'label']]
                apps_id_label = id_label_list[id_label_list['label'].str.lower() == app_name.lower()]
                primary_object = primary_object + str(apps_id_label.id.iloc[0])
                return primary_object
        except:
            error_result = "Unexpected error 1TL: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
            print error_result



if __name__ == '__main__':
    workday = Okta_Application(app_name='workday')
    print workday.app_users