__author__ = 'Lothilius'

from se_helpers.actions import wait
from os import environ
from se_helpers.live_chat_actions import Live_Chat_Test


try:
    files = []
    errors = ''
    for attempt in range(10):
        test_livechat = Live_Chat_Test()
        results = test_livechat.run_test(environ['ENVIRONMENT'])
        if 'error' in results:
            print results
            if attempt < 9:
                files.append(test_livechat.screen_shot)
                errors = errors + '\n' + results
                test_livechat.browser.quit()
            pass
        else:
            break
        wait(10)
    if 'error' in results:
        test_livechat.notify_help_desk(errors, files=files)
    elif 'timed out' in results:
        test_livechat.notify_help_desk(errors, files=files)
    test_livechat.browser.quit()
except Exception, e:
    test_livechat.browser.quit()
    print "error: %s" % e
