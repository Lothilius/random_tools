__author__ = 'Lothilius'

from os import environ
from requests_aws4auth import AWS4Auth

class Authentication(object):
    @staticmethod
    def okta_authentication():
        api_key = environ['OKTA_KEY']
        headers = {
        'accept': "application/json",
        'content-type': "application/json",
        'cache-control': "no-cache",
        'authorization': "SSWS " + api_key,
        'postman-token': "trs8GxmAQxBT2axefZFA98xig"
        }
        return headers

    @staticmethod
    def bv_credentials():
        username = '%s@bazaarvoice.com' % environ['USER']
        password = environ['MY_PW']

        return username, password

    @staticmethod
    def spark_credentials(environment=environ['ENVIRONMENT']):
        username = '%s@bazaarvoice.com' % environ['SPARK_USER']
        if environment == 'prod':
            password = environ['SPARK_PW']
        else:
            password = environ['SPARK_STAGING_PW']

        return username, password

    @staticmethod
    def tableau__credentials():
        username = environ['USER']
        password = environ['MY_PW']

        return username, password

    @staticmethod
    def smtp_login(account=''):
        # if account == '':
        #     username, password = Authentication.bv_credentials()
        # else:
        username = 'helpdesk@bazaarvoice.com'
        password = environ['HD_EMAIL_PW']


        return username, password

    @staticmethod
    def hdt_token():
        helpdesk_token = environ['HDT_TOKEN']

        return helpdesk_token

    @staticmethod
    def lever_token():
        lever_token = environ['LEVER_TOKEN']

        return lever_token

    @staticmethod
    def sfdc_login(environment='staging'):
        if environment == 'prod':
            username, password = Authentication.bv_credentials()
            token = environ['MY_TOKEN']
            sandbox = False
        elif environment == 'media':
            username, password = Authentication.bv_credentials()
            token = environ['MY_TOKEN']
            sandbox = False
        else:
            username = '%s@bazaarvoice.com.staging' % environ['ME']
            password = environ['MY_PW_STAGING']
            token = environ['SFDC_STAGING_TOKEN']
            sandbox = True
        return username, password, token, sandbox


    @staticmethod
    def tableau_publishing(env=environ['MY_ENVIRONMENT'], url=''):
        """ Method prodives the data needed to publish a data source to the Tableau server.
        :return: server_url, username, password,
        """
        username, password = Authentication.tableau__credentials()
        # TODO -- Re do this part it's dumb
        if url != '' and env != 'prod':
            server_url = url
        elif env == 'prod':
            server_url = 'https://tableau.bazaarvoice.com/'
        else:
            server_url = 'https://tableauserver.bazaarvoice.com/'

        return server_url, username, password

    @staticmethod
    def hue_bridge():
        hue_ip = environ['HUE_IP']
        hue_token = environ['HUE_TOKEN']

        return hue_ip, hue_token

    @staticmethod
    def aws_connect():
        aws_connector = AWS4Auth(environ['AWS_ACCESS_KEY'], environ['AWS_SECRET_KEY'], 'us-east-1', 'es')

        return aws_connector