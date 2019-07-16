# coding: utf-8
__author__ = 'Lothilius'

import sys

from bv_authenticate.Authentication import Authentication as auth
from send_email.OutlookConnection import OutlookConnection as outlook
from tableau_data_publisher.data_assembler_hyper import HyperAssembler
from tableau_data_publisher.Tableau import Tableau
from helper_scripts.notify_helpers import Notifier
from okta.Okta_Application import Okta_Application
from triage_tickets.Ticket import Ticket
from os import remove
from os.path import basename
from time import time
import socket
from os import environ
from datetime import datetime


if environ['MY_ENVIRONMENT'] == 'prod':
    file_path = '/var/shared_folder/BizTech/Tableau_data/'
    project = 'Default'
else:
    file_path = '/Users/%s/Downloads/' % environ['USER']
    project = 'Testing'
    # file_path = 'Testing/BizApps/Tableau_data/'

extract_name = 'SFDC_User_Permissions'
data_source_name = 'Workday_Employee_data'

def main():
    try:
        # Get Users from Okta for Workday
        workday = Okta_Application(app_name='workday')
        employees = workday.app_users

        # Package in to a hyper file
        data_file = HyperAssembler(data_frame=employees, extract_name=extract_name, file_path=file_path)
        # Set values for publishing the data.
        file_name = str(data_file)
        tableau_server = Tableau(server_url='https://tableau.bazaarvoice.com/', site_id='BizTech')
        tableau_server.publish_datasource(project=project,
                                          file_path=file_name,
                                          mode='Append', name=data_source_name)

        remove(file_name)

        outlook().send_email(to='BizAppsIntegrations@bazaarvoice.com',
                             subject='Workday_User_data compiling complete', body='Workday_User_data compiling complete')


    except KeyboardInterrupt:
        pass
    except:
        error_result = 'Unexpected AttributeError: %s, %s' \
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
    print (end - start)/60
    print datetime.now()