__author__ = 'Lothilius'
# coding: utf-8

from triage_tickets.TicketList import TicketList
from send_email.OutlookConnection import OutlookConnection
import pandas as pd
from datetime import datetime, date, timedelta
from HTMLParser import HTMLParser
import sys


reload(sys)
sys.setdefaultencoding('utf8')

pd.set_option('display.width', 160)
pd.set_option('display.max_colwidth', -1)

def triage_timeframe():
    today_date_time = datetime.today()
    today_date_time = today_date_time.replace(hour=10, minute=0, second=0, microsecond=0)
    if today_date_time.weekday() in range(1, 4):
        last_triage = today_date_time - timedelta(days=1)
        return last_triage, today_date_time
    else:
        last_triage = today_date_time - timedelta(days=3)
        return last_triage, today_date_time
        # last_traige = last_traige -

def create_link(reauest_id, link_id):
    pass


def main():
    # try:
    last_triage, triage_cutoff = triage_timeframe()
    tickets = TicketList()
    tickets = tickets.reformat_as_dataframe(tickets)
    tickets = tickets[tickets['CREATEDTIME'] >= last_triage]
    tickets = tickets[tickets['CREATEDTIME'] < triage_cutoff]
    # tickets = tickets.rename(columns={'WORKORDERID': 'RequestID'}, inplace=True)
    # print tickets
    ticket_triage = tickets[tickets['GROUP'] == 'BizApps - Triage'][[
                               'TECHNICIAN',
                               'PRIORITY',
                               'System Component',
                               'WORKORDERID',
                               'REQUESTER',
                               'SUBJECT']]
    ticket_triage = ticket_triage.groupby([
                               'TECHNICIAN',
                               'PRIORITY',
                               'System Component'], as_index=False).size()

    ticket_technical = tickets[tickets['GROUP'] == 'BizApps - Technical'][['GROUP',
                               'TECHNICIAN',
                               'System Component',
                               'PRIORITY',
                               'REQUESTER',
                               'SUBJECT']]
    ticket_technical = ticket_technical.groupby([
                               'TECHNICIAN',
                               'PRIORITY',
                               'System Component'], as_index=False).size()

    ticket_integration = tickets[tickets['GROUP'] == 'BizApps - Integrations'][['GROUP',
                               'TECHNICIAN',
                               'System Component',
                               'PRIORITY',
                               'REQUESTER',
                               'SUBJECT']]
    ticket_integration = ticket_integration.groupby([
                               'TECHNICIAN',
                               'PRIORITY',
                               'System Component'], as_index=False).size()


    ticket_triage = pd.DataFrame(ticket_triage, columns=['Count']).reset_index()
    ticket_technical = pd.DataFrame(ticket_technical, columns=['Count']).reset_index()
    ticket_integration = pd.DataFrame(ticket_integration, columns=['Count']).reset_index()
    full_tickets = tickets.sort_values(by=['GROUP',
                                           'TECHNICIAN',
                                           'PRIORITY',
                                           'WORKORDERID',
                                           'SUBJECT']
                                       )[['GROUP', 'TECHNICIAN', 'PRIORITY', 'WORKORDERID', 'SUBJECT']]

    to = 'martin.valenzuela@bazaarvoice.com'
    subject = 'Triage summery %s' % str(date.today())
    # print tickets.iloc[0].tolist()
    ticket_triage = ticket_triage.to_html()
    ticket_technical = ticket_technical.to_html()
    ticket_integration = ticket_integration.to_html()
    full_tickets = full_tickets.to_html(index=False, show_dimensions=True)

    html = HTMLParser()
    body = '<html><head></head><body>' + \
           '<h2>BizApps - Triage</h2>' + html.unescape(ticket_triage) + '<br><br>'\
           '<h2>BizApps - Technical</h2>' + html.unescape(ticket_technical) + '<br><br>'\
           '<h2>BizApps - Integrations</h2>' + html.unescape(ticket_integration) + '<br><br>'\
           '<h2>All Tickets</h2>' + html.unescape(full_tickets) + '<br><br>'\
           '</body></html>'
    # body = unicode(body, errors='ignore')
    # print body
    OutlookConnection.send_email(to=to, subject=subject, body=body, html=body)
    # except:
    #     to = 'martin.valenzuela@bazaarvoice.com'
    #     subject = 'It is broken'
    #     body = 'Broken'
    #     OutlookConnection.send_email(to=to, subject=subject, body=body)


if __name__ == '__main__':
    main()
