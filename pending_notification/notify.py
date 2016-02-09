#!/usr/bin/env python
# coding: utf-8

__author__ = 'Lothilius'

from bv_tools.triage_tickets.TicketList import TicketList
from bv_tools.triage_tickets.Ticket import Ticket
from bv_tools.send_email.OutlookConnection import OutlookConnection as outlook
import pandas as pd
import sys

reload(sys)
sys.setdefaultencoding('utf8')


low_priority_message = """Please be aware that, due to capacity constraints on our team (Business Applications), we aren't able to respond to low priority issues at this time."""


try:
    # Get list of filters of list views in Helpdesk
    filters = pd.DataFrame(TicketList.get_filter_list())
    holding_pool_id = filters[filters.VIEWNAME == 'Holding Pool - Pending Assignment'].VIEWID.iloc[0]

    # Get list of helpdesk tickets using the holding pool list view.
    tickets = TicketList(holding_pool_id)
    tickets = TicketList.reformat_as_dataframe(tickets)
    reply_messages_sent = []

    # Cycle through each ticket
    for each in tickets.WORKORDERID:
        try:
            # Get ticket detail of particular ticket
            ticket = Ticket(each)

            # Get List of conversations for ticket
            conversations = TicketList.reformat_as_dataframe(ticket.get_conversations())
            ticket_as_df = TicketList.reformat_as_dataframe([ticket.details])

            # Separate replies form the conversation
            replyies = conversations[conversations.TYPE == 'REPLY']
            present = 0

            # Check if one of the replies has was a low priority reply.
            for each in replyies.CONVERSATIONID:
                conversations_details = ticket.get_conversation_detail(each)
                conversations_details = TicketList.reformat_as_dataframe(conversations_details)
                reply_message = conversations_details.DESCRIPTION.iloc[0]
                if low_priority_message in reply_message:
                    present = 1

            # If no low priority replies where found send a low priority message to ticket requester
            if present == 0:
                ticket.send_priority_reply()
                reply_messages_sent.append("Reply sent for %s" % ticket.hdt_id)

            # print 'done'
        except:
            error_result = "Unexpected error 2: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
            subject = 'Error with pending notification ' + ticket.hdt_id
            print subject
            print error_result
            print '\n'
            outlook.send_email('helpdesk@bazaarvoice.com', cc='martin.valenzuela@bazaarvoice.com', subject=subject, body=error_result)

    # Send a confirmation email to Martin that the tickets were reviewed and the messages were sent
    subject = 'Low priority Messages Sent: %s sent out of %s' % (len(reply_messages_sent), len(tickets.WORKORDERID))
    reply_messages_sent = '\n'.join(reply_messages_sent)

    outlook.send_email('martin.valenzuela@bazaarvoice.com', cc='daniel.parkhurst@bazaarvoice.com', subject=subject, body=reply_messages_sent)

except:
    error_result = "Unexpected error 1: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
    subject = 'Error with pending notification'
    print error_result
    outlook.send_email('helpdesk@bazaarvoice.com', cc='martin.valenzuela@bazaarvoice.com', subject=subject, body=error_result)