__author__ = 'Lothilius'

from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.keys import Keys
from bv_authenticate.Authentication import Authentication as auth
import sys
import time


def wait(seconds=5):
    time.sleep(seconds)

def start_form_fill(environment, first_name, last_name, email, user_name, title, manager):
    baseurl = ''
    username = ''
    pw = ''
    if environment == 'prod':
        username, pw, token = auth.sfdc_login('prod')
        baseurl = "https://na3.salesforce.com/005?retURL=%2Fui%2Fsetup%2FSetup%3Fsetupid%3DUsers&setupid=ManageUsers"
    elif environment == ('st' or 'staging'):
        username, pw, token = auth.sfdc_login()
        baseurl = "https://cs13.salesforce.com/005?retURL=%2Fui%2Fsetup%2FSetup%3Fsetupid%3DUsers&setupid=ManageUsers"

    browser = webdriver.Chrome('/Users/martin.valenzuela/Dropbox/Coding/BV/chromedriver')
    browser.get(baseurl)
    browser.implicitly_wait(4)
    login(browser, username, pw)
    create_user(browser, first_name, last_name, email, user_name, title, manager)


def open_new_tab(browser, web_url):
    body = browser.find_element_by_tag_name("body")
    body.send_keys(Keys.CONTROL + 't')
    body.send_keys(web_url)

def okta_load(first_name, last_name):
    username, pw = okta_login()
    baseurl = "https://bazaarvoice-admin.okta.com/admin/users"\

    browser = webdriver.Chrome('/Users/martin.valenzuela/Dropbox/Coding/BV/chromedriver')
    browser.get(baseurl)
    browser.implicitly_wait(4)

    login_okta(browser, username, pw)
    wait(5)

    okta_fill_out_form(browser, first_name, last_name)

# Do the actual Filling in of the form
def okta_fill_out_form(browser, first_name, last_name):
    browser.implicitly_wait(3)
    try:
        name = first_name, " ", last_name
        # Look up name
        browser.find_element_by_css_selector('input.text-field-default').send_keys(name)
        wait(10)
        # Select link when looked up partial matching the name
        browser.find_element_by_partial_link_text(str(first_name)).click()
        wait(2)
        # Click on Unassigned Applications
        browser.find_element_by_css_selector('span.button-label').click()
        wait(3)
        # Lookup the Staging App
        browser.find_element_by_css_selector('input.text-field-default').send_keys('Salesforce (Staging)')
        wait(3)
        # Click to add the Staging App
        browser.find_element_by_css_selector('a.link-button.link-button-icon.app-user-add-link').click()
        wait(15)

        # Click to save
        browser.find_element_by_xpath("//form[@name='APPUSER']/div[2]/input[1]").click()
    except:
        print "Unexpected error 2:", sys.exc_info()[0]

        pass


def login_okta(browser, username, pw):
    #Write Username in Username TextBox
    browser.find_element_by_name("username").send_keys(username)

    #Write PW in Password TextBox
    browser.find_element_by_id("pass-signin").send_keys(pw)

    #Click Login button
    browser.find_element_by_id("signin-button").click()

# Login function
def login(browser, username, pw):
    #Write Username in Username TextBox
    browser.find_element_by_name("username").send_keys(username)

    #Write PW in Password TextBox
    browser.find_element_by_name("pw").send_keys(pw)

    #Click Login button
    browser.find_element_by_css_selector("#Login").click()

# Open the Form to create a new user.
def open_new_record(browser):
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
def fill_out_form(browser, first_name, last_name, email, user_name, title, manager):
    # Set First name
    browser.find_element_by_id('name_firstName').send_keys(first_name)
    browser.implicitly_wait(1)
    # Clear and write Last name
    browser.find_element_by_id('name_lastName').clear()
    browser.find_element_by_id('name_lastName').send_keys(last_name)
    # Set Email
    browser.find_element_by_id('Email').clear()
    browser.find_element_by_id('Email').send_keys(email)

    # Clear and fill Username
    browser.find_element_by_id('Username').clear()
    browser.find_element_by_id('Username').send_keys(email)
    browser.implicitly_wait(1)

    # Clear and fill Title
    browser.find_element_by_id('Title').clear()
    browser.find_element_by_id('Title').send_keys(title)
    # Clear and fill Manager
    browser.find_element_by_id('Manager').clear()
    browser.find_element_by_id('Manager').send_keys(manager)

    # Click on Remove from notification
    browser.find_element_by_id('new_password').click()

    browser.find_element_by_id('UserPermissions_9').click()
    # Select user license
    Select(browser.find_element_by_id("user_license_id")).select_by_value('100500000000D6z')

    admin_action = ''
    while admin_action != 'Yes':
        admin_action = raw_input('Are we ready to move on? ')
        if admin_action == 'Yes':
            break
    # Save
    # browser.find_element_by_name("save").click()
    # browser.implicitly_wait(20)


def create_user(browser, first_name, last_name, email, user_name, title, manager):
    try:
        browser.implicitly_wait(7)
        open_new_record()
    except:
        print "Unexpected error 1:", sys.exc_info()[0]
        #Wait for page to load.
        browser.implicitly_wait(10)
        browser.find_element_by_name("new").click()

    try:
        fill_out_form(browser, first_name, last_name, email, user_name, title, manager)
    except:
        print "Unexpected error 2:", sys.exc_info()[0]

    try:
        browser.implicitly_wait(20)
        displayed = browser.find_element_by_id('errorDiv_ep').is_displayed()
        if displayed:
            the_error = browser.find_element_by_class_name('errorMsg').text
            print 'Oh no there is an error! \n'
            print the_error
        else:
            print 'We are good!'
        admin_action = ''
        while admin_action != 'Yes':
            admin_action = raw_input('Are we ready to move on? ')
        # browser.close()
    except:
        admin_action = ''
        print '3', sys.exc_info()[0]
        while admin_action != 'Yes':
            admin_action = raw_input('Are we ready to move on? ')
        # browser.close()
