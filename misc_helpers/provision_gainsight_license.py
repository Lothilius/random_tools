__author__ = 'Lothilius'

from bv_authenticate.Authentication import Authentication as auth
from sfdc.SFDC_User import SfdcUser
from se_helpers.actions import *

def main():
    #TODO fix user interaction lines
    while True:
        environment = raw_input("Which environment would you like to use, (prod) or (st)aging? ")
        if environment == 'prod':
            username, pw = auth.sfdc_login('prod')
        elif environment == ('st' or 'staging'):
            username, pw = auth.sfdc_login()
        else:
            print "I'm Sorry I did not understand your selection. Please try again."

        mode = raw_input('Would you like (s)ingle, (a)ssisted, or (f)ull automatic provisioning mode? ')
        if mode == ('s' or 'single'):
            new_user_name = raw_input('Please enter name: ')
            new_user_title = raw_input('Please enter title: ')
            new_user_manager = raw_input('Please enter manager: ')
            user = SfdcUser()
            user.add_name(new_user_name)
            user.add_title(new_user_title)
            user.add_manager(new_user_manager)
            print user.email()
            start_form_fill(environment, user.first_name, user.last_name, user.email(), user.name(), user.title,
                            user.manager)

        elif mode == ('a' or 'assisted'):
            file_name = raw_input('Please enter file name: ')
            while file_name != 'exit':
                try:
                    full_file_path = '/Users/martin.valenzuela/Desktop/SFDC_exports/New_hires_' + file_name + '.csv'  # New_hires
                    csv_info = array_from_file(full_file_path)
                    break
                except IOError:
                    print """\nNo file found with that name. \nPlease Try again. \n"""
                    file_name = raw_input('Please enter file name: ')

            for each in csv_info[1:]:
                print each[2]
                # Create User object for each user row in csv
                user = SfdcUser()
                user.add_name(each[2])
                user.add_title(each[3])
                user.add_manager(each[4])
                print user.email()
                start_form_fill(environment, user.first_name, user.last_name, user.email(), user.name(), user.title,
                                user.manager)

        elif mode == ('f' or 'full'):
            file_name = raw_input('Please enter file name: ')
            full_file_path = '/Users/martin.valenzuela/Desktop/SFDC_exports/New_hires_' + file_name + '.csv'  # New_hires
            csv_info = array_from_file(full_file_path)
            # print csv_info[1, 2]

            user = SfdcUser()
            user.add_name(csv_info[1, 2])
            print csv_info[1, 2]

        else:
            print "I'm Sorry I did not understand your selection. Please try again."