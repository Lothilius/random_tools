# coding: utf-8
__author__ = 'Lothilius'

import sys

from bv_authenticate.Authentication import Authentication as auth
from send_email.OutlookConnection import OutlookConnection as outlook
from tableau_data_publisher.data_assembler import TDEAssembler
from tableau_data_publisher.data_publisher import publish_data
from triage_tickets.TicketList import TicketList
from helper_scripts.notify_helpers import Notifier
from datetime import timedelta
import pandas as pd
import os
from os import environ
from os.path import basename
from datetime import datetime
from time import time


if os.environ['MY_ENVIRONMENT'] == 'prod':
    file_path = '/var/shared_folder/EUS/Tableau_data/'
else:
    file_path = '/Users/%s/Downloads/' % environ['USER']

extract_name = 'EUS_HDT'
last_record_file = file_path + extract_name + '_last_data_row_pickle'

attempts = 1
give_notice = Notifier()

def gather_tickets():
        # for i in range(attempts):
        # TODO - Fix the retry mechanism
        # try:
        #     # Check for last processed ticket ID
        #     last_data_record = pd.read_pickle(last_record_file)
        #
        #     time_since_last_extract = datetime.now() - last_data_record['Extract_Timestamp'].iloc[0].to_pydatetime()
        #     if time_since_last_extract < timedelta(hours=24):
        #         last_record_id = int(last_data_record['WORKORDERID'].iloc[0])
        #     else:
        #         last_record_id = 0
        #         # os.remove(last_record_file)
        #     break
        # except:
        #     last_record_id = 0
        # print last_record_id

        # try:
            # Get tickets from the HDT view
        tickets = TicketList(helpdesk_que='YtoD-EUS', with_resolution=True)
        tickets = tickets.reformat_as_dataframe(tickets)
        try:
            tickets.drop('ATTACHMENTS', axis=1, inplace=True)
        except:
            print 'No Attachments column.'
        return tickets

        # except:
        #     raise Exception


def main():
    try:
        tickets = gather_tickets()

        # Package in to a tde file
        data_file = TDEAssembler(data_frame=tickets, file_path=file_path, extract_name=extract_name)
        # Set values for publishing the data.
        file_name = str(data_file)
        server_url, username, password, site_id, data_source_name, project = \
            auth.tableau_publishing(datasource_type='EUS', data_source_name='EUS-Helpdesk-Tickets')

        publish_data(server_url, username, password, site_id, file_name, data_source_name, project, replace_data=True)
        outlook().send_email(to='BizAppsIntegrations@bazaarvoice.com',
                             subject='EUS-HDT-Data update complete', body='EUS-HDT-Data update complete')

    except:
        error_result = "Unexpected AttributeError: %s, %s"\
                       % (sys.exc_info()[0], sys.exc_info()[1])
        subject = 'Error with Tableau refresh script, %s' % basename(__file__)
        for each in sys.exc_info():
            print each
        outlook().send_email('helpdesk@bazaarvoice.com', cc='BizAppsIntegrations@bazaarvoice.com', subject=subject, body=error_result)
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
