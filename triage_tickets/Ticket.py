#!/usr/bin/env python
# coding: utf-8
__author__ = 'Lothilius'

from HelpdeskConnection import HelpdeskConnection as hdc
import sys

reload(sys)
sys.setdefaultencoding('utf8')

class Ticket(object):
    def __init__(self, hdt_id):
        self.hdt_id = hdt_id
        self.details = self.get_ticket_details(self.hdt_id)
        self.conversations = ''

    def __getitem__(self, item):
        details = list(dict(self.details))
        return details[item]

    def __str__(self):
        """
        :return: String value of the ticket.
        """
        return str(self.details)

    def get_ticket_details(self, ticket_number):
        """ Retrieve ticket detials for individual ticket.
        :param ticket_number: The workorder id of ticket number of the Ticket
        :return: Dictionary of the ticket details
        """
        url, querystring, headers = hdc.create_api_request()

        url = url + "/" + ticket_number

        querystring['OPERATION_NAME'] = "GET_REQUEST"
        del querystring['INPUT_DATA']
        # print querystring
        helpdesk_ticket_details = hdc.fetch_from_helpdesk(url, querystring, headers)

        return helpdesk_ticket_details

    def get_conversations(self):
        """ Retrieve conversations list for individual ticket.
        :param ticket_number: The workorder id of ticket number of the Ticket
        :return: Dictionary of the ticket details
        """
        url, querystring, headers = hdc.create_api_request()

        url = url + "/" + self.hdt_id + "/conversation"

        querystring['OPERATION_NAME'] = "GET_CONVERSATIONS"
        del querystring['INPUT_DATA']
        # print querystring
        ticket_conversation_details = hdc.fetch_from_helpdesk(url, querystring, headers)

        self.conversations = list(ticket_conversation_details)
        return self.conversations

    def get_conversation_detail(self, conversation_id):
        """ Retrieve conversation detials for an individual ticket.
        :param conversation_id: The workorder id of ticket number of the Ticket
        :return: Dictionary of the ticket details
        """
        url, querystring, headers = hdc.create_api_request()

        url = url + "/" + self.hdt_id + "/conversation/" + conversation_id

        querystring['OPERATION_NAME'] = "GET_CONVERSATION"
        del querystring['INPUT_DATA']
        # print querystring
        ticket_conversation_details = hdc.fetch_from_helpdesk(url, querystring, headers)

        get_conversation_detail = list([ticket_conversation_details])
        return get_conversation_detail

    def send_priority_reply(self):
        """ Send a hard coded reply to a ticket.
        :param requester_email: The workorder id of ticket number of the Ticket
        :return: Dictionary of the ticket details
        """
        requester_first_name = self.details['REQUESTER'].split()[0]
        requester_email = self.details['REQUESTEREMAIL']
        subject = 'Re: [Request ID :##%s##] : ' % self.hdt_id + self.details['SUBJECT']
        reply_message = "Hi %s -<br><br>" \
                        "Thanks for submitting a Helpdesk request. Please be aware that, due to capacity constraints on " \
                        "our team (Business Applications), we aren\\'t able to respond to low priority issues at this time. If you " \
                        "feel that this request has been inaccurately prioritized, please feel free to reply and state " \
                        "the reason you\\'d like to place higher priority on a particular issue and we will definitely " \
                        "review your ticket and consider re-prioritizing." \
                        "<br><br>" \
                        "Apologies in advance for any delays!" \
                        "<br><br>" \
                        "Thanks,<br>" \
                        "BizApps" % requester_first_name
        url, querystring, headers = hdc.create_api_request()

        url = url + "/" + self.hdt_id

        querystring['OPERATION_NAME'] = "REPLY_REQUEST"
        querystring['INPUT_DATA'] = "{operation: " \
                                    "{Details:{TO: '%s',SUBJECT: '%s' ,DESCRIPTION: '%s'}}}" % (requester_email, subject, reply_message)
        ticket_conversation_details = hdc.fetch_from_helpdesk(url, querystring, headers)

        # TODO - use Conversation ID to check if success.
        get_conversation_detail = list([ticket_conversation_details])
        return get_conversation_detail

if __name__ == '__main__':
    ticket = Ticket('11098')
    print ticket.send_priority_reply()