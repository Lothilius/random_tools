# coding: utf-8
__author__ = 'Lothilius'

import sys

from bv_authenticate.Authentication import Authentication as auth
from send_email.OutlookConnection import OutlookConnection as outlook
from tableau_data_publisher.data_assembler import TDEAssembler
from tableau_data_publisher.data_publisher import publish_data
from triage_tickets.TicketList import TicketList
from time import time
from os import remove

def main():
    try:

        # Get tickets from the HDT view
        tickets = TicketList(helpdesk_que='Hourly-Open-Tickets-do-not-edit', with_resolution=True)
        tickets = tickets.reformat_as_dataframe(tickets)
        try:
            tickets.drop('ATTACHMENTS', axis=1, inplace=True)
        except:
            print 'No Attachments column.'

        # Package in to a tde file
        data_file = TDEAssembler(data_frame=tickets, extract_name='BizApps_Open_HDT')
        # Set values for publishing the data.
        file_name = str(data_file)
        server_url, username, password, site_id, data_source_name, project = \
            auth.tableau_publishing(datasource_type='BizTech', data_source_name='BizApps_Open_HDTs')

        publish_data(server_url, username, password, site_id, file_name, data_source_name, project, replace_data=True)
        # outlook.send_email(to='martin.valenzuela@bazaarvoice.com',
        # subject='HDT-Hourly update complete', body='HDT-Hourly update complete')
        remove(file_name)

    except ValueError:
        error_result = "Unexpected AttributeError: %s, %s"\
                       % (sys.exc_info()[0], sys.exc_info()[1])
        subject = 'Error with Hourly Tableau refresh script'
        print error_result
        outlook.send_email('helpdesk@bazaarvoice.com', cc='martin.valenzuela@bazaarvoice.com', subject=subject, body=error_result)


if __name__ == '__main__':
    start = time()
    main()
    end = time()
    print (end - start)/60