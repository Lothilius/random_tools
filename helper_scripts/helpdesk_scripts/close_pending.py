__author__ = 'Lothilius'

from triage_tickets.TicketList import TicketList, Ticket
import sys

if __name__ == '__main__':
    try:
        # Retrieve the list of tickets from the view
        ticket_list = TicketList(helpdesk_que='Pending')
        ticket_list = TicketList.reformat_as_dataframe(ticket_list)

        # Work through the list and set the status to Resolved for each ticket.
        for each in ticket_list.WORKORDERID.tolist():
            result = Ticket.set_status(each, status='Resolved')
            try:
                print result['STATUS'] + '\n'
            except KeyError:
                print result['status'] + '\n'
            # print Ticket.set_status(each)
    except:
        error_result = "Unexpected error 1CP: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
        print error_result
