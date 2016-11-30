__author__ = 'Lothilius'


from send_email.OutlookConnection import OutlookConnection as out


def main():
    subject = "NetSuite Boomi user needs a new password"
    body = """90 day reminder of NetSuite Boomi pw change.
    Please click on the link to update the password.
     https://system.na2.netsuite.com/app/common/entity/employee.nl?id=5415
    """
    out.create_helpdesk_ticket(subject=subject, body=body)

if __name__ == '__main__':
    main()