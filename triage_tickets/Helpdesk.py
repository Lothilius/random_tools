__author__ = 'Lothilius'

import requests
import json
import sys
from triage_tickets.TicketList import TicketList
from Status import Status
import datetime
import pandas as pd
import re

pd.set_option('display.width', 160)


class Helpdesk(Status):
    """ Extend Status class for Helpdesk.
    """
    def __init__(self):
        super(Helpdesk, self).__init__()
        self.technician_groups = ''

    def count_tickets(self, helpdesk_tickets):
        """Count total unassigned"""
        unassigned_total = 0
        for each in helpdesk_tickets:
            if each['TECHNICIAN'] == '':
                unassigned_total += 1

        return unassigned_total


    def get_all_tickets(self):
        try:
            from_value = 1
            # Get first 100 ticket from helpdesk
            tickets = TicketList(helpdesk_que='Hourly-Open-Tickets-do-not-edit', with_detail=False)
            self.set_status(status_value=1)
            self.set_status_message('Functioning normally')
            self.set_error_message('No Error Reported.')
            tickets = TicketList.reformat_as_dataframe(tickets)
            return len(tickets)
        except requests.exceptions.ConnectionError:
            error_result = "Unexpected error 1: %s" % (sys.exc_info()[0])
            if 'Max retries exceeded with url:' in sys.exc_info()[1]:
                self.status = 0
                self.set_status_message('Not able to Connect to manageengine.com')
                # TODO -Fix this issue so that error_message is populated!
                self.error_message = error_result
        except:
            error_result = "Unexpected error 1: %s" % (sys.exc_info()[0])
            self.status = 0
            self.set_status_message('Error Loading. Possible Helpdesk outage.')
            # TODO -Fix this issue so that error_message is populated!
            self.error_message = error_result

            return -1



if __name__ == '__main__':
    status = Helpdesk()
    # tickets = pd.DataFrame(status.tickets)
