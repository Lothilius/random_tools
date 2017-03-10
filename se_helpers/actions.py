__author__ = 'Lothilius'

from selenium import webdriver
from selenium.webdriver import *
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.keys import Keys
from bv_authenticate.Authentication import Authentication as auth
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import *
import sys
import time
from os import environ


def wait(seconds=5):
    time.sleep(seconds)

def hover(browser, element):
    hover_over = ActionChains(browser).move_to_element(element)
    hover_over.perform()


def get_se_browser(browser_type='chrome'):
    """ Create a Selenium webdriver object.
    :return: Selenium webdriver object
    """
    if "phantom" in browser_type:
        browser = webdriver.PhantomJS(executable_path=environ['PHANTOM_JS'])
    else:
        browser = webdriver.Chrome(executable_path=environ['CHROME_PATH'])

    return browser


def concur_go_to_employee(browser, employee_id='', employee_name=''):
    """ Go to the Employee record in Concur.
    :param browser:
    :param employee_id:
    :param employee_name:
    :return:
    """
    try:
        browser.find_element_by_id('searchString').clear()
        browser.find_element_by_id('searchString').send_keys(employee_id)
        browser.find_element_by_id('SearchWhat').send_keys("emp")
        browser.find_element_by_id('searchString').send_keys(Keys.ENTER)
        wait(2)
        browser.find_element_by_partial_link_text(employee_name).click()
        wait(2)
    except:
        print employee_name, " Unexpected error going to employee record:", sys.exc_info()[0]

def concur_employee_deprecation(browser, employee_id='', employee_name='', termination_date=''):
    """ This function will perform the steps of searching for a user navigating to their user record.
    :param browser: The selenium Webdriver object.
    :return: nothing
    """
    try:
        # Go to the employee record.
        concur_go_to_employee(browser, employee_id, employee_name)

        browser.find_element_by_id('AccountTerminationDate').send_keys(termination_date)
        browser.find_element_by_id('AccountTerminationDate').send_keys(Keys.ENTER)
        wait(3)
        browser.find_element_by_name('btnSave1').click()
        wait(7)

        print employee_name, "complete"
    except UnexpectedAlertPresentException:
        alert = browser.switch_to_alert()
        alert.accept()
        wait(3)
        browser.get('https://www.concursolutions.com/companyadmin/view_users.asp')
        wait(4)
        concur_employee_deprecation(browser, employee_id, employee_name, termination_date)
    except:
         print employee_name, " Unexpected error 2:", sys.exc_info()[0]


def switch_to_pop_up(browser, main_window_handle):
    pop_up_window_handle = None
    while not pop_up_window_handle:
        for handle in browser.window_handles:
            if handle != main_window_handle:
                pop_up_window_handle = handle
                break
        browser.switch_to.window(pop_up_window_handle)


def concur_change_expense_approver(browser, employee_id='', employee_name='', approver=''):
    """ This function will perform the steps of searching for a user navigating to their user record.
    :param browser: The selenium Webdriver object.
    :return: nothing
    """
    try:
        main_window_handle = None
        while not main_window_handle:
            main_window_handle = browser.current_window_handle
        # Go to the employee record.
        concur_go_to_employee(browser, employee_id, employee_name)

        browser.find_element_by_xpath("//a[@href='javascript:openApprovers();']").click()
        wait(3)
        switch_to_pop_up(browser, main_window_handle)
        wait(3)
        browser.find_element_by_id('newexpenseapproverName').clear()
        wait(1)
        browser.find_element_by_id('newexpenseapproverName').send_keys(approver)
        wait(2)
        browser.find_element_by_id('saveApproversChangesBtn').click()
        wait(2)
        browser.close()
        browser.switch_to.window(main_window_handle)
        wait(3)
        browser.find_element_by_name('btnSave1').click()

        print employee_name, "complete"
    except UnexpectedAlertPresentException:
        alert = browser.switch_to_alert()
        alert.accept()
        wait(3)
        browser.get('https://www.concursolutions.com/companyadmin/view_users.asp')
        wait(4)
        concur_change_expense_approver(browser, employee_id, employee_name)
    except:
         print employee_name, " Unexpected error in concur_change_expense_approver:", sys.exc_info()[0]

def go_to_concur_user_page():
    """ Use as a quick way to jump to the User Administration in Concur.
    :return: This function provides selenium initiated browsers.
    """
    try:
        baseurl = ''
        username = ''
        pw = ''
        username, pw = auth.bv_credentials()
        baseurl = "https://www.concursolutions.com/companyadmin/view_users.asp"

        baseurl = baseurl
        browser = get_se_browser()
        browser.get('https://bazaarvoice.okta.com/')
        wait(2)
        login_okta(browser, username, pw)
        wait(20)
        browser.get('https://bazaarvoice.okta.com/home/concur/0oaeqjcwmIDXNCEXMUBI/615?fromHome=true')
        wait(1)
        browser.get(baseurl)
        wait(3)

        return browser
    except:
         print "Unexpected error login:", sys.exc_info()[0]

def go_to_sfdc_page(environment='', url_ending=''):
    """ Use as a quick way to deploy multiple windows in an environment.
    :param environment: Label as 'prod' and '' will route to staging.
    :param url_ending: The record id is the id that would normally go at the end of the url to get to the webpage.
    :return: Returns nothing. This function provides selenium initiated browsers.
    """
    baseurl = ''
    username = ''
    pw = ''
    if environment == 'prod':
        username, pw, token, sandbox = auth.sfdc_login('prod')
        baseurl = "https://na3.salesforce.com/"
    elif environment == ('st' or 'staging'):
        username, pw, token, sandbox = auth.sfdc_login()
        baseurl = "https://cs13.salesforce.com/"

    baseurl = baseurl + url_ending
    browser = get_se_browser()
    browser.get(baseurl)
    wait(3)
    login(browser, username, pw)

    return browser

def add_permission_sfdc(browser='', user_id=''):
    """
    :param browser:
    :param user_id:
    :return:
    """
    edit_profile_url_end = '?noredirect=1&isUserEntityOverride=1'
    username = ''
    pw = ''
    try:
        base_url = browser.current_url
        url = base_url + user_id + edit_profile_url_end
        browser.get(url)
    except:
        browser = get_se_browser()
        username, pw, token, sandbox = auth.sfdc_login('')
        base_url = 'https://na3.salesforce.com/'
        url = base_url + user_id + edit_profile_url_end

    element = browser.find_element_by_xpath("//span[contains(.,'Permission Set Assignments[1]')]")
    hover(browser, element)
    browser.find_element_by_xpath("//input[@name='editPermSetAssignments']").click()


def start_form_fill(environment, first_name, last_name, email, user_name, title, manager):
    baseurl = ''
    username = ''
    pw = ''
    if environment == 'prod':
        username, pw, token, sandbox = auth.sfdc_login('prod')
        baseurl = "https://na3.salesforce.com/005?retURL=%2Fui%2Fsetup%2FSetup%3Fsetupid%3DUsers&setupid=ManageUsers"
    elif environment == ('st' or 'staging'):
        username, pw, token, sandbox = auth.sfdc_login()
        baseurl = "https://cs13.salesforce.com/005?retURL=%2Fui%2Fsetup%2FSetup%3Fsetupid%3DUsers&setupid=ManageUsers"

    browser = get_se_browser()
    browser.get(baseurl)
    browser.implicitly_wait(4)
    login(browser, username, pw)
    create_user(browser, first_name, last_name, email, user_name, title, manager)


def open_new_tab(browser, web_url):
    body = browser.find_element_by_tag_name("body")
    body.send_keys(Keys.CONTROL + 't')
    body.send_keys(web_url)

def okta_load(first_name, last_name):
    username, pw = auth.bv_credentials()
    baseurl = "https://bazaarvoice-admin.okta.com/admin/users"

    browser = get_se_browser()
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
    browser.find_element_by_name("password").send_keys(pw)

    #Click Login button
    browser.find_element_by_xpath("//input[@class='button button-primary']").click()

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



if __name__ == '__main__':
    browser = go_to_concur_user_page()
    concur_change_expense_approver(browser=browser)
