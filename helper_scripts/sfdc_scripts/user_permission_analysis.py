__author__ = 'Lothilius'

from sfdc.SFDC_Users import SFDC_Users
from helper_scripts.misc_helpers.data_manipulation import create_feature_vector_dataframe
import pandas as pd
from okta.Okta_Application import Okta_Application
from helper_scripts.notify_helpers import alert_homer, alert_the_light
import scipy.stats as s


pd.set_option('display.width', 330)
pd.set_option('display.max_rows', 100)


class SFDC_User_Analysis(object):
    def __init__(self):
        self.full_user_vector = self.get_user_vector()

    def __str__(self):
        return str(self.full_user_vector)

    def replacement_method(self, item_value):
        replace_with = {False: 0, True: 1, 'na': 0, 'False': 0, 'True': 1}
        try:
            if item_value in [False, True, 'na', 'False', 'True']:
                replacing_value = replace_with[item_value]
            else:
                replacing_value = 1

            return replacing_value

        except Exception, e:
            print e


    def get_permissions(self, df):
        # Reduce columns to columns that are profile features to the user record
        binary_columns = self.boil_down_columns(df)
        # print '----binary_columns---'
        # print binary_columns
        calculation_dataframe = df[binary_columns]
        calculation_dataframe.to_csv('/Users/martin.valenzuela/Downloads/user_permissions_reduced_.csv', encoding='utf-8')

        # Sum the entries in the feature columns
        sum_df = calculation_dataframe.iloc[:, 1:].sum(axis=0)
        print len(df)

        zero_entropy_positives = self.gather_zero_entropy_positives(sum_df, len(df['email'])).index

        # Calculate probabilty when pertaining to the group
        probability_df = sum_df.map(lambda x: float(x) / len(calculation_dataframe.iloc[:, 0]))

        # Apply a threshold
        threshhold_columns = (sum_df > len(df) * .34)
        entropy_df = self.calculate_entropy(probability_df[threshhold_columns[threshhold_columns == True].index])

        self.reduced_mean_entropy = entropy_df[~(entropy_df == 0.0)].mean()
        print entropy_df[~(entropy_df == 0.0)]
        print self.reduced_mean_entropy

        low_entropy_permissions = entropy_df[(entropy_df <= self.reduced_mean_entropy) & (entropy_df > 0)]
        permissions_list = low_entropy_permissions.index.tolist()
        permissions_list.extend(zero_entropy_positives)

        return permissions_list


    def boil_down_columns(self, df):
        columns = df.columns.tolist()
        feature_columns = ['Email']
        for each in columns:
            if df[each].dtypes == 'int64':
                feature_columns.extend([each])

        return feature_columns


    def calculate_entropy(self, probability_df):
        """ Cancluate the entropy for the probability dataframe
        :param probability_df: A dataframe object made of probabilities
        :return: a entropy series for dataframe by column
        """
        entropy_df = probability_df.map(lambda x: s.entropy([x, 1 - x]))
        # print entropy_df[entropy_df > 0]

        return entropy_df


    def gather_zero_entropy_positives(self, sum_df, group_size):
        positive_columns = sum_df[sum_df == group_size]
        return positive_columns

    def get_peer_group_by_manager(self, manager_name='dave.griffiths@bazaarvoice.com'):
        # Get nearest group according to manager
        nearest_group = self.full_user_vector[self.full_user_vector['managerUserName'].str.lower() == manager_name.lower()]
        # nearest_group = full_clean[full_clean['businessTitle'].str.contains('Client Success Director')]

        return nearest_group

    def get_permissions_by_manager_peer_group(self, manager_name='dave.griffiths@bazaarvoice.com'):
        """
        :return:
        """
        nearest_group = self.get_peer_group_by_manager(manager_name)
        reduced_group = self.get_permissions(nearest_group)

        similar_columns = ['Email']
        similar_columns.extend(reduced_group)

        return nearest_group[similar_columns]

    def get_user_vector(self):
        replace_with = {False: 0, True: 1, 'na': 0, 'False': 0, 'True': 1}

        no_touch_columns = ['Email', 'Employee_ID__c', 'UserId', 'UserName']
        # Create the initial SFDC user list with permissions
        sfdc_list = SFDC_Users(include_licenses=True, include_permissions=True)
        sfdc_users = sfdc_list.users_with_licenses_permissions().copy()
        sfdc_users['Email'] = sfdc_users['Email'].map(lambda x: x.lower())

        # Vectorize the profiles
        # print '---------------new DF---------------\n'
        # print sfdc_users[['UserId', 'Profile_Name']]
        profiles_vectorized = create_feature_vector_dataframe(sfdc_users[['UserId', 'Profile_Name']],
                                              feature_index_column='UserId', feature_column='Profile_Name', suffix='_profile')
        profiles_vectorized.fillna(value=0, inplace=True)
        profile_clean = pd.merge(left=sfdc_users, right=profiles_vectorized, on='UserId')

        # Vectorize the roles
        # print '---------------new DF---------------\n'
        # print sfdc_users[['UserId', 'Role__c']]
        profiles_vectorized = create_feature_vector_dataframe(sfdc_users[['UserId', 'Role__c']],
                                              feature_index_column='UserId', feature_column='Role__c', suffix='_role')
        profiles_vectorized.fillna(value=0, inplace=True)
        almost_clean = pd.merge(left=profile_clean, right=profiles_vectorized, on='UserId')


        # print '---------------new DF---------------\n'
        almost_clean.drop(['Profile_Name', 'Role__c'], axis=1, inplace=True)
        # print almost_clean


        # print '---------------new DF---------------\n'
        # Save none binary columns
        user_values = almost_clean[no_touch_columns]
        # print user_values


        # Replace nulls and nots with 0's
        almost_clean = almost_clean.applymap(self.replacement_method)

        # print '---------------new DF---------------\n'
        cleaned_df = user_values.join(almost_clean, how='left', rsuffix='_ac')
        # print cleaned_df


        # print '---------------new DF---------------\n'
        # Continue to clean up Data frame to onlye necessary data
        duplicate_columns = [element + '_ac' for element in no_touch_columns]
        cleaned_df.drop(duplicate_columns, axis=1, inplace=True)
        # print cleaned_df

        # print '---------------new DF---------------\n'
        # Gather Workday data
        workday = Okta_Application(app_name='workday')
        work_day = workday.app_users[['email', 'businessTitle', 'managerUserName', 'accountType']].copy()
        work_day['email'] = work_day['email'].map(lambda x: x.lower())

        # print '---------------new DF---------------\n'
        #  Merge the workday title and manager data with the SFDC permissions
        full_clean = cleaned_df.merge(work_day, how='left', left_on='Email', right_on='email')
        # print full_clean['managerUserName']
        full_clean = full_clean[~pd.isnull(full_clean['businessTitle'])]

        alert_the_light()
        alert_homer()

        return full_clean


if __name__ == '__main__':
    use_list = SFDC_User_Analysis()
    # print use_list

    print use_list.get_permissions_by_manager_peer_group()