# -----------------------------------------------------------------------------
#
# This file is the copyrighted property of Tableau Software and is protected
# by registered patents and other applicable U.S. and international laws and
# regulations.
#
# Unlicensed use of the contents of this file is prohibited. Please refer to
# the NOTICES.txt file for further details.
#
# -----------------------------------------------------------------------------

from tableausdk import *
from tableausdk.Server import *
from send_email.OutlookConnection import OutlookConnection
from triage_tickets.Ticket import Ticket


def publish_data(server_url, username, password, site_id, file_name,
                 data_source_name, project='default', replace_data=False):
    """ Use to publish tde files to the server.
    :param server_url:
    :param username:
    :param password:
    :param site_id:
    :param file_name:
    :param data_source_name:
    :param project:
    :param replace_data:
    :return:
    """
    try:
        # Initialize Tableau Server API
        ServerAPI.initialize()

        # Create the server connection object
        serverConnection = ServerConnection()

        # Connect to the server
        serverConnection.connect(server_url, username, password, site_id);

        # Publish file_name to the server under the default project with name data_source_name
        serverConnection.publishExtract(file_name, project, data_source_name, replace_data);

        # Disconnect from the server
        serverConnection.disconnect();

        # Destroy the server connection object
        serverConnection.close();

        # Clean up Tableau Server API
        ServerAPI.cleanup();
        if site_id == '':
            site_id = 'Default'
        print "Published %s to %s in %s" % (data_source_name, project, site_id)

    except TableauException, e:
        # Handle the exception depending on the type of exception received

        error_message = "Error: "

        if e.errorCode == Result.INTERNAL_ERROR:
            error_message += "INTERNAL_ERROR - Could not parse the response from the server."

        elif e.errorCode == Result.INVALID_ARGUMENT:
            error_message += "INVALID_ARGUMENT - " + e.message

        elif e.errorCode == Result.CURL_ERROR:
            error_message += "CURL_ERROR - " + e.message

        elif e.errorCode == Result.SERVER_ERROR:
            error_message += "SERVER_ERROR - " + e.message

        elif e.errorCode == Result.NOT_AUTHENTICATED:
            error_message += "NOT_AUTHENTICATED - " + e.message

        elif e.errorCode == Result.BAD_PAYLOAD:
            error_message += "BAD_PAYLOAD - Unknown response from the server. Make sure this version of Tableau API is compatible with your server."

        elif e.errorCode == Result.INIT_ERROR:
            error_message += "INIT_ERROR - " + e.message

        else:
            error_message += "An unknown error occured."

        print error_message
        try:
            data = {'REQUESTEREMAIL': 'martin.valenzuela@bazaarvoice.com',
                    'REQUESTER': 'Martin Valenzuela',
                    'DESCRIPTION': error_message,
                    'SUBJECT': 'Error Creating HDT Tableau export'}
            Ticket().create_ticket(data)
        except:
            OutlookConnection().send_email(to='helpdesk@bazaarvoice.com',
                                           subject='Error Publishing Extract to server Tableau export',
                                           body=error_message)


if __name__ == '__main__':
    tableau_extract = '/Users/martin.valenzuela/Downloads/BizApps_HDT_.tde'
