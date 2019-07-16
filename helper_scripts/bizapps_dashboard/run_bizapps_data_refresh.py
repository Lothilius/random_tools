# coding: utf-8
__author__ = 'Lothilius'

import sys
from send_email.OutlookConnection import OutlookConnection as outlook
from tableau_data_publisher.data_assembler_hyper import HyperAssembler
from tableau_data_publisher.Tableau import Tableau
from triage_tickets.TicketList import TicketList
from triage_tickets.Ticket import Ticket
from helper_scripts.notify_helpers import Notifier
from os.path import basename
from datetime import datetime
from time import time
from os import environ
import socket


if environ['MY_ENVIRONMENT'] == 'prod':
    file_path = '/var/shared_folder/BizApps/Tableau_data/'
    project = 'Business Applications'
else:
    file_path = '/Users/%s/Downloads/' % environ['USER']
    project = 'Testing'
    # file_path = 'Testing/BizApps/Tableau_data/'

extract_name = 'BizApps_HDT'
data_source_name = 'Helpdesk-Tickets'

give_notice = Notifier()

def main():
    try:
        # Get tickets for BizApps queues
        tickets = TicketList(version=3, query=["BizApps - Triage", "BizApps - Integrations", "BizApps - Technical"],
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


        # Package in to a hyper file
        data_file = HyperAssembler(data_frame=tickets, extract_name=extract_name, file_path=file_path)
        # Set values for publishing the data.
        file_name = str(data_file)
        tableau_server = Tableau(server_url='https://tableau.bazaarvoice.com/', site_id='BizTech')
        tableau_server.publish_datasource(project=project,
                                          file_path=file_name,
                                          mode='Append', name=data_source_name)

        outlook().send_email(to='BizAppsIntegrations@bazaarvoice.com',
                           subject='HDT-Data update complete', body='HDT-Data update complete')

    except:
        error_result = "Unexpected AttributeError: %s, %s"\
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
    print '-----------------\n'