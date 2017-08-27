# coding: utf-8
__author__ = 'Lothilius'

import sys

from bv_authenticate.Authentication import Authentication as auth
from send_email.OutlookConnection import OutlookConnection as outlook
from tableau_data_publisher.data_assembler import TDEAssembler
from tableau_data_publisher.data_publisher import publish_data
from triage_tickets.TicketList import TicketList
from helper_scripts.notify_helpers import Notifier
from sfdc.SFDC_Users import SFDC_Users
from os import remove
from os.path import basename


try:
    # Get tickets from the HDT view
    the_list = SFDC_Users(include_licenses=True, include_permissions=True)
    tickets = the_list.users_with_licenses_permissions()
    # print tickets

    # Package in to a tde file
    data_file = TDEAssembler(data_frame=tickets, extract_name='SFDC_User_data')
    # Set values for publishing the data.
    file_name = str(data_file)
    server_url, username, password, site_id, data_source_name, project = \
        auth.tableau_publishing(datasource_type='BizApps', data_source_name='SFDC_User_Permissions')

    publish_data(server_url, username, password, site_id, file_name, data_source_name, project, replace_data=True)
    outlook().send_email(to='martin.valenzuela@bazaarvoice.com',
                       subject='SFDC_User_data compiling complete', body='SFDC_User_data compiling complete')

    remove(file_name)

except:
    error_result = "Unexpected AttributeError: %s, %s"\
                   % (sys.exc_info()[0], sys.exc_info()[1])
    subject = 'Error with Tableau refresh script, %s' % basename(__file__)
    print error_result
    outlook().send_email('helpdesk@bazaarvoice.com', cc='martin.valenzuela@bazaarvoice.com', subject=subject, body=error_result)
    give_notice = Notifier()
    give_notice.set_red()
    give_notice.wait(120)
    give_notice.flow_the_light()