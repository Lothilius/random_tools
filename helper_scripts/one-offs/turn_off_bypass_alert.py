__author__ = 'Lothilius'

from send_email.OutlookConnection import OutlookConnection as outlook
import sys


if __name__ == '__main__':
    try:
        name = sys.argv[1]
    except:
        name = 'Someone'
    print name
    subject = 'SFDC - Alert - Turn off Account trigger bypass.'
    body = 'It has been at least 24 hours since the Account trigger bypass has been turned on for %s. ' \
           'https://na3.salesforce.com/setup/ui/listCustomSettingsData.apexp?id=aAS' % name
    outlook.create_helpdesk_ticket(subject=subject, body=body)
