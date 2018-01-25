# coding: utf-8
__author__ = 'Lothilius'

import sys

from bv_authenticate.Authentication import Authentication as auth
from send_email.OutlookConnection import OutlookConnection as outlook
from tableau_data_publisher.data_assembler import TDEAssembler
from tableau_data_publisher.data_publisher import publish_data
from helper_scripts.notify_helpers import Notifier
from helper_scripts.misc_helpers.data_manipulation import correct_date_dtype
from se_helpers.actions import wait
from lever.Candidates import Candidates
from lever.Postings import Postings
from lever.Offers import Offers
from lever.Users import Lever_Users
from lever.Stages import Lever_Stages
from lever.Requisitions import Requisitions
from lever.Applications import Applications
from lever.Requisition_Fields import Requisition_Fields
from os.path import basename
from datetime import datetime
from time import time


def main():
    testing_file_path = '/Users/martin.valenzuela/Box Sync/Documents/Austin Office/BizReqs/Lever_API_595101/'
    try:
        # Get users from Lever
        users = Lever_Users()
        users = users.users

        # Package in to a tde file
        data_file = TDEAssembler(data_frame=users,
                                 file_path=testing_file_path,
                                 extract_name='Lever_Users')
        # Set values for publishing the data.
        file_name = str(data_file)
        server_url, username, password, site_id, data_source_name, project = \
            auth.tableau_publishing(datasource_type='PandT', data_source_name='Lever_Users')

        publish_data(server_url, username, password, site_id, file_name, data_source_name, project, replace_data=True)
    except:
        error_result = "Unexpected AttributeError: %s, %s"\
                       % (sys.exc_info()[0], sys.exc_info()[1])
        subject = 'Error with Tableau refresh script, %s' % basename(__file__)
        print error_result
        # outlook().send_email('helpdesk@bazaarvoice.com', cc='BizAppsIntegrations@bazaarvoice.com', subject=subject, body=error_result)
        give_notice = Notifier()
        give_notice.set_red()
        give_notice.wait(3)
        give_notice.alert_the_light()
        give_notice.flow_the_light()
    wait(10)
    try:
        # Get posts from Lever
        posts = Postings()
        postings = posts.full_postings
        final_posts = postings.copy(deep=True)

        # Package in to a tde file
        data_file = TDEAssembler(data_frame=final_posts,
                                 file_path=testing_file_path,
                                 extract_name='Lever_Posts')
        # Set values for publishing the data.
        file_name = str(data_file)
        server_url, username, password, site_id, data_source_name, project = \
            auth.tableau_publishing(datasource_type='PandT', data_source_name='Lever_Posts',)

        publish_data(server_url, username, password, site_id, file_name, data_source_name, project, replace_data=True)
    except:
        error_result = "Unexpected AttributeError: %s, %s"\
                       % (sys.exc_info()[0], sys.exc_info()[1])
        subject = 'Error with Tableau refresh script, %s' % basename(__file__)
        print error_result
        # outlook().send_email('helpdesk@bazaarvoice.com', cc='BizAppsIntegrations@bazaarvoice.com', subject=subject, body=error_result)
        give_notice = Notifier()
        give_notice.set_red()
        give_notice.wait(3)
        give_notice.alert_the_light()
        give_notice.flow_the_light()
    wait(10)
    try:
        # Get posts from Lever
        requisitions = Requisitions()
        requisitions = requisitions.full_requisitions

        # Package in to a tde file
        data_file = TDEAssembler(data_frame=requisitions,
                                 file_path=testing_file_path,
                                 extract_name='Lever_Requisitions')
        # Set values for publishing the data.
        file_name = str(data_file)
        server_url, username, password, site_id, data_source_name, project = \
            auth.tableau_publishing(datasource_type='PandT', data_source_name='Lever_Requisitions')

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
    wait(10)
    try:
        # Get posts from Lever
        candidates = Candidates()
        candidate_stages_ids = candidates.candidates[['candidate_id', 'stage']]
        candidates = candidates.full_candidates
        # Package in to a tde file
        data_file = TDEAssembler(data_frame=candidates,
                                 file_path=testing_file_path,
                                 extract_name='Lever_Candidates')
        # Set values for publishing the data.
        file_name = str(data_file)
        server_url, username, password, site_id, data_source_name, project = \
            auth.tableau_publishing(datasource_type='PandT', data_source_name='Lever_Candidates')

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
    wait(10)
    try:
        # Get posts from Lever
        stages = Lever_Stages()
        stages = stages.stages

        # Package in to a tde file
        data_file = TDEAssembler(data_frame=stages,
                                 file_path=testing_file_path,
                                 extract_name='Lever_Stages')
        # Set values for publishing the data.
        file_name = str(data_file)
        server_url, username, password, site_id, data_source_name, project = \
            auth.tableau_publishing(datasource_type='PandT', data_source_name='Lever_Stages')

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
    wait(10)
    try:
        stage_ids = ['44015e45-bbf3-447c-8517-55fe4540acdc', 'offer']

        candidates_with_offers = candidate_stages_ids[candidate_stages_ids['stage'].isin(stage_ids)]['candidate_id'].tolist()

        # Get applications from Lever based on candidates with Stages in stage_ids
        applications = Applications(candidate_id=candidates_with_offers)
        applications = applications.full_application
        applications = correct_date_dtype(applications, date_time_format='%Y-%m-%d %H:%M:%S',
                                               date_time_columns={'createdAt_application', 'createdAt__fields'})

        # Package in to a tde file
        data_file = TDEAssembler(data_frame=applications,
                                 file_path=testing_file_path,
                                 extract_name='Lever_Applications')
        # Set values for publishing the data.
        file_name = str(data_file)
        server_url, username, password, site_id, data_source_name, project = \
            auth.tableau_publishing(datasource_type='PandT', data_source_name='Lever_Applications')

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
    wait(10)
    try:
        # Get posts from Lever
        requisition_fields = Requisition_Fields()
        requisition_fields = requisition_fields.requisition_fields

        # Package in to a tde file
        data_file = TDEAssembler(data_frame=requisition_fields,
                                 file_path=testing_file_path,
                                 extract_name='Lever_Req_Fields')
        # Set values for publishing the data.
        file_name = str(data_file)
        server_url, username, password, site_id, data_source_name, project = \
            auth.tableau_publishing(datasource_type='PandT', data_source_name='Lever_Req_Fields')

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
        wait(10)
    try:
        # Get applications from Lever based on candidates with Stages in stage_ids
        offers = Offers(candidate_id=candidates_with_offers)
        offers = offers.full_offer
        offers = correct_date_dtype(offers, date_time_format='%Y-%m-%d %H:%M:%S',
                                               date_time_columns={'createdAt', 'approvedAt', 'sentAt'})

        # Package in to a tde file
        data_file = TDEAssembler(data_frame=offers,
                                 file_path=testing_file_path,
                                 extract_name='Lever_Offers')
        # Set values for publishing the data.
        file_name = str(data_file)
        server_url, username, password, site_id, data_source_name, project = \
            auth.tableau_publishing(datasource_type='PandT', data_source_name='Lever_Offers')

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

    # outlook().send_email(to='BizAppsIntegrations@bazaarvoice.com',
    #                      subject='HDT-Data update complete', body='HDT-Data update complete')

if __name__ == '__main__':
    start = time()
    main()
    end = time()
    print (end - start) / 60
    print datetime.now()
    print '-----------------\n'