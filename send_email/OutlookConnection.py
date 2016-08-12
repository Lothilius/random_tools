__author__ = 'Lothilius'

import smtplib
from bv_authenticate.Authentication import Authentication as auth
import sys


class OutlookConnection(object):

    @staticmethod
    def send_email(to, cc='', bcc='', subject='', body=' '):
        username = ''
        password = ''
        # TODO - create user interactive section here.
        # while username == '' and password == '':
        # username = ''
        # password = ''
        # print 'Username and Password needed'
        if isinstance(to, list):
            to = ", ".join(to)
        if cc != '':
            if isinstance(cc, list):
                cc = '\n' + 'CC: ' + ",".join(cc)
            else:
                cc = '\n' + 'CC: ' + cc
        if bcc != '':
            if isinstance(cc, list):
                bcc = '\n' + 'BCC: ' + ",".join(bcc)
            else:
                bcc = '\n' + 'BCC:' + bcc

        try:
            username, password = auth.smtp_login()
            full_message = "From: " + username \
                           + '\n' + 'To: ' + to \
                           + cc \
                           + bcc \
                           + '\n' + 'Subject: ' + subject \
                           + '\n\n' + body

            all_emails = [to] + [cc] + [bcc]
            email_connection = OutlookConnection.connect_mail(username, password)
            email_connection.sendmail(username, all_emails, full_message)
            email_connection.close()
            print 'Message sent'
        except:
            error_result = "Unexpected error 1: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
            print error_result

    @staticmethod
    def create_helpdesk_ticket(subject, body, cc='', bcc=''):
        """ Use to quickly email Helpdesk
        :param subject: The subject of the email
        :param body: The message of the email
        :return:
        """
        to = 'helpdesk@bazaarvoice.com'
        OutlookConnection.send_email(to=to, cc=cc, bcc=bcc, subject=subject, body=body)


    @staticmethod
    def connect_mail(username, password):
        """ Method does the actual connection to the smtp server.
        :param username: should be in the form of an email.
        :param password:
        :return:
        """
        try:
            smtp_object = smtplib.SMTP('smtp.office365.com', 587)
            smtp_object.ehlo()
            smtp_object.starttls()
            username, password = auth.smtp_login()
            smtp_object.login(username, password)
            return smtp_object
        except Exception, exc:
            error_result = "Unexpected error 1: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
            print error_result