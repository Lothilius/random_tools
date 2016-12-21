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
    def bv_credentials():
        username = '%s@bazaarvoice.com' % environ['USER']
        password = environ['MY_PW']

        return username, password

    @staticmethod
    def tableau__credentials():
        username = environ['USER']
        password = environ['MY_PW']

        return username, password

    @staticmethod
    def smtp_login():
        username, password = Authentication.bv_credentials()

        return username, password

    @staticmethod
    def hdt_token():
        helpdesk_token = environ['HDT_TOKEN']

        return helpdesk_token

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
    def tableau_publishing(datasource_type='HDT'):
        server_url = 'https://tableau.bazaarvoice.com/'
        project = 'Business Applications'
        site_id = 'BizTech'
        if datasource_type == 'HDT':
            # Set values for publishing the data.
            username, password = Authentication.tableau__credentials()
            if environ['MY_ENVIRONMENT'] == 'prod':
                data_source_name = 'Helpdesk-Tickets'
            else:
                data_source_name = 'HDT-test'


        return server_url, username, password, site_id, data_source_name, project

    @staticmethod
    def hue_bridge():
        hue_ip = environ['HUE_IP']
        hue_token = environ['HUE_TOKEN']

        return hue_ip, hue_token