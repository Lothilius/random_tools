# coding: utf-8
__author__ = 'Lothilius'

import sys

from bv_authenticate.Authentication import Authentication as auth
from send_email.OutlookConnection import OutlookConnection as outlook
from tableau_data_publisher.data_assembler import TDEAssembler
from tableau_data_publisher.data_publisher import publish_data
from helper_scripts.notify_helpers import Notifier
from se_helpers.actions import wait
from lever.Candidates import Candidates
from lever.Postings import Postings
from lever.Users import Lever_Users
from lever.Requisitions import Requisitions
from os.path import basename
from datetime import datetime
from time import time


def main():
    # try:
    #     # Get users from Lever
    #     users = Lever_Users()
    #     users = users.users
    #
    #     # Package in to a tde file
    #     data_file = TDEAssembler(data_frame=users, extract_name='Lever_Users')
    #     # Set values for publishing the data.
    #     file_name = str(data_file)
    #     server_url, username, password, site_id, data_source_name, project = \
    #         auth.tableau_publishing(datasource_type='PandT', data_source_name='Lever_Users',)
    #
    #     publish_data(server_url, username, password, site_id, file_name, data_source_name, project, replace_data=True)
    # except:
    #     error_result = "Unexpected AttributeError: %s, %s"\
    #                    % (sys.exc_info()[0], sys.exc_info()[1])
    #     subject = 'Error with Tableau refresh script, %s' % basename(__file__)
    #     print error_result
    #     # outlook().send_email('helpdesk@bazaarvoice.com', cc='BizAppsIntegrations@bazaarvoice.com', subject=subject, body=error_result)
    #     give_notice = Notifier()
    #     give_notice.set_red()
    #     give_notice.wait(3)
    #     give_notice.alert_the_light()
    #     give_notice.flow_the_light()
    wait(10)
    # try:
    #     # Get posts from Lever
    #     posts = Postings()
    #     postings = posts.full_postings
    #     final_posts = postings.copy(deep=True)
    #
    #     # Package in to a tde file
    #     data_file = TDEAssembler(data_frame=final_posts, extract_name='Lever_Posts')
    #     # Set values for publishing the data.
    #     file_name = str(data_file)
    #     server_url, username, password, site_id, data_source_name, project = \
    #         auth.tableau_publishing(datasource_type='PandT', data_source_name='Lever_Posts',)
    #
    #     publish_data(server_url, username, password, site_id, file_name, data_source_name, project, replace_data=True)
    # except:
    #     error_result = "Unexpected AttributeError: %s, %s"\
    #                    % (sys.exc_info()[0], sys.exc_info()[1])
    #     subject = 'Error with Tableau refresh script, %s' % basename(__file__)
    #     print error_result
    #     # outlook().send_email('helpdesk@bazaarvoice.com', cc='BizAppsIntegrations@bazaarvoice.com', subject=subject, body=error_result)
    #     give_notice = Notifier()
    #     give_notice.set_red()
    #     give_notice.wait(3)
    #     give_notice.alert_the_light()
    #     give_notice.flow_the_light()
    wait(10)
    # try:
    #     # Get posts from Lever
    #     requisitions = Requisitions()
    #     requisitions = requisitions.full_requisitions
    #
    #     # Package in to a tde file
    #     data_file = TDEAssembler(data_frame=requisitions, extract_name='Lever_Requisitions')
    #     # Set values for publishing the data.
    #     file_name = str(data_file)
    #     server_url, username, password, site_id, data_source_name, project = \
    #         auth.tableau_publishing(datasource_type='PandT', data_source_name='Lever_Requisitions', )
    #
    #     publish_data(server_url, username, password, site_id, file_name, data_source_name, project, replace_data=True)
    # except:
    #     error_result = "Unexpected AttributeError: %s, %s" \
    #                    % (sys.exc_info()[0], sys.exc_info()[1])
    #     subject = 'Error with Tableau refresh script, %s' % basename(__file__)
    #     print error_result
    #     # outlook().send_email('helpdesk@bazaarvoice.com', cc='BizAppsIntegrations@bazaarvoice.com', subject=subject, body=error_result)
    #     give_notice = Notifier()
    #     give_notice.set_red()
    #     give_notice.wait(3)
    #     give_notice.alert_the_light()
    #     give_notice.flow_the_light()
    wait(10)
    try:
        # Get posts from Lever
        candidates = Candidates()
        candidates = candidates.full_candidates

        # Package in to a tde file
        data_file = TDEAssembler(data_frame=candidates, extract_name='Lever_Candidates')
        # Set values for publishing the data.
        file_name = str(data_file)
        server_url, username, password, site_id, data_source_name, project = \
            auth.tableau_publishing(datasource_type='PandT', data_source_name='Lever_Candidates', )

        publish_data(server_url, username, password, site_id, file_name, data_source_name, project, replace_data=True)
    except:
        error_result = "Unexpected AttributeError: %s, %s" \
                       % (sys.exc_info()[0], sys.exc_info()[1])
        subject = 'Error with Tableau refresh script, %s' % basename(__file__)
        print error_result
        # outlook().send_email('helpdesk@bazaarvoice.com', cc='BizAppsIntegrations@bazaarvoice.com', subject=subject, body=error_result)
        give_notice = Notifier()
        give_notice.set_red()
        give_notice.wait(3)
        give_notice.alert_the_light()
        give_notice.flow_the_light()
    # wait(30)

    # outlook().send_email(to='BizAppsIntegrations@bazaarvoice.com',
    #                      subject='HDT-Data update complete', body='HDT-Data update complete')

if __name__ == '__main__':
    start = time()
    main()
    end = time()
    print (end - start) / 60
    print datetime.now()
    print '-----------------\n'