__author__ = 'Lothilius'

from os import environ

class Authentication(object):
    @staticmethod
    def okta_authentication():
        url = 'https://bazaarvoice.okta.com/api/v1/events?'
        api_key = environ['OKTA_KEY']
        headers = {
        'accept': "application/json",
        'content-type': "application/json",
        'cache-control': "no-cache",
        'authorization': "SSWS " + api_key,
        'postman-token': "trs8GxmAQxBT2axefZFA98xig"
        }
        return url, headers

    @staticmethod
    def smtp_login():
        username = '%s@bazaarvoice.com' % environ['USER']
        password = environ['MY_PW']

        return username, password

    @staticmethod
    def hdt_token():
        helpdesk_token = environ['HDT_TOKEN']

        return helpdesk_token

    @staticmethod
    def sfdc_login(environment='staging'):
        if environment == 'prod':
            username = '%s@bazaarvoice.com' % environ['ME']
            password = environ['MY_PW']
            token = environ['MY_TOKEN']
            sandbox = False
        else:
            username = '%s@bazaarvoice.com.staging' % environ['ME']
            password = environ['SFDC_PW']
            token = environ['SFDC_STAGING_TOKEN']
            sandbox = True

        return username, password, token, sandbox
