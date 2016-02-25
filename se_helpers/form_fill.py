__author__ = 'Lothilius'


from selenium import webdriver, common
from selenium.webdriver.support.select import Select
from bv_authenticate.Authentication import Authentication as auth
import sys



baseurl = "https://cs2.salesforce.com/005?retURL=%2Fui%2Fsetup%2FSetup%3Fsetupid%3DUsers&setupid=ManageUsers"

browser = webdriver.Firefox()
username, pw = auth.sfdc_login()


# Login function
def login(browser):
    #Write Username in Username TextBox
    browser.find_element_by_name("username").send_keys(username)

    #Write PW in Password TextBox
    browser.find_element_by_name("pw").send_keys(pw)

    #Click Login button
    browser.find_element_by_css_selector("#Login").click()

# Open the Form to create a new user.
def open_new_record():
    browser.implicitly_wait(4)
    displayed = browser.find_element_by_name("new").is_displayed()
    if not displayed:
        for i in range(0, 3):
            displayed = browser.find_element_by_name("new").is_displayed()
            if displayed:
                #Click New button
                browser.find_element_by_name("new").click()
                break
            else:
                browser.implicitly_wait(3)
    else:
        browser.find_element_by_name("new").click()


# Do the actual Filling in of the form
def fill_out_form(first_name, last_name, email, user_name, type, profile, role=''):
    # Set first name
    browser.find_element_by_id('name_firstName').send_keys(first_name)
    # Clear and write Subject
    browser.find_element_by_id('name_lastName').clear()
    browser.find_element_by_id('name_lastName').send_keys(last_name)
    # Set Product
    browser.find_element_by_id('Email').send_keys(email)
    # Clear and fill Username
    browser.find_element_by_id('Username').clear()
    browser.find_element_by_id('Username').send_keys(user_name)

    if type == '100500000000D6z':
        # Select role
        Select(browser.find_element_by_id("role")).select_by_value(role)
        # Fill License and Profile
        Select(browser.find_element_by_id("user_license_id")).select_by_value(type)
        Select(browser.find_element_by_id('Profile')).select_by_visible_text(profile)
    elif type == '10050000000M69y':
        # Fill License and Profile
        Select(browser.find_element_by_id("user_license_id")).select_by_value(type)
        Select(browser.find_element_by_id('Profile')).select_by_value(profile)
    else:
        # Select role
        Select(browser.find_element_by_id("role")).select_by_value(role)
        print 'none'

    print first_name, last_name, type

    # Cick on Prioritize
    browser.find_element_by_id('new_password').click()

    # Save
    browser.find_element_by_name("save").click()
    browser.implicitly_wait(15)
    browser.get(baseurl)


def create_user(first_name, last_name, email, user_name, type, profile, role=''):
    browser.get(baseurl)
    try:
        browser.implicitly_wait(5)
        open_new_record()
    except:
        print "Unexpected error 1:", sys.exc_info()[0]
        #Wait for page to load.
        browser.implicitly_wait(10)
        browser.find_element_by_name("new").click()

    try:
        fill_out_form(first_name, last_name, email, user_name, type, profile, role='')
    except:
        print "Unexpected error 2:", sys.exc_info()[0]


    try:
        browser.implicitly_wait(15)
        displayed = browser.find_element_by_id('errorDiv_ep').is_displayed()
        print displayed
        if displayed:
            the_error = browser.find_element_by_class_name('errorMsg').text
            print 'Oh no there is an error! \n'
            print the_error
        else:
            print 'We are good!'
            webdriver.close()
    except common.exceptions.NoSuchElementException, e:
        print '3', e