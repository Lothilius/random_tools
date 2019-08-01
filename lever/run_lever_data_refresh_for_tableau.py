# coding: utf-8
__author__ = 'Lothilius'

import sys
import pandas as pd
from bv_authenticate.Authentication import Authentication as auth
from send_email.OutlookConnection import OutlookConnection as outlook
from tableau_data_publisher.data_assembler_hyper import HyperAssembler
from tableau_data_publisher.Tableau import Tableau
from helper_scripts.notify_helpers import Notifier
from helper_scripts.misc_helpers.data_manipulation import correct_date_dtype
from lever import *
from os.path import basename
from os import environ
from os import remove
from datetime import datetime
from time import time
from triage_tickets.Ticket import Ticket
import traceback
import socket

if environ['MY_ENVIRONMENT'] == 'prod':
    file_path = '/var/shared_folder/PandT/Tableau_data/'
    project = 'Recruiting'
else:
    file_path = '/Users/%s/Downloads/' % environ['USER']
    project = 'Testing'

try:
    give_notice = Notifier()
except:
    pass


def main():
    hired_and_offer_stage_ids = ['44015e45-bbf3-447c-8517-55fe4540acdc', 'offer']

    today = datetime.today()
    current_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    beginning_of_three_months_ago = current_month - pd.offsets.MonthBegin(3)
    beginning_of_three_months_ago = beginning_of_three_months_ago.value / 1000000

    try:
        # Get stages from Lever
        stages = Lever_Stages()
        stages = stages.stages
        stages = stages.append([{'stage_id': '4ddfa41f-8cf2-4648-9780-21923247c3f3',
                                 'text': 'Recruiter Qualified'},
                                {'stage_id': '0798c37a-2a2f-4978-88ac-8af174a5a2e8',
                                 'text': 'Hiring Manager Qualified'},
                                {'stage_id': '32c7f46d-8921-4752-8091-a207199d60c0',
                                 'text': 'Contact Candidate'},
                                {'stage_id': '44015e45-bbf3-447c-8517-55fe4540acdc',
                                 'text': 'Background Check'}
                                ])
        stages.set_index(['stage_id'], inplace=True)
        stages.loc['-'] = '-'

        # Get archive_reasons from Lever
        archive_reasons = Archive_Reasons()
        archive_reasons = archive_reasons.archive_reasons
        archive_reasons.set_index(['archive_reason_id'], inplace=True)
        archive_reasons.loc['-'] = '-'

        # Combine Stage and Archive reasons
        stage_and_archive_reasons = pd.merge(left=stages, right=archive_reasons, how='outer', on='text',
                                             left_index=True, right_index=True)

        # Get requisition_fields from Lever
        requisition_fields = Requisition_Fields()
        requisition_fields = requisition_fields.requisition_fields

        # Get user from Lever
        users = Lever_Users()
        users = users.users

        # Get posts from Lever
        posts = Postings()
        postings = posts.full_postings[['categories', 'content', 'createdAt', 'followers', 'hiringManager', 'post_id',
                                        'owner', 'reqCode', 'state', 'tags', 'text', 'updatedAt', 'urls', 'user',
                                        'commitment', 'department', 'level', 'location', 'team', 'closing',
                                        'closingHtml', 'customQuestions', 'description', 'descriptionHtml', 'lists']]
        final_posts = postings.copy(deep=True)
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        error_result = "Unexpected Error: %s, %s, %s" \
                       % (exc_type, exc_value, traceback.format_exc())
        subject = 'Error with Tableau refresh script, Failed to gather supporting tables %s' % basename(__file__)
        print error_result

        # TODO- Log errors in to table then send only one email to HD
        outlook().create_helpdesk_ticket(cc='BizAppsIntegrations@bazaarvoice.com',
                                         subject=subject, body=error_result)
        give_notice = Notifier()
        give_notice.set_red()
        give_notice.wait(3)
        give_notice.set_error_light()
        give_notice.flow_the_light()

    try:

        # Get candidates from Lever
        candidates = Candidates(date_limit=beginning_of_three_months_ago)
        candidate_stages_ids = candidates.stages[['candidate_id', 'toStageId']]
        candidates_full_columns = candidates.full_candidates[['applications', 'archived', 'createdAt',
                                                              'emails', 'followers', 'headline', 'candidate_id',
                                                              'lastAdvancedAt', 'lastInteractionAt', 'links',
                                                              'location',
                                                              'name', 'origin', 'owner', 'phones', 'snoozedUntil',
                                                              'sources', 'stage', 'stageChanges', 'tags', 'urls',
                                                              'archivedAt', 'reason', 'applications_as_feature_column',
                                                              'toStageId', 'toStageIndex', 'updatedAt', 'userId']]

        candidates_full = candidates_full_columns.copy()
        # Swap out if values with Label
        candidates_full['reason'] = candidates_full['reason'].apply(lambda x: stage_and_archive_reasons.loc[x])
        candidates_full['stage'] = candidates_full['stage'].apply(lambda x: stage_and_archive_reasons.loc[x])

        # Narrow candidates to only those that reach stage_ids at some point for applications and offers
        candidates_with_offers = candidate_stages_ids[candidate_stages_ids['toStageId']
            .isin(hired_and_offer_stage_ids)]['candidate_id']
        candidates_with_offers = candidates_with_offers.copy()
        candidates_with_offers.drop_duplicates(inplace=True)
        # Update stage tds with labels
        candidates_full['toStageId'] = candidates_full['toStageId'].apply(lambda x: stage_and_archive_reasons.loc[x])
        # Split out a list for applications and offers
        candidates_with_offers = candidates_with_offers.tolist()
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        error_result = "Unexpected Error: %s, %s, %s" \
                       % (exc_type, exc_value, traceback.format_exc())
        subject = 'Error with Tableau refresh script, Failed to gather candidates %s' % basename(__file__)
        print error_result
        outlook().create_helpdesk_ticket(cc='BizAppsIntegrations@bazaarvoice.com',
                                         subject=subject, body=error_result)
        give_notice = Notifier()
        give_notice.set_red()
        give_notice.wait(3)
        give_notice.set_error_light()
        give_notice.flow_the_light()

    try:
        # Get offers from Lever based on candidates with Stages in hired_and_offer_stage_ids
        offers = Offers(candidate_id=candidates_with_offers)
        offers_full = offers.full_offer
        offers_full = correct_date_dtype(offers_full, date_time_format='%Y-%m-%d %H:%M:%S',
                                         date_time_columns={'createdAt', 'approvedAt', 'sentAt'})

        print offers_full.columns
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        error_result = "Unexpected Error: %s, %s, %s" \
                       % (exc_type, exc_value, traceback.format_exc())
        subject = 'Error with Tableau refresh script, Failed to gather offers %s' % basename(__file__)
        print error_result
        outlook().create_helpdesk_ticket(cc='BizAppsIntegrations@bazaarvoice.com',
                                         subject=subject, body=error_result)
        give_notice = Notifier()
        give_notice.set_red()
        give_notice.wait(3)
        give_notice.set_error_light()
        give_notice.flow_the_light()

    try:
        # Get requisitions from Lever
        requisitions = Requisitions()
        requisitions_full = requisitions.full_requisitions
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        error_result = "Unexpected Error: %s, %s, %s" \
                       % (exc_type, exc_value, traceback.format_exc())
        subject = 'Error with Tableau refresh script, Failed to gather requisitions %s' % basename(__file__)
        print error_result
        outlook().create_helpdesk_ticket(cc='BizAppsIntegrations@bazaarvoice.com',
                                         subject=subject, body=error_result)
        give_notice = Notifier()
        give_notice.set_red()
        give_notice.wait(3)
        give_notice.set_error_light()
        give_notice.flow_the_light()
    try:
        # Left join candidates with offers
        candidates_and_offers = pd.merge(left=candidates_full,
                                         right=offers_full[['candidate_id', 'offer_id',
                                                            'posting', 'Type', 'Commission amount']],
                                         how='left', on='candidate_id')
        candidates_with_offers = pd.merge(left=candidates_and_offers,
                                          right=postings[['post_id', 'team', 'location', 'owner', 'reqCode']],
                                          how='outer', left_on='posting', right_on='post_id',
                                          suffixes=('_candidate', '_posting'))
        candidates_for_offers = correct_date_dtype(candidates_with_offers, date_time_format='%Y-%m-%d %H:%M:%S',
                                                   date_time_columns={'archivedAt', 'createdAt', 'updatedAt_posts',
                                                                      'createdAt_posts', 'lastAdvancedAt',
                                                                      'snoozedUntil', 'updatedAt',
                                                                      'lastInteractionAt'})
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        error_result = "Unexpected Error: %s, %s, %s" \
                       % (exc_type, exc_value, traceback.format_exc())
        subject = 'Error with Tableau refresh script, Failed to gather candidates wiht offers %s' % basename(__file__)
        print error_result
        outlook().create_helpdesk_ticket(cc='BizAppsIntegrations@bazaarvoice.com',
                                         subject=subject, body=error_result)
        give_notice = Notifier()
        give_notice.set_red()
        give_notice.wait(3)
        give_notice.set_error_light()
        give_notice.flow_the_light()

    try:
        """ Left join requisition data with candidates"""
        # Gather limited data on Candidates
        candidates_for_heatmap = candidates.candidates[['candidate_id', 'archivedAt', 'reason']]

        # Left join Offers data with Candidates
        candidates_for_heatmap_with_offers = pd.merge(left=candidates_for_heatmap,
                                                      right=offers_full[['candidate_id', 'offer_id', 'posting',
                                                                         'Type']],
                                                      how='left', on='candidate_id', suffixes=('_candidate', '_offer'))
        candidates_for_heatmap_with_offers.rename(columns={'posting': 'post_id'}, inplace=True)
        # Left join Posting data with Candidates
        candidates_for_heatmap_with_offers_posts = pd.merge(left=candidates_for_heatmap_with_offers,
                                                            right=postings[['post_id', 'tags', 'owner', 'updatedAt',
                                                                            'createdAt']],
                                                            how='outer', on='post_id',
                                                            suffixes=('_candidate', '_posts'))
        candidates_for_heatmap_with_offers_posts.fillna(value='-', inplace=True)
        candidates_for_heatmap_with_offers_posts = candidates_for_heatmap_with_offers_posts.copy(deep=True)
        candidates_for_heatmap_with_offers_posts.rename(columns={'owner': 'owner_posting',
                                                                 'updatedAt': 'updatedAt_posts',
                                                                 'createdAt': 'createdAt_posts'}, inplace=True)
        # Reduce row count
        candidates_for_heatmap_with_offers_posts.sort_values(by=['post_id', 'tags', 'Type'], inplace=True)
        candidates_for_heatmap_with_offers_posts.drop_duplicates(subset=['post_id'], inplace=True)

        # Gather requisitions for joining with the candidates
        requisitions_prep_for_heatmap = requisitions.requisitions[['team',
                                                                   'postings_as_feature_column',
                                                                   'requisition_id',
                                                                   'location',
                                                                   'offerIds',
                                                                   'createdAt',
                                                                   'name',
                                                                   'creator',
                                                                   'owner',
                                                                   'status',
                                                                   'hiringManager',
                                                                   'requisitionCode']].copy(deep=True)

        requisitions_prep_for_heatmap.rename(columns={'postings_as_feature_column': 'post_id'}, inplace=True)
        requisitions_prep_for_heatmap_candidates_offers_posts = pd.merge(left=requisitions_prep_for_heatmap,
                                                                         right=candidates_for_heatmap_with_offers_posts,
                                                                         how='left', on='post_id',
                                                                         suffixes=('_requisition', '_candidate'))
        requisitions_for_heatmap = requisitions_prep_for_heatmap_candidates_offers_posts.copy(deep=True)
        requisitions_for_heatmap.sort_values(by=['updatedAt_posts', 'tags', 'Type'], inplace=True)
        requisitions_for_heatmap.drop_duplicates(subset=['requisition_id'], inplace=True)

        # Clean up date columns
        requisitions_for_heatmap = correct_date_dtype(requisitions_for_heatmap, date_time_format='%Y-%m-%d %H:%M:%S',
                                                      date_time_columns={'archivedAt', 'createdAt', 'updatedAt_posts',
                                                                         'createdAt_posts'})
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        error_result = "Unexpected Error: %s, %s, %s" \
                       % (exc_type, exc_value, traceback.format_exc())
        subject = 'Error with Tableau refresh script, Failed to gather Requisitions for Heatmaps %s' \
                  % basename(__file__)
        print error_result
        outlook().create_helpdesk_ticket(cc='BizAppsIntegrations@bazaarvoice.com',
                                         subject=subject, body=error_result)
        give_notice = Notifier()
        give_notice.set_red()
        give_notice.wait(3)
        give_notice.set_error_light()
        give_notice.flow_the_light()

    try:

        offers_full.drop(columns=[''], axis=1, inplace=True)

        # Create table array to iterate through for creation and publishing.
        extract_name = [[offers_full, 'Lever_Offers'],
                        [users, 'Lever_Users'],
                        [final_posts, 'Lever_Posts'],
                        [requisitions_full, 'Lever_Requisitions'],
                        [candidates_full, 'Lever_Candidates'],
                        [stages, 'Lever_Stages'],
                        [requisition_fields, 'Lever_Req_Fields'],
                        [archive_reasons, 'Lever_Archieve_Reasons'],
                        [candidates_for_offers, 'Lever_Candidates_with_Offers_Posts'],
                        [requisitions_for_heatmap, 'Lever_Requisitions_with_Candidates_data_for_Heatmap']]

        file_names_to_publish = {}

        for table in extract_name:
            # Package in to a tde file
            data_file = HyperAssembler(data_frame=table[0], extract_name=table[1], file_path=file_path)

            # Set values for publishing the data.
            file_names_to_publish[table[1]] = data_file.file_name

            print table[1], "\n", str(data_file), "\n-------------\n\n"
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        error_result = "Unexpected Error: %s, %s, %s" \
                       % (exc_type, exc_value, traceback.format_exc())
        subject = 'Error creating Extracts in Tableau refresh script, %s on Server %s' % (basename(__file__),
                                                                                          socket.gethostname())
        error_result += subject

        print error_result
        try:
            data = {'REQUESTEREMAIL': 'martin.valenzuela@bazaarvoice.com',
                    'REQUESTER': 'Martin Valenzuela',
                    'DESCRIPTION': error_result,
                    'SUBJECT': subject}
            Ticket().create_ticket(data)
        except:
            outlook().send_email('martin.valenzuela@bazaarvoice.com', cc='BizAppsIntegrations@bazaarvoice.com', subject=subject,
                                 body=error_result)
        give_notice = Notifier()
        give_notice.set_red()
        give_notice.wait(3)
        give_notice.set_error_light()
        give_notice.flow_the_light()

    try:
        tableau_server = Tableau(server_url='https://tableau.bazaarvoice.com/', site_id='PeopleandTalent')
        tableau_old = Tableau(server_url='https://tableauserver.bazaarvoice.com/', site_id='PeopleandTalent')
        for table_name in extract_name:
            tableau_server.publish_datasource(project=project,
                                              file_path=file_names_to_publish[table_name[1]],
                                              mode='Append', name=table_name[1])
            tableau_old.publish_datasource(project=project,
                                              file_path=file_names_to_publish[table_name[1]],
                                              mode='Append', name=table_name[1])

            remove(file_names_to_publish[table_name[1]])

        outlook().send_email(to='BizAppsIntegrations@bazaarvoice.com',
                             subject='Lever-Data update complete', body='Lever-Data update complete')

    except:
        error_result = "Unexpected AttributeError: %s, %s" \
                       % (sys.exc_info()[0], sys.exc_info()[1])
        subject = 'Error with Tableau refresh script, %s on Server %s' % (basename(__file__), socket.gethostname())
        error_result += subject
        print error_result
        try:
            data = {'REQUESTEREMAIL': 'martin.valenzuela@bazaarvoice.com',
                    'REQUESTER': 'Martin Valenzuela',
                    'DESCRIPTION': error_result,
                    'SUBJECT': subject}
            Ticket().create_ticket(data)
        except:
            outlook().send_email('martin.valenzuela@bazaarvoice.com', cc='BizAppsIntegrations@bazaarvoice.com', subject=subject,
                                 body=error_result)
            give_notice = Notifier()
            give_notice.set_red()
            give_notice.wait(3)
            give_notice.set_error_light()
            give_notice.flow_the_light()


if __name__ == '__main__':
    start = time()
    main()
    end = time()
    print (end - start) / 60
    print datetime.now()
    print '-----------------\n'
