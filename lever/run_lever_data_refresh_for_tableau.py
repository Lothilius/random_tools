# coding: utf-8
__author__ = 'Lothilius'

import sys
import pandas as pd
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
from lever.Archive_Reasons import Archive_Reasons
from os.path import basename
from datetime import datetime
from time import time


def main():
    try:
        testing_file_path = '/Users/martin.valenzuela/Box Sync/Documents/Austin Office/BizReqs/Lever_API_595101/'
        stage_ids = ['44015e45-bbf3-447c-8517-55fe4540acdc', 'offer']

        # Get stages from Lever
        stages = Lever_Stages()
        stages = stages.stages
        stages.set_index(['stage_id'], inplace=True)
        stages.loc['-'] = '-'

        # Get archive_reasons from Lever
        archive_reasons = Archive_Reasons()
        archive_reasons = archive_reasons.archive_reasons
        archive_reasons.set_index(['archive_reason_id'], inplace=True)
        archive_reasons.loc['-'] = '-'

        # Get users from Lever
        users = Lever_Users()
        users = users.users

        # Get posts from Lever
        posts = Postings()
        postings = posts.full_postings
        final_posts = postings.copy(deep=True)

        # Get requisitions from Lever
        requisitions = Requisitions()
        requisitions = requisitions.full_requisitions

        # Get candidates from Lever
        candidates = Candidates()
        candidate_stages_ids = candidates.stages[['candidate_id', 'toStageId']]
        candidates = candidates.full_candidates
        # Swap out if values with Label
        candidates.reason = candidates.reason.apply(lambda x: archive_reasons.loc[x])
        candidates.stage = candidates.stage.apply(lambda x: stages.loc[x])

        # Narrow candidates to only those that reaches stage_ids at some point for applications and offers
        candidates_with_offers = candidate_stages_ids[candidate_stages_ids['toStageId'].isin(stage_ids)]['candidate_id']
        candidates_with_offers = candidates_with_offers.copy()
        candidates_with_offers.drop_duplicates(inplace=True)
        # Update stage tds with labels
        candidates.toStageId = candidates.toStageId.apply(lambda x: stages.loc[x])
        # Split out a list for applications and offers
        candidates_with_applications = candidates_with_offers.tolist()
        candidates_with_offers = candidates_with_offers.tolist()

        # Get applications from Lever based on candidates having been in stages that are in stage_ids
        applications = Applications(candidate_id=candidates_with_applications)
        applications = applications.full_application
        applications = correct_date_dtype(applications, date_time_format='%Y-%m-%d %H:%M:%S',
                                          date_time_columns={'createdAt_application', 'createdAt__fields'})

        # Get offers from Lever based on candidates with Stages in stage_ids
        offers = Offers(candidate_id=candidates_with_offers)
        offers = offers.full_offer
        offers = correct_date_dtype(offers, date_time_format='%Y-%m-%d %H:%M:%S',
                                    date_time_columns={'createdAt', 'approvedAt', 'sentAt'})

        # Get requisition_fields from Lever
        requisition_fields = Requisition_Fields()
        requisition_fields = requisition_fields.requisition_fields

        # Left join candidates with offers
        candidates_and_offers = pd.merge(left=candidates, right=offers[['candidate_id', 'offer_id', 'posting']],
                                         how='left', on='candidate_id')
        candidates_with_offers = pd.merge(left=candidates_and_offers,
                                          right=postings[['post_id', 'team', 'location', 'owner']], how='left',
                                         left_on='posting', right_on='post_id', suffixes=('_candidate', '_posting'))

        try:
            # Create table array to iterate through for creation and publishing.
            extract_name = [[users, 'Lever_Users'], [final_posts, 'Lever_Posts'], [requisitions, 'Lever_Requisitions'],
                            [candidates, 'Lever_Candidates'], [stages, 'Lever_Stages'],
                            [applications, 'Lever_Applications'],
                            [requisition_fields, 'Lever_Req_Fields'], [offers, 'Lever_Offers'],
                            [archive_reasons, 'Lever_Archieve_Reasons'],
                            [candidates_with_offers, 'Lever_Candidates_with_Offers_Posts']]

            file_names_to_publish = {}

            for table in extract_name:
                # Package in to a tde file
                data_file = TDEAssembler(data_frame=table[0],
                                         file_path=testing_file_path,
                                         extract_name=table[1])
                # Set values for publishing the data.
                file_names_to_publish[table[1]] = str(data_file)

                print table[1], "\n", str(data_file), "\n-------------\n\n"
        except:
            error_result = "Error building tableau extract. Unexpected Error: %s, %s" \
                           % (sys.exc_info()[0], sys.exc_info()[1])
            subject = 'Error with Tableau refresh script, tableau extract, %s' % basename(__file__)
            print error_result
            # outlook().send_email('helpdesk@bazaarvoice.com', cc='BizAppsIntegrations@bazaarvoice.com', subject=subject, body=error_result)
            give_notice = Notifier()
            give_notice.set_red()
            give_notice.wait(3)
            give_notice.set_error_light()
            give_notice.flow_the_light()


    except:
        error_result = "Unexpected Error: %s, %s"\
                       % (sys.exc_info()[0], sys.exc_info()[1])
        subject = 'Error with Tableau refresh script, %s' % basename(__file__)
        print error_result
        # outlook().send_email('helpdesk@bazaarvoice.com', cc='BizAppsIntegrations@bazaarvoice.com', subject=subject, body=error_result)
        give_notice = Notifier()
        give_notice.set_red()
        give_notice.wait(3)
        give_notice.set_error_light()
        give_notice.flow_the_light()



    # try:
    #
    #     for table_name in extract_name:
    #         server_url, username, password, site_id, data_source_name, project = \
    #             auth.tableau_publishing(datasource_type='PandT', data_source_name=table_name[1])
    #
    #         # publish_data(server_url, username, password, site_id, file_names_to_publish[table_name[1]], data_source_name, project, replace_data=True)
    #     # outlook().send_email(to='BizAppsIntegrations@bazaarvoice.com',
    #     #                      subject='HDT-Data update complete', body='HDT-Data update complete')
    #
    # except:
    #     error_result = "Error publishing tableau extracts. Unexpected Error: %s, %s"\
    #                    % (sys.exc_info()[0], sys.exc_info()[1])
    #     subject = 'Error with Tableau refresh script, %s' % basename(__file__)
    #     print error_result
    #     # outlook().send_email('helpdesk@bazaarvoice.com', cc='BizAppsIntegrations@bazaarvoice.com', subject=subject, body=error_result)
    #     give_notice = Notifier()
    #     give_notice.set_red()
    #     give_notice.wait(3)
    #     give_notice.set_error_light()
    #     give_notice.flow_the_light()

if __name__ == '__main__':
    start = time()
    main()
    end = time()
    print (end - start) / 60
    print datetime.now()
    print '-----------------\n'