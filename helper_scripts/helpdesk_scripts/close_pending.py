__author__ = 'Lothilius'

from triage_tickets.TicketList import TicketList, Ticket
import pandas as pd

if __name__ == '__main__':
    # try:
    # Get the view ID for the pending view HD
    pending_view__id = TicketList.get_view_id('Pending')
    print pending_view__id
    # Retrieve the list of tickets from the view
    ticket_list = TicketList(helpdesk_que=pending_view__id)
    # print ticket_list[0]
    ticket_list = TicketList.reformat_as_dataframe(ticket_list)
    # print ticket_list
    # ticket_list.columns
    for each in ticket_list.WORKORDERID.tolist():
        result = Ticket.set_status(each, status='Resolved')
        try:
            print result['STATUS'] + '\n'
        except KeyError:
            print result['status'] + '\n'
        # print Ticket.set_status(each)
    # except: