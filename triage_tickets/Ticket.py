#!/usr/bin/env python
# coding: utf-8
__author__ = 'Lothilius'

from HelpdeskConnection import HelpdeskConnection as hdc
import sys
import re
from time import time

reload(sys)
sys.setdefaultencoding('utf8')

class Ticket(object):
    def __init__(self, hdt_id):
        self.hdt_id = hdt_id
        self.resolution = self.get_resolution()
        self.details = self.get_ticket_details()
        self.conversations = ''

    def __getitem__(self, item):
        details = list(dict(self.details))
        return details[item]

    def __str__(self):
        """
        :return: String value of the ticket.
        """
        return str(self.details)

    def get_ticket_details(self):
        """ Retrieve ticket detials for individual ticket.
        :param ticket_number: The workorder id of ticket number of the Ticket
        :return: Dictionary of the ticket details
        """
        url, querystring, headers = hdc.create_api_request()

        url = url + "/" + self.hdt_id

        querystring['OPERATION_NAME'] = "GET_REQUEST"
        del querystring['INPUT_DATA']
        # print querystring
        helpdesk_ticket_details = hdc.fetch_from_helpdesk(url, querystring, headers)
        helpdesk_ticket_details.update(self.resolution)

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

    def get_resolution(self):
        """ Retrieve resolution for individual ticket.
        :param ticket_number: The workorder id of ticket number of the Ticket
        :return: Dictionary of the ticket details
        """
        url, querystring, headers = hdc.create_api_request()

        url = url + "/" + self.hdt_id + "/resolution"

        querystring['OPERATION_NAME'] = "GET_RESOLUTION"
        del querystring['INPUT_DATA']
        # print querystring
        ticket_resolution_details = hdc.fetch_from_helpdesk(url, querystring, headers)
        # If Resolution is response is empty pad with NA
        if ticket_resolution_details == {}:
            ticket_resolution_details['RESOLUTION'] = 'NA'
            ticket_resolution_details['RESOLUTIONLASTUPDATEDTIME'] = 'NA'
            ticket_resolution_details['RESOLVER'] = 'NA'
            self.resolution = ticket_resolution_details
        else:
            ticket_resolution_details['RESOLUTIONLASTUPDATEDTIME'] = \
                ticket_resolution_details.pop('LASTUPDATEDTIME')
            self.resolution = ticket_resolution_details

        return self.resolution

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

    @staticmethod
    def set_status(hdt_id, status='Resolved'):
        """ Set status for ticket.
        :param hdt_id: The workorder id of ticket number of the Ticket
        :param status: String value selectable as the status for the HDT
        :return: Dictionary of the ticket details once the status has been changed.
        """
        try:
            # Change today to Epoch time
            print hdt_id, status
            url, querystring, headers = hdc.create_api_request()

            url = url + "/" + hdt_id

            querystring['OPERATION_NAME'] = "EDIT_REQUEST"
            querystring['INPUT_DATA'] = "{operation:{" \
                                        "Details:{" \
                                        "STATUS:%s}}}" % status
            # print querystring
            helpdesk_ticket_details = hdc.fetch_from_helpdesk(url, querystring, headers)

            return helpdesk_ticket_details
        except:
            error_result = "Unexpected error 1T: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
            print error_result


    def send_priority_reply(self):
        """ Send a hard coded reply to a ticket.
        :param requester_email: The workorder id of ticket number of the Ticket
        :return: Dictionary of the ticket details
        """
        requester_first_name = self.details['REQUESTER'].split()[0]
        requester_email = self.details['REQUESTEREMAIL']

        # Create subject without special characters.
        subject = 'Re: [Request ID :##%s##] : %s' % \
                  (self.hdt_id, re.sub('[^A-Za-z0-9\s]+', '', self.details['SUBJECT']))
        print subject
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
    ticket = Ticket('15438')
    # print ticket
    print ticket

