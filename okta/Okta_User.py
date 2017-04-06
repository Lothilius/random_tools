__author__ = 'Lothilius'


import requests
import json
from bv_authenticate.Authentication import Authentication as auth
from send_email.OutlookConnection import OutlookConnection as outlook
import smtplib
import sys
import pandas as pd

class Okta_User(object):
    """ User list from Okta. When called, list of users are retrieved from Okta in a panda dataframe.
        """

    def __init__(self):
        self.licenses = self.get_license_list()

    def __str__(self):
        return str(self.licenses)

    def licenses(self):
        return self.licenses