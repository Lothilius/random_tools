__author__ = 'Lothilius'
# coding: utf-8

import smtplib
from bv_authenticate.Authentication import Authentication as auth
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from os.path import basename
from os import environ
import sys

reload(sys)
sys.setdefaultencoding('utf8')

class OutlookConnection(object):
    def __init__(self, to='', cc='', bcc='', subject='', body=' ', html='', files=None, reply_to=''):
        try:
            self.html = html.encode("utf-8")
            self.files = files
            if html != '':
                self.msg = MIMEMultipart('alternative')
                self.msg.attach(MIMEText(body.encode("utf-8"), 'plain', _charset="utf-8"))
                self.msg.attach(MIMEText(body.encode("utf-8"), 'html', _charset="utf-8"))
            else:
                self.msg = MIMEMultipart()
                self.msg.attach(MIMEText(body.encode("utf-8"), 'plain', _charset="utf-8"))

            username, password = auth.smtp_login()
            self.msg['From'] = username

            self.build(to, cc=cc, bcc=bcc, reply_to=reply_to, subject=subject)
        except:
            error_result = "Unexpected error in initiating Outlook Connection: %s, %s" \
                           % (sys.exc_info()[0], sys.exc_info()[1])
            print error_result

    def build(self, to, cc='', bcc='', reply_to='', subject=''):
        self.msg['Subject'] = subject

        if isinstance(to, list):
            self.msg['To'] = ", ".join(to)
            self.to = to
        else:
            self.msg['To'] = to
            self.to = [to]
            # print to

        if cc != '':
            if isinstance(cc, list):
                self.msg['CC'] = ", ".join(cc)
                self.cc = cc
            else:
                self.msg['CC'] = cc
                self.cc = [cc]
        else:
            self.cc = [cc]
        if bcc != '':
            if isinstance(cc, list):
                self.msg['BCC'] = ", ".join(bcc)
                self.bcc = bcc
            else:
                self.msg['BCC'] = bcc
                self.bcc = [bcc]
        else:
            self.bcc = [bcc]

        if reply_to != '':
            if isinstance(reply_to, list):
                self.msg['Reply-to'] = ", ".join(reply_to)
                self.reply_to = reply_to
            else:
                self.msg['Reply-to'] = reply_to
                self.reply_to = [reply_to]
        else:
            self.reply_to = [reply_to]


    def attach_file(self):
        """ Attach any files in a list or string passed to the initiation of the object.
        """
        # Help from stack over flow
        # http://stackoverflow.com/questions/3362600/how-to-send-email-attachments-with-python
        if not isinstance(self.files, list):
            self.files = [self.files]
        for f in self.files or []:
            with open(f, "rb") as fil:
                part = MIMEApplication(
                    fil.read(),
                    Name=basename(f)
                )
                part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
                self.msg.attach(part)

    def send_email(self, to='', cc='', bcc='', subject='', body=' ', html='', files='', reply_to=''):
        """ Send email with or without variables passed in initiation.
        :param to: list or comma separated string of To emails addresses
        :param cc: list or comma separated string of CC emails addresses
        :param bcc: list or comma separated string of BCC emails addresses
        :param subject: string of the subject for the email
        :param body: HTML or Plain text body of email
        :param html: HTML of the text in the body of the email
        :param files: file address of attachment for the email
        :param reply_to: list or comma separated string of reply_to emails

        """
        # TODO - create user interactive section here.

        if body != ' ':
            self.__init__(to, cc, bcc, subject, body, html, files, reply_to)

        try:
            username, password = auth.smtp_login()
            self.msg['From'] = username

            all_emails = self.to + self.cc + self.bcc + self.reply_to

            email_connection = OutlookConnection.connect_mail(username, password)

            if self.files != '' and self.files is not None:
                self.attach_file()

            email_connection.sendmail(username, all_emails, self.msg.as_string())

            email_connection.quit()
            print 'Message sent'
        except:
            error_result = "Unexpected error in sending Email: %s, %s" % (sys.exc_info()[0], sys.exc_info()[1])
            print error_result

    @staticmethod
    def create_helpdesk_ticket(subject, body, cc='', bcc='', html='', files='', send_test=''):
        """ Use to quickly email Helpdesk
        :param subject: The subject of the email
        :param body: The message of the email
        :return:
        """
        if environ['MY_ENVIRONMENT'] != 'prod' and send_test != '':
            subject = '--TESTING--' + subject
            to = 'martin.valenzuela@bazaarvoice.com'
        else:
            to = 'helpdesk@bazaarvoice.com'
        OutlookConnection().send_email(to=to, cc=cc, bcc=bcc, subject=subject, body=body, html=html, files=files)



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
        except Exception, e:
            error_result = "Unexpected error in making connection to mail server: %s, %s" \
                           % (sys.exc_info()[0], sys.exc_info()[1])
            print error_result

if __name__ == '__main__':
    body = '<html><head></head><body><h2>BizApps - Technical</h2></body></html>'
    subject = 'Do you get this>'
    to = ['mars110110@aol.com']
    cc = ['martin.valenzuela@bazaarvoice.com']#, 'Lindsey.Fivecoat@bazaarvoice.com', 'Dustin.Dodson@bazaarvoice.com']
    # oc = OutlookConnection()
    # oc.send_email(to=to, subject=subject, body=body, html=body)
    oc = OutlookConnection()
    oc.send_email(to=to, cc=cc, subject=subject, body=body, html=body)