#!/usr/bin/python

__author__ = 'Lothilius'


import requests
import json
from bv_authenticate.Authentication import Authentication as auth
from send_email.OutlookConnection import OutlookConnection as outlook
from Okta_Connection import Okta_Connection as okta_connect
import smtplib
import sys
import pandas as pd
from datetime import datetime
from datetime import timedelta


# Create query
def create_query():
    yesterday = datetime.today() - timedelta(1)
    yesterday = yesterday.strftime('%Y-%m-%dT%H:%M:%S.000Z')
    query_string = "action.objectType eq \"app.salesforce.user_management.failure.provisioning\" and " \
                   "published gt \"%s\"" % yesterday
    query_dictionary = {"filter":query_string}

    return query_dictionary

def message_breakup(message):
    # For error messages with multiple messages eplit on : and rebuild on every other :
    prep_message = message.split(':')
    error_message = ''
    for i, each in enumerate(prep_message):
        if i % 2 == 0 and i <= len(prep_message) - 2:
            error_message = error_message + prep_message[i] + ':' + prep_message[i + 1] + '\n'

    return error_message


# Create the body of the message
def create_body(errors):
    body = 'Hello. Some errors have been found in Okta deprovisioning.  ' + errors

    return body

# Create a String of the errors that will be place in the email body.
def create_message(errors):
    # print errors.values[0][1]
    error_message = ''
    for each in errors.values:
        message = str(message_breakup(each[1]))
        name = str(each[0])
        id = "https://bazaarvoice-admin.okta.com/admin/user/profile/view/" + str(each[2])
        application = str(each[3])
        error_message = error_message + '\n\n' + str(name + "\n" + id + "\n" + application + "\n" + message)

    return error_message


# Build and send the emails
def send_message(subject, body, receiver='helpdesk@bazaarvoice.com'):
    outlook.send_email(to=receiver, subject=subject, body=body)
    print "Successfully sent email to " + receiver


def querry_okta():
    # Initiate connection to Okta
    okta = okta_connect(primary_object='events', query=create_query())

    # Set response json object to variable
    okta_json = okta.fetch_from_okta()
    print okta_json
    # Create dataframe
    errors = pd.DataFrame(columns=['Name', 'Message', 'ID', 'Application'])

    for each in okta_json:
        name = each["targets"][0]["displayName"]
        message = each["action"]["message"]
        id = each["targets"][0]["id"]
        app = each["targets"][1]["displayName"]

        # Place info in to the dataframe
        errors = errors.append({'Name': name, 'Message': message, 'ID': id, 'Application': app}, ignore_index=True)
    if errors.empty:
        print "No errors"
    else:
        # Iterate through the json object retrieving useful info.
        body = create_body(create_message(errors))
        subject='Okta - SFDC Deprovisioning Errors'
        try:
            send_message(subject=subject, body=body)
        except smtplib.SMTPServerDisconnected:
            print 'Server Disconnected'
            try:
                send_message(subject=subject, body=body)
            except Exception, exc:
                sys.exit("mail failed1; %s" % str(exc)) # give a error message
        except Exception, exc:
            sys.exit("mail failed2; %s" % str(exc)) # give a error message


if __name__ == '__main__':
    querry_okta()