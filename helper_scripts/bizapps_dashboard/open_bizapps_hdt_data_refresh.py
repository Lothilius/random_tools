# coding: utf-8
__author__ = 'Lothilius'

import sys

from bv_authenticate.Authentication import Authentication as auth
from send_email.OutlookConnection import OutlookConnection as outlook
from tableau_data_publisher.data_assembler import TDEAssembler
from tableau_data_publisher.data_publisher import publish_data
from triage_tickets.TicketList import TicketList
from helper_scripts.notify_helpers import Notifier
from time import time
from os import remove
from os.path import basename
from datetime import datetime


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

        # Get tickets from the HDT view
        tickets = TicketList(helpdesk_que='Hourly-Open-Tickets-do-not-edit', with_resolution=True)
        tickets = tickets.reformat_as_dataframe(tickets)
        try:
            tickets.drop('ATTACHMENTS', axis=1, inplace=True)
        except:
            print 'No Attachments column.'

        backlog_levels(len(tickets))
        # Package in to a tde file
        data_file = TDEAssembler(data_frame=tickets, extract_name='BizApps_Open_HDT')
        # Set values for publishing the data.
        file_name = str(data_file)
        server_url, username, password, site_id, data_source_name, project = \
            auth.tableau_publishing(datasource_type='BizApps', data_source_name='BizApps_Open_HDTs')

        publish_data(server_url, username, password, site_id, file_name, data_source_name, project, replace_data=True)
        # outlook().send_email(to='BizAppsIntegrations@bazaarvoice.com',
        #                      subject='HDT-Open ticket refresh to Tableau complete',
        #                      body='HDT-Open ticket refresh to Tableau complete')
        remove(file_name)

    except KeyboardInterrupt:
        pass
    except:
        error_result = "Unexpected AttributeError: %s, %s"\
                       % (sys.exc_info()[0], sys.exc_info()[1])
        subject = 'Error with Hourly Tableau refresh script, %s' % basename(__file__)
        print error_result
        outlook().send_email(to='helpdesk@bazaarvoice.com', cc='BizAppsIntegrations@bazaarvoice.com',
                             subject=subject, body=error_result)
        give_notice.set_error_light()
        give_notice.wait(3)
        give_notice.flow_the_light()

if __name__ == '__main__':
    start = time()
    main()
    end = time()
    print (end - start)/60
    print datetime.now()
    print '-----------------'
