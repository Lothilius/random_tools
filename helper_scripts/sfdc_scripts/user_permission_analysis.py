__author__ = 'Lothilius'

from sfdc.SFDC_Users import SFDC_Users
from helper_scripts.misc_helpers.data_manipulation import create_feature_vector_dataframe
import pandas as pd


pd.set_option('display.width', 330)
pd.set_option('display.max_rows', 9)

def replacement_method(item_value):
    replace_with = {False: 0, True: 1, 'na': 0, 'False': 0, 'True': 1}
    try:
        if item_value in [False, True, 'na', 'False', 'True']:
            replacing_value = replace_with[item_value]
        else:
            replacing_value = item_value

        return replacing_value

    except Exception, e:
        print e



replace_with = {False: 0, True: 1, 'na': 0, 'False': 0, 'True': 1}

no_touch_columns = ['Email', 'Employee_ID__c', 'UserId', 'Profile_Name', 'Role__c', 'UserName']
# Create the initial SFDC user list with permissions
sfdc_list = SFDC_Users(include_licenses=True, include_permissions=True)
sfdc_users = sfdc_list.users_with_licenses_permissions().copy()

print '---------------new DF---------------\n'
print sfdc_users[['UserId', 'Profile_Name']]
profiles_vectorized = create_feature_vector_dataframe(sfdc_users[['UserId', 'Profile_Name']],
                                      feature_index_column='UserId', feature_column='Profile_Name')
profiles_vectorized.fillna(value=0, inplace=True)
almost_clean = pd.merge(left=sfdc_users, right=profiles_vectorized, on='UserId')


print '---------------new DF---------------\n'
print almost_clean

sfdc_users = sfdc_users.applymap(replacement_method)

print sfdc_users
# print cleaned_users['UserPermissionsKnowledgeUser'].iloc[0]