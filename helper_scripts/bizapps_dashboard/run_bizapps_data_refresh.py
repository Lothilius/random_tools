__author__ = 'Lothilius'

from triage_tickets.TicketList import TicketList
from tableau_data_publisher.data_assembler import TDEAssembler
from bv_authenticate.Authentication import Authentication as auth
from tableau_data_publisher.data_publisher import publish_data
import sys
from send_email.OutlookConnection import OutlookConnection as outlook


try:
    # Get tickets from the HDT view
    tickets = TicketList(helpdesk_que='YtoD-BizApps')
    tickets = tickets.reformat_as_dataframe(tickets)

    # Package in to a tde file
    data_file = TDEAssembler(data_frame=tickets, file_path='/Users/martin.valenzuela/Desktop/', extract_name='testing')

    # Set values for publishing the data.
    server_url = 'https://tableau.bazaarvoice.com/'
    username, password = auth.tableau__credentials()
    site_id = 'BizTech'
    file_name = str(data_file)
    data_source_name = 'HDT-test'
    project = 'Business Applications'
    publish_data(server_url, username, password, site_id, file_name, data_source_name, project, replace_data=True)

# print server_url,
# print data_source_name
except:
    error_result = "Unexpected AttributeError: %s, %s"\
                   % (sys.exc_info()[0], sys.exc_info()[1])
    subject = 'Error with Tableau refresh script'
    print tickets
    print error_result
    outlook.send_email('helpdesk@bazaarvoice.com', cc='martin.valenzuela@bazaarvoice.com', subject=subject, body=error_result)