__author__ = 'Lothilius'

import sys
from HTMLParser import HTMLParser

import pandas as pd

from helper_scripts.misc_helpers.request_input_prompt import request_user_input
from send_email.OutlookConnection import OutlookConnection as out_look_email
from sfdc.SFDC_User_Licenses import SFDC_Package_Licenses as sfdc_licenses
from sfdc.SFDC_Users import SFDC_Users as sf_users
from okta.Okta_Application import Okta_Application

pd.set_option('display.width', 250)
pd.set_option('display.max_columns', 40)
pd.set_option('display.max_rows', 5)
pd.set_option('max_colwidth', 40)


e2cp = ('05050000000PD1HAAW', """      In an effort to reduce our licensing costs, BizApps is looking to identify unused \"Email to Case Premium\" licenses.

Please take a moment to consider your use of the \"New Comment\" button on the Case screen in Salesforce.
If it has been a while since you have used the \"New Comment\" button,
""")

gainsight = ('05050000000PGwkAAG', """      In an effort to reduce our licensing costs, BizApps is looking to identify unused \"Gainsight\" licenses.

Please take a moment to consider whether you use \"Gainsight\" functionality in Salesforce.
If it has been a while since you have used \"Gainsights\",
""")

workit =('05050000000PDJGAA4', """      In an effort to reduce our licensing costs, BizApps is looking to identify unused \"Workit\" licenses.

Please take a moment to consider whether you use \"WorkIt\" case timing functionality in Salesforce.
If it has been a while since you have used \"Workit\" case timing functionality,
""")

license_list = [e2cp, gainsight, workit]

# Create email addresses.
def create_email_address(name):
    email = name.replace(' ', '.')
    email = email + '@bazaarvoice.com'

    return email

# Create the body of the message
def create_license_request_body(full_name, license):
    first_name = full_name.split()[0]
    body = 'Hello ' + first_name + ',\n' + license + """or your role has changed so you no longer need this functionality, please let us know so we can recapture the license and save BV some $$$.
If you still use the functionality please ignore this email.

We appreciate your help in our efforts.
Please let us know if you have any questions.

Thank you

Martin A Valenzuela
Business Applications Administrator
m:  915.217.8558
Martin.Valenzuela@bazaarvoice.com"""

    return body


# Build and send the emails
def send_message(smtp_object, subject, body, receiver='martin.valenzuela@bazaarvoice.com',
                  sender='martin.valenzuela@bazaarvoice.com'):

    full_message = """From:""" + sender + '\n' + 'To:' + receiver + '\n' \
              + 'Subject: ' + subject + '\n\n' + body


    smtp_object.sendmail(sender, [receiver], full_message)
    print "Successfully sent email to " + receiver

def create_deprovisioning_body(user_list):
    """ Create the HTML body for emailing the data frame that is passed to it.
    :param user_list: Must be a Pandas Dataframe
    :return: sting of the html ready to send in an email.
    """
    html = HTMLParser()
    user_list = user_list.to_html()

    # Get Style sheet for the email.
    f = open('/Users/martin.valenzuela/Dropbox/Coding/BV/bv_tools/static/styleTags.html', 'r')
    style = f.readlines()
    style = ' '.join(style)
    style = html.unescape(style)

    body = '<html><head>%s</head><body>' % (style) + \
           '<h2>Please check and Deprovision as necessary</h2>' + html.unescape(user_list) + '<br><br>'\
           '</body></html>'

    return body

def main():
    try:
        outlook = out_look_email()
    except Exception, exc:
        sys.exit("mail failed1; %s" % str(exc))

    try:
        # Get Active SFDC users
        sfdc_users = sf_users().get_user_list()
        sfdc_users.rename(columns={'Id': 'UserId'}, inplace=True)
        sfdc_users['Email'] = sfdc_users['Email'].apply(lambda x: x.lower())
        sfdc_users = sfdc_users[sfdc_users['IsActive'] == True]

        # Get Workday Users
        workday = Okta_Application(app_name='workday')
        current_emplyee_list = workday.app_users

        current_emplyee_list.rename(columns={'email': 'Email'}, inplace=True)
        current_emplyee_list['Email'] = current_emplyee_list['Email'].apply(lambda x: x.lower())

        print current_emplyee_list.columns

    except IOError, error:
        print 'Try Again ' + str(error)  # give a error message

    # Get list of licenses with users.
    licensed_users = sfdc_licenses().get_license_list()

    # print licensed_users

    users_and_license = licensed_users.merge(sfdc_users, on='UserId', how='inner')
    # print users_and_license
    left_outer_list = users_and_license.merge(current_emplyee_list, on='Email', how='left')
    print "<---------- deprovision_list ---------->"
    deprovision_list = left_outer_list[
        (left_outer_list['employeeID'].isnull())
        &
        (~left_outer_list['UserName'].str.contains(
            'AutoCaseUser|Integration|BizApps|Apttus Cache Warmer|Tableau'))].copy()

    deprovision_list.drop_duplicates(subset=['UserName', 'Email', 'UserId'], keep='first', inplace=True)
    body = create_deprovisioning_body(deprovision_list[['UserName', 'Email', 'UserId']])
    outlook.create_helpdesk_ticket(subject='Users not found as active employees.', body=body, html=body)

    # Gather users with E2CP licenses.
    e2cp_users = users_and_license[['PackageLicenseId', 'UserId', 'Email', 'UserName']][users_and_license['PackageLicenseId'] == e2cp[0]]


    #gather list of user emails that have the license and are not on the deprovision list
    print "<---------- Emailing ---------->"
    users_to_ask = e2cp_users[~e2cp_users['Email'].isin(deprovision_list['Email'].tolist())][['Email', 'UserName']].values.tolist()
    e2cp_users[~e2cp_users['Email'].isin(deprovision_list['Email'].tolist())][['Email', 'UserName']].to_csv('/Users/martin.valenzuela/Downloads/recieved_email_.csv')

    # Request user input...
    response = request_user_input(prompt='Ready to send emails?')

    if response == 'y':
        for each in users_to_ask:
            try:
                print each[0]
                body = create_license_request_body(each[1], e2cp[1])
                receiver = create_email_address(each[1])


                # outlook.send_email(to=receiver, subject='License usage in SFDC', body=body)
            except:
                print "Error did not send."
                # sys.exit("mail failed2; %s" % str(exc))  # give a error message
                pass
    else:
        print 'Good bye!'

if __name__ == '__main__':
    main()


