__author__ = 'Lothilius'
import pandas as pd
import lxml.objectify as objectify
from StringIO import StringIO

pd.set_option('display.width', 285)

def pandafy_workday_file():
    file = open(
        "/Users/martin.valenzuela/Downloads/BAZ_Concur_20170410_1239.xml")
    xml = objectify.parse(StringIO(file.read()))

    root = xml.getroot()

    df = pd.DataFrame(columns=['id', 'name',  'first_name', 'last_name', 'email', 'status', 'active', 'active_status_date', 'position_title', 'management_level',
                               'business_site', 'business_site_name', 'business_site_country', 'supervisor_id',
                               'supervisor_name', 'base_pay_currency', 'cost_center'])

    for i, each in enumerate(root.getchildren()[1:]):
        id = each.getchildren()[0].getchildren()[0].text
        name = each.getchildren()[0].getchildren()[1].text
        first_name = each.getchildren()[2].getchildren()[0].getchildren()[1].text
        if 'Last_Name' in each.getchildren()[2].getchildren()[0].getchildren()[2].tag:
            last_name = each.getchildren()[2].getchildren()[0].getchildren()[2].text
        else:
            last_name = each.getchildren()[2].getchildren()[0].getchildren()[3].text
        for item in each.getchildren()[2].getchildren():
            if 'Email_Data' in item.tag:
                for i, email_tag in enumerate(item.getchildren()):
                    if 'WORK' in email_tag.text:
                        try:
                            email = item.getchildren()[1].text
                            break
                        except:
                            email = "Error1"

        status = each.getchildren()[3].getchildren()[0].text
        active = each.getchildren()[3].getchildren()[1].text
        active_status_date = each[3].getchildren()[2].text
        try:
            position_title = each.getchildren()[4].getchildren()[0].text
            management_level = each.getchildren()[4].getchildren()[5].text
            business_site = each.getchildren()[4].getchildren()[6].text
            business_site_name = each.getchildren()[4].getchildren()[7].text
            business_site_country = each.getchildren()[4].getchildren()[-3].text
            supervisor_id = each.getchildren()[4].getchildren()[-2].text
            supervisor_name = each.getchildren()[4].getchildren()[-1].text
            # print each.getchildren()[-1].getchildren()[0].text
            base_pay_currency = each.getchildren()[-1].getchildren()[0].text
            cost_center = each.getchildren()[4].getchildren()[3].getchildren()[0].text


            row_data = dict(zip(
                ['id', 'name', 'first_name', 'last_name', 'email', 'status', 'active', 'active_status_date', 'position_title', 'management_level',
                 'business_site', 'business_site_name', 'business_site_country', 'supervisor_id', 'supervisor_name', 'base_pay_currency', 'cost_center'],
                [id, name,  first_name, last_name, email, status, active, active_status_date, position_title, management_level, business_site,
                 business_site_name, business_site_country, supervisor_id, supervisor_name, base_pay_currency,cost_center]))
            row_data = pd.Series(row_data)
            df = df.append(row_data, ignore_index=True)

        except IndexError:
            position_title = each.getchildren()[4].getchildren()[0].text
            management_level = each.getchildren()[4].getchildren()[5].text
            business_site = each.getchildren()[4].getchildren()[6].text
            business_site_name = each.getchildren()[4].getchildren()[7].text
            business_site_country = each.getchildren()[4].getchildren()[-3].text
            supervisor_id = each.getchildren()[4].getchildren()[-2].text
            supervisor_name = each.getchildren()[4].getchildren()[-1].text
            base_pay_currency = each.getchildren()[-1].getchildren()
            cost_center = ''

            row_data = dict(zip(
                ['id', 'name',  'first_name', 'last_name', 'email', 'status', 'active', 'active_status_date', 'position_title', 'management_level',
                 'business_site', 'business_site_name', 'business_site_country', 'supervisor_id', 'supervisor_name', 'base_pay_currency', 'cost_center'],
                [id, name,  first_name, last_name, email, status, active, active_status_date, position_title, management_level, business_site,
                 business_site_name, business_site_country, supervisor_id, supervisor_name, base_pay_currency, cost_center]))
            row_data = pd.Series(row_data)
            df = df.append(row_data, ignore_index=True)

    df['concur_name'] = df['last_name'].str.cat(df['first_name'], sep=", ")
    return df

if __name__ == '__main__':
    data = pandafy_workday_file()
    data.fillna(value='NA', inplace=True)
    regular_data = data[~data['business_site'].str.contains('Contractor')
                  & ~data['business_site_name'].str.contains('Contractor')
                  & ~data['business_site_name'].str.contains('Moderation/Authenticity')
                  & ~data['position_title'].str.contains('Contractor')
                  & ~data['management_level'].str.contains('Coordinator')
                  & ~data['cost_center'].str.contains('\W', na=True)].copy(deep=True)
    print regular_data[regular_data['first_name'].str.contains(r'[\W]')]