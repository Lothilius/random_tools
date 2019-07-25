# coding: utf-8
__author__ = 'Lothilius'

import sys

from bv_authenticate.Authentication import Authentication as auth
from send_email.OutlookConnection import OutlookConnection as outlook
from triage_tickets.TicketList import Ticket
from tableau_data_publisher.data_assembler_hyper import HyperAssembler
from tableau_data_publisher.Tableau import Tableau
from helper_scripts.notify_helpers import Notifier
from okta.Okta_Group_Members import Okta_Group_Members
from os.path import basename
from os import environ
from time import time
from datetime import datetime
from HTMLParser import HTMLParser
from static.static_files import get_static_file
from helper_scripts.notify_helpers import wait
import pandas as pd
import os
from os import remove
import socket


work_day_groups = Okta_Group_Members(query='WD-Active')
m_f_group = '00gcy0wldkSLIQJLRDDU'
today = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

if environ['MY_ENVIRONMENT'] == 'prod':
    file_path = '/var/shared_folder/EUS/Tableau_data/'
    project = 'EUS'
else:
    file_path = '/Users/%s/Downloads/' % environ['USER']
    project = 'Testing'

extract_name = 'MFA_Employee_data'


def mfa_notify(user_info=('martin.valenzuela@bazaarvoice.com', 'Martin')):
    try:
        user_email = user_info[0]
        user_first_name = user_info[1]

        # Connect as Helpdesk
        email = outlook(account='helpdesk@bazaarvoice.com')
        instructions_path = os.path.join(os.path.dirname(__file__), 'mfa_instructions/')
        html_file_name = instructions_path + 'instruction_email_html.txt'

        with open(html_file_name, 'r') as html_file:
            html = html_file.read()

        # Create list for attaching images to the html for the email
        html = html % user_first_name
        file_names = ['%simage%03d.jpg' % (instructions_path, number) for number in range(1, 11)]

        email.send_email(to=user_email, subject='Added to Multi Factor Authentication',
                         body=html,
                         html=html,
                         files=file_names)
    except Exception, e:
        error_result = "Unexpected Error: %s, %s, %s" \
                       % (sys.exc_info()[0], sys.exc_info()[1], e)
        subject = 'Error with MFA true up script. Not able to send Email. %s' % basename(__file__)
        print error_result
        try:
            data = {'REQUESTEREMAIL': 'martin.valenzuela@bazaarvoice.com',
                    'REQUESTER': 'Martin Valenzuela',
                    'DESCRIPTION': error_result,
                    'SUBJECT': subject}
            Ticket().create_ticket(data)
        except:
            outlook().send_email('helpdesk@bazaarvoice.com', cc='BizAppsIntegrations@bazaarvoice.com',
                                 subject=subject,
                                 body=error_result)
        give_notice = Notifier()
        give_notice.set_red()
        give_notice.wait(30)
        give_notice.flow_the_light()


def main():
    try:
        all_wd_employees = []
        for each in work_day_groups.groups['id'].tolist():
            # Get Users from Okta that are in the list of Workday groups
            mfa_users = Okta_Group_Members(group_id=each)
            mfa_employees = mfa_users.group_members
            all_wd_employees.append(mfa_employees)

        # Union all data frames
        all_wd_employees = pd.concat(all_wd_employees, ignore_index=True)

        # Get Users from Okta that are in mfa-everywhere group
        mfa_users = Okta_Group_Members(group_id=m_f_group)
        mfa_employees = mfa_users.group_members

        # Do an left outer join so all Workday employees and their MFA profiles are matched up
        left_wd_join = pd.merge(left=all_wd_employees, right=mfa_employees[['email', 'login']],
                                how='left', on='email', suffixes=('_wd', '_mfa'))

        # Any Null in login_mfa column are not in MFA group.
        employees_without_mfa = left_wd_join[left_wd_join['login_mfa'].isnull()].copy()  # type: pd.DataFrame

        # If employees_without_mfa is not Empty then apply mfa group to user missing the group and publish full list.
        if not employees_without_mfa.empty:
            # Apply mfa group to each user without mfa
            employees_without_mfa['result'] = employees_without_mfa['email'].apply(mfa_users.add_user_to_group)

            # Reduce to Success list
            employees_success = employees_without_mfa[
                employees_without_mfa['result'].str.contains('Success')][['email', 'firstName']]

            # Send Email notifiying user of the change
            for each in employees_success.values.tolist():
                mfa_notify(each)
                wait(1)

            left_wd_join = pd.merge(left=left_wd_join, right=employees_without_mfa[['email', 'result']],
                                    how='left', on='email', suffixes=('_wd', '_results'))

            try:
                # Package in to a hyper file
                data_file = HyperAssembler(data_frame=left_wd_join, extract_name=extract_name, file_path=file_path)
                # Set values for publishing the data.
                file_name = str(data_file)
                tableau_server = Tableau(server_url='https://tableau.bazaarvoice.com/', site_id='BizTech')
                tableau_server.publish_datasource(project=project,
                                                  file_path=file_name,
                                                  mode='Append', name=extract_name)

                remove(file_name)

            except Exception, e:
                error_result = "Unexpected Error: %s, %s, %s" \
                               % (sys.exc_info()[0], sys.exc_info()[1], e)
                subject = 'Error with MFA true up script. Could not publish user list to Tableau. %s on %s' % \
                          (basename(__file__), socket.gethostname())
                error_result += subject
                print error_result
                try:
                    data = {'REQUESTEREMAIL': 'martin.valenzuela@bazaarvoice.com',
                            'REQUESTER': 'Martin Valenzuela',
                            'DESCRIPTION': error_result,
                            'SUBJECT': subject}
                    Ticket().create_ticket(data)
                except:
                    outlook().send_email('helpdesk@bazaarvoice.com', cc='BizAppsIntegrations@bazaarvoice.com',
                                         subject=subject,
                                         body=error_result)
                give_notice = Notifier()
                give_notice.set_red()
                give_notice.wait(30)
                give_notice.flow_the_light()

        # Get Style sheet for the email.
        html = HTMLParser()
        f = open(get_static_file('styleTags.html'), 'r')
        style = f.readlines()
        style = ' '.join(style)
        style = html.unescape(style)
        employees_without_mfa = employees_without_mfa[['id', 'email', 'result']].to_html(index=False,
                                                                                         show_dimensions=True)
        body = '<html><head>%s</head><body>' % style + '<h2>MFA_User_application compiling complete</h2><br><br>' \
               '<h2>List of Users Below</h2>' + html.unescape(employees_without_mfa) + \
               '<br><br></body></html>'

        outlook().send_email(to='BizAppsIntegrations@bazaarvoice.com',
                             subject='MFA_User_application Complete',
                             body=body, html=body)


    except KeyboardInterrupt:
        pass
    except Exception, e:
        error_result = "Unexpected AttributeError: %s, %s" \
                       % (sys.exc_info()[0], sys.exc_info()[1])
        subject = 'Error with MFA true up script. Major error. ' \
                  'Might have prevented mfa Provisioning. %s on %s' % (basename(__file__), socket.gethostname())
        error_result += subject
        print error_result
        try:
            data = {'REQUESTEREMAIL': 'martin.valenzuela@bazaarvoice.com',
                    'REQUESTER': 'Martin Valenzuela',
                    'DESCRIPTION': error_result,
                    'SUBJECT': subject}
            Ticket().create_ticket(data)
        except:
            outlook().send_email('helpdesk@bazaarvoice.com', cc='BizAppsIntegrations@bazaarvoice.com', subject=subject,
                                 body=error_result)
        give_notice = Notifier()
        give_notice.set_red()
        give_notice.wait(30)
        give_notice.flow_the_light()


if __name__ == '__main__':
    start = time()
    main()
    end = time()
    print (end - start) / 60
    print datetime.now()
