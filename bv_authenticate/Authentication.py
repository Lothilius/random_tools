__author__ = 'Lothilius'

from os import environ

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
    def tableau_publishing(datasource_type='BizTech', data_source_name='New_Extract'):
        """ Method prodives the data needed to publish a data source to the Tableau server.
        :param datasource_type: The department that will be using the data source
        :param data_source_name:
        :return:
        """
        server_url = 'https://tableau.bazaarvoice.com/'
        if datasource_type == 'BizTech':
            project = 'Business Applications'
            site_id = 'BizTech'
            # Set values for publishing the data.
            username, password = Authentication.tableau__credentials()
            # TODO - Move most of this trash to the publish data module
            if environ['MY_ENVIRONMENT'] == 'prod' and data_source_name == 'Helpdesk-Tickets':
                data_source_name = 'Helpdesk-Tickets'
            elif environ['MY_ENVIRONMENT'] == 'prod' and data_source_name != 'New_Extract':
                pass
            else:
                data_source_name = 'BizTech-test'
        else:
            # Set values for publishing the data.
            username, password = Authentication.tableau__credentials()
            project = ''
            site_id = ''

        return server_url, username, password, site_id, data_source_name, project

    @staticmethod
    def hue_bridge():
        hue_ip = environ['HUE_IP']
        hue_token = environ['HUE_TOKEN']

        return hue_ip, hue_token