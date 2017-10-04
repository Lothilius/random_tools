# coding: utf-8
__author__ = 'Lothilius'

import sys

from bv_authenticate.Authentication import Authentication as auth
from send_email.OutlookConnection import OutlookConnection as outlook
from tableau_data_publisher.data_assembler import TDEAssembler
from tableau_data_publisher.data_publisher import publish_data
from helper_scripts.notify_helpers import Notifier
from okta.Okta_Application import Okta_Application
from os import remove
from os.path import basename
from time import time
from datetime import datetime



def main():
    try:
        # Get Users from Okta for Workday
        workday = Okta_Application(app_name='workday')
        employees = workday.app_users

        # Package in to a tde file
        data_file = TDEAssembler(data_frame=employees, extract_name='Workday_Employee_data')
        # Set values for publishing the data.
        file_name = str(data_file)
        server_url, username, password, site_id, data_source_name, project = \
            auth.tableau_publishing(datasource_type='BizApps', data_source_name='Workday_Employee_data')

        publish_data(server_url, username, password, site_id, file_name, data_source_name, project, replace_data=True)
        outlook().send_email(to='BizAppsIntegrations@bazaarvoice.com',
                           subject='Workday_User_data compiling complete', body='Workday_User_data compiling complete')


    except KeyboardInterrupt:
        pass
    except:
        error_result = "Unexpected AttributeError: %s, %s"\
                       % (sys.exc_info()[0], sys.exc_info()[1])
        subject = 'Error with Tableau refresh script, %s' % basename(__file__)
        print error_result
        outlook().send_email('helpdesk@bazaarvoice.com', cc='BizAppsIntegrations@bazaarvoice.com',
                             subject=subject, body=error_result)
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