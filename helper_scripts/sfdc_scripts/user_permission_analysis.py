__author__ = 'Lothilius'

from sfdc.SFDC_Users import SFDC_Users
from helper_scripts.misc_helpers.data_manipulation import create_feature_vector_dataframe
import pandas as pd
from okta.Okta_Application import Okta_Application


pd.set_option('display.width', 330)
pd.set_option('display.max_rows', 9)

def replacement_method(item_value):
    replace_with = {False: 0, True: 1, 'na': 0, 'False': 0, 'True': 1}
    try:
        if item_value in [False, True, 'na', 'False', 'True']:
            replacing_value = replace_with[item_value]
        else:
            replacing_value = 1

        return replacing_value

    except Exception, e:
        print e



replace_with = {False: 0, True: 1, 'na': 0, 'False': 0, 'True': 1}

no_touch_columns = ['Email', 'Employee_ID__c', 'UserId', 'UserName']
# Create the initial SFDC user list with permissions
sfdc_list = SFDC_Users(include_licenses=True, include_permissions=True)
sfdc_users = sfdc_list.users_with_licenses_permissions().copy()

# Vectorize the profiles
print '---------------new DF---------------\n'
print sfdc_users[['UserId', 'Profile_Name']]
profiles_vectorized = create_feature_vector_dataframe(sfdc_users[['UserId', 'Profile_Name']],
                                      feature_index_column='UserId', feature_column='Profile_Name')
profiles_vectorized.fillna(value=0, inplace=True)
profile_clean = pd.merge(left=sfdc_users, right=profiles_vectorized, on='UserId')

# Vectorize the roles
print '---------------new DF---------------\n'
print sfdc_users[['UserId', 'Role__c']]
profiles_vectorized = create_feature_vector_dataframe(sfdc_users[['UserId', 'Role__c']],
                                      feature_index_column='UserId', feature_column='Role__c')
profiles_vectorized.fillna(value=0, inplace=True)
almost_clean = pd.merge(left=profile_clean, right=profiles_vectorized, on='UserId')


print '---------------new DF---------------\n'
almost_clean.drop(['Profile_Name', 'Role__c', 'na'], axis=1, inplace=True)
print almost_clean


print '---------------new DF---------------\n'
# Save none binary columns
user_values = almost_clean[no_touch_columns]
print user_values


# Replace nulls and nots with 0's
almost_clean = almost_clean.applymap(replacement_method)

print '---------------new DF---------------\n'
cleaned_df = user_values.join(almost_clean, how='left', rsuffix='_ac')
print cleaned_df


print '---------------new DF---------------\n'
# Continue to clean up Data frame to onlye necessary data
duplicate_columns = [element + '_ac' for element in no_touch_columns]
cleaned_df.drop(duplicate_columns, axis=1, inplace=True)
print cleaned_df

print '---------------new DF---------------\n'
workday = Okta_Application(app_name='workday')
work_day = workday.app_users[['email', 'businessTitle', 'managerUserName']]

print '---------------new DF---------------\n'
full_clean = cleaned_df.merge(work_day, how='outer', left_on='Email', right_on='email')
print full_clean