__author__ = 'Lothilius'

from se_helpers.actions import get_se_browser


browser = get_se_browser()


url = "https://bazaarvoice--staging.cs59.my.salesforce.com/08e?setupid=ScheduledJobs&fcf=00B50000008XBAi"

browser.get(url)


title ="Delete - Record 1 - f8230c90-88f2-813b-aef4-1ea145f3019e"
browser.find_element_by_xpath("//a[@title='Delete - Record 1 - f8230c90-88f2-813b-aef4-1ea145f3019e']")
title = "Delete - Record 3 - Scorecard Snapshot Population"
browser.find_element_by_xpath("//a[@title='Delete - Record 3 - Scorecard Snapshot Population']")

"hit enter"
