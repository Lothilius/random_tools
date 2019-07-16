# coding: utf-8
__author__ = 'Lothilius'

import sys

from send_email.OutlookConnection import OutlookConnection as outlook
from triage_tickets.TicketList import TicketList
from triage_tickets.TicketList import Ticket
from tableau_data_publisher.data_assembler_hyper import HyperAssembler
from helper_scripts.notify_helpers import Notifier
from tableau_data_publisher.Tableau import Tableau
from os import environ
from os.path import basename
from datetime import datetime
from time import time
from os import remove
import socket


if environ['MY_ENVIRONMENT'] == 'prod':
    file_path = '/var/shared_folder/BizApps/Tableau_data/'
    project = 'Business Applications'
else:
    file_path = '/Users/%s/Downloads/' % environ['USER']
    project = 'Testing'
    # file_path = 'Testing/BizApps/Tableau_data/'

extract_name = 'BizApps_Open_HDT'
data_source_name = 'BizApps_Open_HDT'

give_notice = Notifier()


def backlog_levels(backlog_number):
    give_notice.alert_the_light()
    if backlog_number < 75:
        give_notice.set_green()
    elif 75 <= backlog_number < 85:
        give_notice.set_yellow()
    elif backlog_number >= 85:
        give_notice.set_red()
    else:
        raise ValueError(backlog_number)


def main():
    try:

        # Get tickets for BizApps queues
        tickets = TicketList(version=3, query=["BizApps - Triage", "BizApps - Integrations", "BizApps - Technical"],
                             count_only=False, open_only=True)
        backlog_levels(tickets.total_count)

        tickets = tickets.reformat_as_dataframe(tickets)
        try:
            tickets.drop('ATTACHMENTS', axis=1, inplace=True)
        except:
            print 'No Attachments column.'

        # Package in to a hyper file
        data_file = HyperAssembler(data_frame=tickets, extract_name=extract_name, file_path=file_path)
        # Set values for publishing the data.
        file_name = str(data_file)
        tableau_server = Tableau(server_url='https://tableau.bazaarvoice.com/', site_id='BizTech')
        tableau_server.publish_datasource(project=project,
                                          file_path=file_name,
                                          mode='Append', name=data_source_name)

        outlook().send_email(to='BizAppsIntegrations@bazaarvoice.com',
                             subject='HDT-Open ticket refresh to Tableau complete',
                             body='HDT-Open ticket refresh to Tableau complete')
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
    print (end - start)/60
    print datetime.now()
    print '-----------------'
