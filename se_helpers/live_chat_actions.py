# coding: utf-8
__author__ = 'Lothilius'

from bv_authenticate.Authentication import Authentication as auth
from bs4 import BeautifulSoup
from actions import wait
from actions import get_se_browser
from actions import switch_to_pop_up
from os import environ
from datetime import datetime
from send_email.OutlookConnection import OutlookConnection as oc
import sys


domain = {'prod': 'https://bazaarvoice.secure.', 'staging': 'https://staging-bazaarvoice.cs59.'}

live_chat_welcome_message = 'Hello this is the hourly test. Please repeat the script. Ready?'

live_chat_script = \
    ['1-asdf qwer% zxcvui op.'
    , '2-rewq fdsa$ vcxzpo iu. lkjh mnbv.'
    , '3-fdsa rewq# poiuvc xz. fghj rtyu cvbn 4321.'
    , '4-uiop ghjk@ vbnmvc xz fdsa. rewq tyui ghjk mnbv dfgh. 1357'
    , '5-qazx wsxc! edcvrf vb tgbnyhnm. ujki iklo poiu ytre ewqa. zxcv bnmk jhgf. 555-123-1234']

def go_to_spark_live_chat(environment='staging'):
    """ Use as a quick way to jump to the Live chat portal in spark.
    :return: This function provides selenium initiated browsers.
    """
    browser = get_se_browser('phantom')
    try:
        username, pw = auth.spark_credentials()
        global domain
        domain = domain[environment]
        baseurl = domain + "force.com/cp/cplogin"
        browser.get(baseurl)
        browser.implicitly_wait(5)
        login_spark(browser, username, pw)
        browser.implicitly_wait(5)
        case_url = domain + 'force.com/cp/sprkCases?cat=Business+or+Technical+Question&page=LeftNavOncphome'
        browser.get(case_url)
        browser.implicitly_wait(5)
        browser.find_element_by_xpath("//span[@class='liveAgent gold']").click()
        browser.implicitly_wait(5)

        # Determine main window reference
        main_window_handle = None
        while not main_window_handle:
            main_window_handle = browser.current_window_handle
        # Switch to Live chat window pop up
        switch_to_pop_up(browser, main_window_handle)
        browser.implicitly_wait(5)
        check_for_agent_reply(browser)

        return browser
    except Exception:
        # try:
        error_message = "Unexpected error login:%s, %s" \
                        % (sys.exc_info()[0], sys.exc_info()[1])
        print error_message
        notify_help_desk(browser, error_message)
        # except:
        #     error_message = "Catastrophic error: Unexpected error login:%s, %s" \
        #                     % (sys.exc_info()[0], sys.exc_info()[1])
        #     oc.send_email('martin.valenzuela@bazaarvoice.com', cc='', body=error_message)
        #     browser.close()
        return error_message


def login_spark(browser, username, pw):
    """ Use selenium to apply a user name and password to login to spark.
    :param browser: Active Selenium webdriver at the login page for the spark portal
    :param username: Spark user name
    :param pw: Spark username password
    :return: Active Selenium webdriver after loging in
    """
    #Write Username in Username TextBox
    browser.find_element_by_xpath("//input[@id='j_id0:j_id1:loginForm:username']").send_keys(username)

    #Write PW in Password TextBox
    browser.find_element_by_xpath("//input[@id='j_id0:j_id1:loginForm:password']").send_keys(pw)

    #Click Login button
    browser.find_element_by_xpath("//input[@id='j_id0:j_id1:loginForm:loginButton']").click()

    return browser


def check_for_agent_reply(browser):
    """ This is the listener that is looped for 400 seconds that is looped around sending the test script and looped
        and around weather a user has responded.
    :param browser: Active Selenium webdriver
    :return: Text
    """
    i = 200
    number_or_errors = 0
    try:
        reply_to_agent(browser, message=live_chat_welcome_message)
        wait(2)
        # Loop through test scripts
        for j, test_line in enumerate(live_chat_script):
            # print test_line
            operator_message_list = explore_page(browser.page_source)
            number_of_agent_posts = len(operator_message_list)

            # Loop is main listener
            while i > 0:
                wait(2)
                operator_message_list = explore_page(browser.page_source)
                try:
                    # print number_of_agent_posts
                    # print len(operator_message_list)
                    # Check if error limit has been reached.
                    if number_or_errors == 3:
                        reply = "Too many errors on response match. Creating helpdesk ticket."
                        reply_to_agent(browser, message=reply)
                        raise Exception
                    # Send initial post
                    elif len(operator_message_list) == 2:
                        reply_to_agent(browser, message=test_line)
                        number_of_agent_posts = len(operator_message_list)
                    # Check if there has been a new post by the agent.
                    elif number_of_agent_posts != len(operator_message_list):
                        # Check if Agent reply is the same as the test script line
                        if operator_message_list[-1] == test_line:
                            reply_to_agent(browser, message="Match recieved. Please wait...")
                            try:
                                reply_to_agent(browser, message=live_chat_script[j+1])
                            except IndexError:
                                pass
                            number_of_agent_posts = len(operator_message_list)
                            number_or_errors = 0
                            break
                        # This piece is if the agent posted reponse is not the same as the test script
                        elif operator_message_list[-1] != test_line:
                            # print test_line
                            # print operator_message_list[-1]
                            reply = "Response does not match. Please try again."
                            reply_to_agent(browser, message=reply)
                            # reply_to_agent(browser, message=test_line)
                            number_of_agent_posts = len(operator_message_list)
                            number_or_errors += 1
                    else:
                        pass
                        # print "waiting..."


                except Exception, e:
                    notify_help_desk(browser, "")
                    browser.close()
                    raise Exception
                i -= 1
        if i < 1:
            raise Exception

        # End the test.
        reply_to_agent(browser, message="Thank you. The test has concluded")
        browser.find_element_by_xpath("//button[@title='End Chat']").click()
        browser.close()

    except Exception, e:
        print e
        notify_help_desk(browser, "Test timed out!!")
        browser.close()

    print "Test Concluded"
    return "Test Concluded"


def explore_page(live_chat_page):
    """  Parse the live_chat_window and return only messages in the window.
            :return: minimal text requested associated with messages.
            """
    soup = BeautifulSoup(live_chat_page, 'html.parser')

    # Find the left portion of the status table and get the rows of the table separated.
    messages = soup.find(name='div', id='liveAgentChatLogText')
    operator_message_list = messages.find_all(name='span', class_='operator')
    # Join results in to a list.
    message_table = []
    for each in operator_message_list:
        try:
            operator_message = each.find(name='span', class_='messageText')
            message_table.append(operator_message.string)
        except:
            pass
    return message_table


def reply_to_agent(browser, message='This is a message'):
    """ Send a message via the live chat agent session
    :param browser: Selenium webdriver session that is active in the live chat window
    :param message: The message to the agent
    :return: Nothing
    """
    try:
        browser.find_element_by_xpath("//textarea[@class='liveAgentChatTextArea']").send_keys(message)
        wait(2)
        browser.find_element_by_xpath("//button[@class='liveAgentChatElement liveAgentSendButton']").click()
        wait(2)
    except:
        reply_to_agent(browser, message)


def notify_help_desk(browser, message):
    """ Notify helpdesk with a screenshot of the active selenium webdriver seession.
    :param browser: Selenium Webdriver session that is active
    :param message:
    :return:
    """
    path = environ['MY_TEMP_FOLDER']
    full_path = path + "error_screen_shot_" + datetime.now().strftime(format='%Y_%m_%d-%H_%M') + '.png'
    print "Screen shot saved: %s" % full_path
    browser.get_screenshot_as_file(full_path)
    file_name = [full_path]
    browser.close()
    oc.create_helpdesk_ticket(subject='An error with Live Chat has occured [BizApps]',
                              cc=['holly.socha@bazaarvoice.com', 'sadie.claire@bazaarvoice.com'],
                              body=message, files=file_name)

if __name__ == '__main__':
    go_to_spark_live_chat(environ['ENVIRONMENT'])