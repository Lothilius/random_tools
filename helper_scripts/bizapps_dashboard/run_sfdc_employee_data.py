# coding: utf-8
__author__ = 'Lothilius'

import sys
from bv_authenticate.Authentication import Authentication as auth
from send_email.OutlookConnection import OutlookConnection as outlook
from tableau_data_publisher.Tableau import Tableau
from triage_tickets.Ticket import Ticket
from tableau_data_publisher.data_assembler_hyper import HyperAssembler
from helper_scripts.notify_helpers import Notifier
from sfdc.SFDC_Users import SFDC_Users
from os import remove
from os.path import basename
from datetime import datetime
from time import time
import socket
from os import environ



if environ['MY_ENVIRONMENT'] == 'prod':
    file_path = '/var/shared_folder/BizApps/Tableau_data/'
    project = 'Business Applications'
else:
    file_path = '/Users/%s/Downloads/' % environ['USER']
    project = 'Testing'
    # file_path = 'Testing/BizApps/Tableau_data/'

extract_name = 'SFDC_User_Permissions'
data_source_name = 'SFDC_User_Permissions'

give_notice = Notifier()

def main():
    try:
        # Get SFDC_users from the Salesforcewith permissions and licenses
        the_list = SFDC_Users(include_licenses=True, include_permissions=True)
        sfdc_users = the_list.users_with_licenses_permissions()

        # Package in to a hyper file
        data_file = HyperAssembler(data_frame=sfdc_users, extract_name=extract_name, file_path=file_path)
        # Set values for publishing the data.
        file_name = str(data_file)
        tableau_server = Tableau(server_url='https://tableau.bazaarvoice.com/', site_id='BizTech')
        tableau_server.publish_datasource(project=project,
                                          file_path=file_name,
                                          mode='Append', name=data_source_name)

        # data_file = TDEAssembler(data_frame=sfdc_users, extract_name='SFDC_User_data')

        # server_url, username, password, site_id, data_source_name, project = \
        #     auth.tableau_publishing(datasource_type='BizApps', data_source_name='SFDC_User_Permissions')
        #
        # # Publish to BizTech
        # publish_data(server_url, username, password, site_id, file_name, data_source_name, project, replace_data=True)
        # # Publish to the Default Tableau page.
        # publish_data(server_url, username, password, '', file_name,
        #              'SFDC_User_Permissions', 'Default', replace_data=True)

        outlook().send_email(to='BizAppsIntegrations@bazaarvoice.com',
                           subject='SFDC_User_data compiling complete', body='SFDC_User_data compiling complete')

        remove(file_name)

    except KeyboardInterrupt:
        pass
    except:
        error_result = "Unexpected AttributeError: %s, %s" \
                       % (sys.exc_info()[0], sys.exc_info()[1])
        subject = 'Error with Tableau refresh script, %s on Server %s' % (basename(__file__), socket.gethostname())
        error_result += subject
        print error_result
        try:
            data = {'REQUESTEREMAIL': 'martin.valenzuela@bazaarvoice.com',
                    'REQUESTER': 'Martin Valenzuela',
                    'DESCRIPTION': error_result,
                    'SUBJECT': subject}
            Ticket().create_ticket(data)
        except:
            outlook().send_email('helpdesk@bazaarvoice.com', cc='BizAppsIntegrations@bazaarvoice.com', subject=subject,
                                 body=error_result)
        give_notice = Notifier()
        give_notice.set_red()
        give_notice.wait(30)
        give_notice.flow_the_light()


if __name__ == '__main__':
    start = time()
    main()
    end = time()
    print (end - start) / 60
    print datetime.now()
    print '-----------------'
