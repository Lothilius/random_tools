# coding: utf-8
__author__ = 'Lothilius'


import sys

from bv_authenticate.Authentication import Authentication as auth
from send_email.OutlookConnection import OutlookConnection as outlook
from tableau_data_publisher.data_assembler import TDEAssembler
from tableau_data_publisher.data_publisher import publish_data
from helper_scripts.notify_helpers import Notifier
from okta.Okta_Group_Members import Okta_Group_Members
from os import remove
from os.path import basename
from time import time
from datetime import datetime
import pandas as pd

work_day_groups = {'WD-Active-CW-Agency': '00gvbnj7mxFBXWJLBWBT',
                   'WD-Active-Employee-Expat': '00gvbnj7m7XOGGYTQIXA',
                   'WD-Active-Employee-Flex': '00gvbnj7lgJYQBLIRPFJ',
                   'WD-Active-Employee-Flex-Coach': '00g113s3nxaIhIxLn0i8',
                    'WD-Active-Employee-Regular': '00gvbnj7lvHDVBBJVPAY',
                    'WD-Active-Employee-Temp': '00gvbnj7l5BJKRDXFMGE',
                    'WD-Active-Employee-Intern': '00gvbnj7mgAHCODJODGH',
                   'WD-Active-CW-Consultant': '00gy9hrcgsZJOXSDQUFH',
                   'WD-Active-CW-Independent': '00gvbnj7mlCYMECZUACB',
                   'WD-Active-CW-Outsourced': '00gy9hrcguWNFPCLSFDD',
                   'WD-Active-CW-VendorService': '00gvbnj7mpPXFTBEWRNH'
                   }
m_f_group = '00gcy0wldkSLIQJLRDDU'

def main():
    try:
        all_wd_employees = []
        for each in work_day_groups.keys():
            # Get Users from Okta that are in the list of Workday groups
            mfa_users = Okta_Group_Members(group_id=work_day_groups[each])
            mfa_employees = mfa_users.group_members
            all_wd_employees.append(mfa_employees)

        all_wd_employees = pd.concat(all_wd_employees, ignore_index=True)


        # Get Users from Okta that are in mfa-everywhere group
        mfa_users = Okta_Group_Members(group_id=m_f_group)
        mfa_employees = mfa_users.group_members

        # Do an left outer join so all Workday employees and their MFA profiles are matched up
        left_wd_join = pd.merge(left=all_wd_employees, right=mfa_employees[['email', 'login']], how='left', on='email',
                              suffixes=('_wd', '_mfa'))

        # Any Null in login_mfa column are not in MFA group.
        employees_without_mfa = left_wd_join[left_wd_join['login_mfa'].isnull()].copy()

        print employees_without_mfa
        file_name = '/Users/martin.valenzuela/Box Sync/Documents/Austin Office/Data/users_needing_mfa.csv'
        employees_without_mfa.to_csv(file_name, index=False)

        email = outlook()

        email.send_email(to="adrian.brown@bazaarvoice.com", cc='martin.valenzuela@bazaarvoice.com',
                         subject='Users not in MFA',
                         body="""Can you please verify I'm pulling the valid users? 
                         The attached file has everyone that the script would automatically set to the MFA group. 
                         Thank you 
                         --Martin""",
                         files=file_name)

        # employees_without_mfa['result'] = employees_without_mfa['email'].apply(user.add_user_to_group)



        # # Package in to a tde file
        # data_file = TDEAssembler(data_frame=employees, extract_name='Workday_Employee_data')
        # # Set values for publishing the data.
        # file_name = str(data_file)
        # server_url, username, password, site_id, data_source_name, project = \
        #     auth.tableau_publishing(datasource_type='BizApps', data_source_name='Workday_Employee_data')
        #
        # publish_data(server_url, username, password, site_id, file_name, data_source_name, project, replace_data=True)
        # outlook().send_email(to='BizAppsIntegrations@bazaarvoice.com',
        #                    subject='Workday_User_data compiling complete', body='Workday_User_data compiling complete')


    except KeyboardInterrupt:
        pass
    except:
        error_result = "Unexpected AttributeError: %s, %s"\
                       % (sys.exc_info()[0], sys.exc_info()[1])
        subject = 'Error with Tableau refresh script, %s' % basename(__file__)
        print error_result
        # outlook().send_email('helpdesk@bazaarvoice.com', cc='BizAppsIntegrations@bazaarvoice.com',
        #                      subject=subject, body=error_result)
        # give_notice = Notifier()
        # give_notice.set_red()
        # give_notice.wait(30)
        # give_notice.flow_the_light()


if __name__ == '__main__':
    start = time()
    main()
    end = time()
    print (end - start)/60
    print datetime.now()