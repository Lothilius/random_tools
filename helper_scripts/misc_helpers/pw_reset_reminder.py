__author__ = 'Lothilius'


from send_email.OutlookConnection import OutlookConnection as out
import os

user_list = [('NetSuite Boomi', 'https://system.na2.netsuite.com/app/common/entity/employee.nl?id=5415'),
             ('Concur API', 'https://www.concursolutions.com/profile/send_password_hint.asp')]


def main():
    try:
        for user_item in user_list:
            subject = "%s user needs a new password" % user_item[0]
            body = """80 day reminder of %s pw change.
            Please click on the link to update the password.
             %s

             [BizApps]
            """ % (user_item[0], user_item[1])
            out.create_helpdesk_ticket(subject=subject, body=body)
    except:
        subject = "%s user needs a new password" % user_item[0]
        body = """Please check the reminder script on the BizTech Ops server.
            The script can be found at the following address
            %s""" % os.path.dirname(unicode(__file__, encoding='utf-8'))
        out.send_email(to='bizapps@bazaarvoice.com', subject=subject, body=body)

if __name__ == '__main__':
    main()