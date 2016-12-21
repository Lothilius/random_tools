# coding: utf-8
__author__ = 'Lothilius'

from sfdc.SFDC_Connection import SFDC_Connection
import pandas as pd
import json
import sys

pd.set_option('display.width', 200)

def refresh_object(object='Lead'):
    sfdc_connect = SFDC_Connection.connect_to_SFDC(environment='staging')
    query = SFDC_Connection.build_query(sf_object=object, type='', status='',
                                        columns='Id, LastName, FirstName, Email, Full_Name__c')
    result = sfdc_connect.query_all(query)
    # print type(result['records'])
    # results = json.load(result)
    # print results
    # print pd.read_json(str(result['records']))
    result_list = []
    for each in result['records']:
        result_list.append([each['Id'], each['LastName'],  each['FirstName'], each['Email'], each['Full_Name__c'], ''])
    results_panda = pd.DataFrame(result_list, columns=['Id', 'LastName', 'FirstName', 'Email', 'Full_Name__c', 'New_email'])

    return results_panda

def append_staging(value):
    value = str(value).split(sep='.staging')
    staging_value = ''.join(value) + '.staging'

    return staging_value


def alter_email(data_frame_row):

    first_name = data_frame_row[2].encode('utf-8')
    last_name = data_frame_row[1].encode('utf-8')
    original_email = data_frame_row[3].encode('utf-8')
    if '@' in original_email:
        clean_email = append_staging(original_email)
    else:
        clean_email = first_name + '.' + last_name + '@example.com'
        clean_email = append_staging(clean_email)
    if '@' in last_name:
        data_frame_row[1] = append_staging(last_name)

    data_frame_row[5] = clean_email

    return data_frame_row

def main():
    objects = ['Lead', 'Contact']
    for each in objects:
        contact_data = refresh_object(each)
        contact_data.fillna(value='', inplace=True)
        contact_data = contact_data.apply(alter_email, axis=1)

        contact_data.to_csv('/Users/martin.valenzuela/Desktop/SFDC_exports/%s_Refreshed_11_14_16_0_b.csv' % each,
                            index=False, encoding='utf-8')
        print contact_data

if __name__ == '__main__':
    main()