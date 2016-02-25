__author__ = 'Lothilius'

import re
import numpy as np
import Permissions


class SfdcUser:
    """ This module creates a SFDC user from the first and last name and Profile.
    """

    def __int__(self, first_name, last_name, email, title, manager, profile, permissions):
        """Create an empty User Object"""
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.title = title
        self.manager = manager
        self.profile = profile
        self.permissions = permissions

    def __str__(self):
        return '[%s, %s, %s, %s, %s, %s, %s]' % (self.first_name, self.last_name,
                                                 self.email, self.title, self.manager, self.profile, self.permissions)

    def first_name(self):
        return self.first_name

    def last_name(self):
        return self.last_name

    def name(self):
        return '%s %s' % (self.first_name, self.last_name)

    def email(self):
        return '%s.%s@bazaarvoice.com' % (self.first_name, self.last_name)

    def title(self):
        return self.title

    def manager(self):
        return self.manager

    def profile(self):
        return self.profile

    def permissions(self):
        return self.permissions

    # Split First and Last Name
    def add_name(self, the_name):
        if the_name != '':
            the_name = self.clean_name(the_name)
            the_name = the_name.split(' ')
            self.first_name = the_name[0]
            self.last_name = the_name[1]

    # Add title to the user object
    def add_title(self, title):
        self.title = title

    # Add manager to the user object
    def add_manager(self, manager):
        self.manager = manager

    def add_profile_id(self, user_info):
        for i in session.query(Profiles.id).order_by(desc(Profiles.id)).limit(100):
                    user_info.append(i)

    def add_permissions(self):
        self.permissions = Permissions(self.title)

    # Clean up the Data so that consultants are caught
    def clean_name(self, the_name):
        # Remove [C]
        regex = re.compile(' \[C\]')
        the_name = regex.sub('', the_name)

        return the_name

    # Create clean array
    def create_clean(csv_info):

        user_list = np.array([['first', 'last']])
        name_list = csv_info[1:, 2]

        for each in name_list:
            name = clean_name(each)
            if name == '':
                pass
            else:
                first, last = split_name(name)
                user_list = np.append(user_list, [[first, last]], 0)

        # Get rid of the column labels first and last
        user_list = user_list[1:]
        emails = np.array([])

        # Create email column
        for each in user_list:
            email = create_user_email(each)
            emails = np.append(emails, [email], 0)

        # Join name array with email column
        user_list = np.c_[user_list, emails]

        # TODO link up with the title mapping
        # Add the first name last name and title in to one array
        user_list = np.c_[user_list, csv_info[1:-1, 3]]

        return user_list


class UserList():
    pass