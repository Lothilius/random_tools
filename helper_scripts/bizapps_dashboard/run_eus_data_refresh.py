# coding: utf-8
__author__ = 'Lothilius'

import sys

from send_email.OutlookConnection import OutlookConnection as outlook
from tableau_data_publisher.data_assembler import TDEAssembler
from triage_tickets.TicketList import TicketList
from triage_tickets.TicketList import Ticket
from helper_scripts.notify_helpers import Notifier
from tableau_data_publisher.Tableau import Tableau
from os import environ
from os.path import basename
from datetime import datetime
from time import time
import socket



if environ['MY_ENVIRONMENT'] == 'prod':
    file_path = '/var/shared_folder/EUS/Tableau_data/'
else:
    file_path = '/Users/%s/Downloads/' % environ['USER']
    # file_path = 'Testing/BizApps/Tableau_data/'

extract_name = 'Escalations_HDT'

give_notice = Notifier()


def main():
    try:
        # Get tickets for BizApps queues
        tickets = TicketList(version=3, query=["IT Escalations"],
                             count_only=False)
        tickets = tickets.reformat_as_dataframe(tickets)
        try:
            tickets.drop('ATTACHMENTS', axis=1, inplace=True)
        except:
            print 'No Attachments column.'

        tickets = tickets[['CATEGORY', 'COMPLETEDTIME', 'CREATEDBY', 'CREATEDTIME',
                           'DELETED_TIME', 'DEPARTMENT', 'DUEBYTIME', 'GROUP', 'HASATTACHMENTS',
                           'HASCONVERSATION', 'HASNOTES', 'ISPENDING', 'ITEM', 'LEVEL',
                           'LONG_REQUESTID', 'MODE', 'PRIORITY', 'REQUESTER', 'REQUESTEREMAIL',
                           'REQUESTTEMPLATE', 'RESOLUTION', 'RESOLUTIONLASTUPDATEDTIME', 'RESOLVER',
                           'RESPONDEDTIME', 'SHORTDESCRIPTION',
                           'SITE', 'SLA', 'STATUS', 'STOPTIMER', 'SUBCATEGORY', 'SUBJECT', 'TECHNICIAN',
                           'TEMPLATEID', 'TIMESPENTONREQ', 'Department_Group', 'System Component',
                           'System', 'WORKORDERID']].copy()

        # Package in to a tde file
        data_file = TDEAssembler(data_frame=tickets, file_path=file_path, extract_name=extract_name)
        # Set values for publishing the data.
        file_name = str(data_file)
        tableau_server = Tableau(server_url='https://tableau.bazaarvoice.com/', site_id='BizTech')
        tableau_server.publish_datasource(project='Testing',
                                          file_path=file_name,
                                          mode='CreateNew', name='EUS-Helpdesk-Tickets')
        # server_url, username, password, site_id, data_source_name, project = \
        #     auth.tableau_publishing(datasource_type='EUS', data_source_name='EUS-Helpdesk-Tickets')
        #
        # publish_data(server_url, username, password, site_id, file_name, data_source_name, project, replace_data=True)
        # outlook().send_email(to='BizAppsIntegrations@bazaarvoice.com',
        #                      subject='EUS-HDT-Data update complete', body='EUS-HDT-Data update complete')

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
