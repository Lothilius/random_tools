# coding: utf-8
__author__ = 'Lothilius'

import sys
import pandas as pd
from bv_authenticate.Authentication import Authentication as auth
from send_email.OutlookConnection import OutlookConnection as outlook
from tableau_data_publisher.data_assembler import TDEAssembler
from tableau_data_publisher.Tableau import Tableau
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
from os import path
from os import environ
from datetime import datetime
from time import time
import traceback


if environ['MY_ENVIRONMENT'] == 'prod':
    file_path = '/var/shared_folder/PandT/Tableau_data/'
    project = 'Recruiting'
else:
    file_path = '/Users/%s/Downloads/' % environ['USER']
    project = 'Testing'

def main():
    hired_and_offer_stage_ids = ['44015e45-bbf3-447c-8517-55fe4540acdc', 'offer']
    funnel_stage_ids = ['applicant-new', 'lead-responded', '5cd295db-095a-438b-8ebb-02be04c5d219',
                        '1b38aea1-5a7c-44e2-87cd-7058b6400cb0', '5e860f8b-acc1-40df-966e-748318285dc2',
                        '944e0470-7698-49be-85ec-3051c7e860ca', 'f46f4de3-aea1-41c0-9a2c-9c31ab0c5b59',
                        '44015e45-bbf3-447c-8517-55fe4540acdc', 'offer']
    today = datetime.today()
    current_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    beginning_of_three_months_ago = current_month - pd.offsets.MonthBegin(3)
    print beginning_of_three_months_ago
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

        # Get posts from Lever
        posts = Postings()
        postings = posts.full_postings
        final_posts = postings.copy(deep=True)
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        error_result = "Unexpected Error: %s, %s, %s"\
                       % (exc_type, exc_value, traceback.format_exc())
        subject = 'Error with Tableau refresh script, Failed to gather supporting tables %s' % path.basename(__file__)
        print error_result

        # TODO- Log errors in to table then send only one email to HD
        outlook().send_email('helpdesk@bazaarvoice.com', cc='BizAppsIntegrations@bazaarvoice.com',
                             subject=subject, body=error_result)
        give_notice = Notifier()
        give_notice.set_red()
        give_notice.wait(3)
        give_notice.set_error_light()
        give_notice.flow_the_light()

    try:
        # Get candidates from Lever
        candidates = Candidates(date_limit=beginning_of_three_months_ago)
        candidate_stages_ids = candidates.stages[['candidate_id', 'toStageId', 'updatedAt']]
        candidates_full = candidates.full_candidates
        # Swap out if values with Label
        candidates_full['reason'] = candidates_full['reason'].apply(lambda x: stage_and_archive_reasons.loc[x])
        candidates_full['stage'] = candidates_full['stage'].apply(lambda x: stage_and_archive_reasons.loc[x])

        # Narrow candidates to only those that reach hired_and_offer_stage_ids at some point for offers
        candidates_for_offers = candidate_stages_ids[
            candidate_stages_ids['toStageId'].isin(hired_and_offer_stage_ids)]['candidate_id']
        candidates_for_offers = candidates_for_offers.copy()
        candidates_for_offers.drop_duplicates(inplace=True)

        # Narrow candidates to only those that reach funnel stages at some point from applications to hired
        candidates_for_applications = candidate_stages_ids[
            candidate_stages_ids['toStageId'].isin(funnel_stage_ids)]
        candidates_for_applications = candidates_for_applications.copy(deep=True)
        candidates_for_applications.drop_duplicates(inplace=True)


        # Update stage ids with labels
        candidates_full['toStageId'] = candidates_full['toStageId'].apply(lambda x: stage_and_archive_reasons.loc[x])
        # Split out a list for applications and offers
        candidates_with_applications = candidates_for_applications['candidate_id'].tolist()
        candidates_with_offers = candidates_for_offers.tolist()

    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        error_result = "Unexpected Error: %s, %s, %s"\
                       % (exc_type, exc_value, traceback.format_exc())
        subject = 'Error with Tableau refresh script, Failed to gather candidates %s' % path.basename(__file__)
        print error_result
        outlook().send_email('helpdesk@bazaarvoice.com', cc='BizAppsIntegrations@bazaarvoice.com',
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
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        error_result = "Unexpected Error: %s, %s, %s"\
                       % (exc_type, exc_value, traceback.format_exc())
        subject = 'Error with Tableau refresh script, Failed to gather offers %s' % path.basename(__file__)
        print error_result
        outlook().send_email('helpdesk@bazaarvoice.com', cc='BizAppsIntegrations@bazaarvoice.com',
                             subject=subject, body=error_result)
        give_notice = Notifier()
        give_notice.set_red()
        give_notice.wait(3)
        give_notice.set_error_light()
        give_notice.flow_the_light()

    try:
        # Get applications from Lever based on candidates having been in stages that are in hired_and_offer_stage_ids
        applications = Applications(candidate_id=candidates_with_applications)
        applications = applications.full_application
        applications = correct_date_dtype(applications, date_time_format='%Y-%m-%d %H:%M:%S',
                                          date_time_columns={'createdAt_application', 'createdAt__fields'})
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        error_result = "Unexpected Error: %s, %s, %s"\
                       % (exc_type, exc_value, traceback.format_exc())
        subject = 'Error with Tableau refresh script, Failed to gather applications%s' % path.basename(__file__)
        print error_result
        outlook().send_email('helpdesk@bazaarvoice.com', cc='BizAppsIntegrations@bazaarvoice.com',
                             subject=subject, body=error_result)
        give_notice = Notifier()
        give_notice.set_red()
        give_notice.wait(3)
        give_notice.set_error_light()
        give_notice.flow_the_light()


    try:
        # Left join candidates with applications
        applications_and_candidates = pd.merge(left=applications,
                                               right=candidates_full,
                                               how='outer', left_on='candidateId', right_on='candidate_id',
                                               suffixes=('_application', '_candidate'))
        applications_and_candidates_and_offers = pd.merge(left=applications_and_candidates,
                                         right=offers_full[['candidate_id', 'offer_id',
                                                            'posting', 'Type', 'Commission amount']],
                                         how='left', on='candidate_id', suffixes=('_a_c', '_offer'))
        candidates_for_funnel = pd.merge(left=applications_and_candidates_and_offers,
                                         right=postings[['post_id', 'team', 'location', 'owner', 'reqCode']],
                                         how='outer', left_on='posting_a_c', right_on='post_id',
                                         suffixes=('_a_c_o', '_posting'))
        candidates_for_funnel = correct_date_dtype(candidates_for_funnel, date_time_format='%Y-%m-%d %H:%M:%S',
                                                   date_time_columns={'archivedAt', 'createdAt', 'updatedAt_posts',
                                                                      'createdAt_posts', 'lastAdvancedAt',
                                                                      'snoozedUntil', 'updatedAt',
                                                                      'lastInteractionAt'})
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        error_result = "Unexpected Error: %s, %s, %s" \
                       % (exc_type, exc_value, traceback.format_exc())
        subject = 'Error with Tableau refresh script, Failed to gather candidates wiht offers %s' % path.basename(
            __file__)
        print error_result
        outlook().send_email('helpdesk@bazaarvoice.com', cc='BizAppsIntegrations@bazaarvoice.com',
                             subject=subject, body=error_result)
        give_notice = Notifier()
        give_notice.set_red()
        give_notice.wait(3)
        give_notice.set_error_light()
        give_notice.flow_the_light()


    try:
        # Create table array to iterate through for creation and publishing.
        extract_name = [[applications, 'Lever_Applications'],
                        [candidates_for_funnel, 'Lever_Funnel_Data']]

        file_names_to_publish = {}

        for table in extract_name:
            # Package in to a tde file
            data_file = TDEAssembler(data_frame=table[0],
                                     extract_name=table[1])
            # Set values for publishing the data.
            file_names_to_publish[table[1]] = str(data_file)

            print table[1], "\n", str(data_file), "\n-------------\n\n"
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        error_result = "Unexpected Error: %s, %s, %s"\
                       % (exc_type, exc_value, traceback.format_exc())
        subject = 'Error with Tableau refresh script, Failed to create tableau extract, %s' % path.basename(__file__)
        print error_result
        outlook().send_email('helpdesk@bazaarvoice.com', cc='BizAppsIntegrations@bazaarvoice.com',
                             subject=subject, body=error_result)
        give_notice = Notifier()
        give_notice.set_red()
        give_notice.wait(3)
        give_notice.set_error_light()
        give_notice.flow_the_light()


    try:
        tableau_server = Tableau(server_url='https://tableau.bazaarvoice.com/', site_id='PeopleandTalent')
        for table_name in extract_name:
            tableau_server.publish_datasource(project=project,
                                              file_path=file_names_to_publish[table_name[1]],
                                              mode='Append', name=table_name[1])
        outlook().send_email(to='BizAppsIntegrations@bazaarvoice.com',
                             subject='Lever-Data update complete', body='Lever-Data update complete')

    except:
        error_result = "Error publishing tableau extracts. Unexpected Error: %s, %s"\
                       % (sys.exc_info()[0], sys.exc_info()[1])
        subject = 'Error with Tableau refresh script, %s' % path.basename(__file__)
        print error_result
        outlook().send_email('helpdesk@bazaarvoice.com', cc='BizAppsIntegrations@bazaarvoice.com',
                             subject=subject, body=error_result)
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