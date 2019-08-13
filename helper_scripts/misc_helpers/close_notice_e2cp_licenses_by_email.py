__author__ = 'Lothilius'

import sys
from HTMLParser import HTMLParser

import pandas as pd

from helper_scripts.misc_helpers.request_input_prompt import request_user_input
from send_email.OutlookConnection import OutlookConnection as out_look_email
from sfdc.SFDC_User_Licenses import SFDC_Package_Licenses as sfdc_licenses
from sfdc.SFDC_Users import SFDC_Users as sf_users
from okta.Okta_Application import Okta_Application
from os import environ

pd.set_option('display.width', 250)
pd.set_option('display.max_columns', 40)
pd.set_option('display.max_rows', 5)
pd.set_option('max_colwidth', 40)


e2cp = ('05050000000PD1HAAW', """<html xmlns:v=3D"urn:schemas-microsoft-com:vml" xmlns:o=3D"urn:schemas-microsof=
t-com:office:office" xmlns:w=3D"urn:schemas-microsoft-com:office:word" xmlns:m=
=3D"http://schemas.microsoft.com/office/2004/12/omml" xmlns=3D"http://www.w3.org=
/TR/REC-html40">
<head>
<meta http-equiv=3D"Content-Type" content=3D"text/html; charset=3Dutf-8">
<meta name=3D"Generator" content=3D"Microsoft Word 15 (filtered medium)">
<!--[if !mso]><style>v\:* {behavior:url(#default#VML);}
o\:* {behavior:url(#default#VML);}
w\:* {behavior:url(#default#VML);}
.shape {behavior:url(#default#VML);}
</style><![endif]--><style><!--
/* Font Definitions */
@font-face
	{font-family:"Cambria Math";
	panose-1:2 4 5 3 5 4 6 3 2 4;}
@font-face
	{font-family:Calibri;
	panose-1:2 15 5 2 2 2 4 3 2 4;}
/* Style Definitions */
p.MsoNormal, li.MsoNormal, div.MsoNormal
	{margin:0in;
	margin-bottom:.0001pt;
	font-size:12.0pt;
	font-family:"Calibri",sans-serif;}
a:link, span.MsoHyperlink
	{mso-style-priority:99;
	color:#0563C1;
	text-decoration:underline;}
a:visited, span.MsoHyperlinkFollowed
	{mso-style-priority:99;
	color:#954F72;
	text-decoration:underline;}
p.MsoListParagraph, li.MsoListParagraph, div.MsoListParagraph
	{mso-style-priority:34;
	margin-top:0in;
	margin-right:0in;
	margin-bottom:0in;
	margin-left:.5in;
	margin-bottom:.0001pt;
	mso-add-space:auto;
	font-size:12.0pt;
	font-family:"Calibri",sans-serif;}
p.MsoListParagraphCxSpFirst, li.MsoListParagraphCxSpFirst, div.MsoListParag=
raphCxSpFirst
	{mso-style-priority:34;
	mso-style-type:export-only;
	margin-top:0in;
	margin-right:0in;
	margin-bottom:0in;
	margin-left:.5in;
	margin-bottom:.0001pt;
	mso-add-space:auto;
	font-size:12.0pt;
	font-family:"Calibri",sans-serif;}
p.MsoListParagraphCxSpMiddle, li.MsoListParagraphCxSpMiddle, div.MsoListPar=
agraphCxSpMiddle
	{mso-style-priority:34;
	mso-style-type:export-only;
	margin-top:0in;
	margin-right:0in;
	margin-bottom:0in;
	margin-left:.5in;
	margin-bottom:.0001pt;
	mso-add-space:auto;
	font-size:12.0pt;
	font-family:"Calibri",sans-serif;}
p.MsoListParagraphCxSpLast, li.MsoListParagraphCxSpLast, div.MsoListParagra=
phCxSpLast
	{mso-style-priority:34;
	mso-style-type:export-only;
	margin-top:0in;
	margin-right:0in;
	margin-bottom:0in;
	margin-left:.5in;
	margin-bottom:.0001pt;
	mso-add-space:auto;
	font-size:12.0pt;
	font-family:"Calibri",sans-serif;}
p.msonormal0, li.msonormal0, div.msonormal0
	{mso-style-name:msonormal;
	mso-margin-top-alt:auto;
	margin-right:0in;
	mso-margin-bottom-alt:auto;
	margin-left:0in;
	font-size:11.0pt;
	font-family:"Calibri",sans-serif;}
span.EmailStyle19
	{mso-style-type:personal;
	font-family:"Calibri",sans-serif;
	color:windowtext;}
span.EmailStyle20
	{mso-style-type:personal;
	font-family:"Calibri",sans-serif;
	color:windowtext;}
span.EmailStyle21
	{mso-style-type:personal;
	font-family:"Calibri",sans-serif;
	color:windowtext;}
span.EmailStyle23
	{mso-style-type:personal-reply;
	font-family:"Calibri",sans-serif;
	color:windowtext;}
.MsoChpDefault
	{mso-style-type:export-only;
	font-size:10.0pt;}
@page WordSection1
	{size:8.5in 11.0in;
	margin:1.0in 1.0in 1.0in 1.0in;}
div.WordSection1
	{page:WordSection1;}
/* List Definitions */
@list l0
	{mso-list-id:1111361755;
	mso-list-type:hybrid;
	mso-list-template-ids:-1399425342 67698703 67698713 67698715 67698703 6769=
8713 67698715 67698703 67698713 67698715;}
@list l0:level1
	{mso-level-tab-stop:none;
	mso-level-number-position:left;
	text-indent:-.25in;}
@list l0:level2
	{mso-level-number-format:alpha-lower;
	mso-level-tab-stop:none;
	mso-level-number-position:left;
	text-indent:-.25in;}
@list l0:level3
	{mso-level-number-format:roman-lower;
	mso-level-tab-stop:none;
	mso-level-number-position:right;
	text-indent:-9.0pt;}
@list l0:level4
	{mso-level-tab-stop:none;
	mso-level-number-position:left;
	text-indent:-.25in;}
@list l0:level5
	{mso-level-number-format:alpha-lower;
	mso-level-tab-stop:none;
	mso-level-number-position:left;
	text-indent:-.25in;}
@list l0:level6
	{mso-level-number-format:roman-lower;
	mso-level-tab-stop:none;
	mso-level-number-position:right;
	text-indent:-9.0pt;}
@list l0:level7
	{mso-level-tab-stop:none;
	mso-level-number-position:left;
	text-indent:-.25in;}
@list l0:level8
	{mso-level-number-format:alpha-lower;
	mso-level-tab-stop:none;
	mso-level-number-position:left;
	text-indent:-.25in;}
@list l0:level9
	{mso-level-number-format:roman-lower;
	mso-level-tab-stop:none;
	mso-level-number-position:right;
	text-indent:-9.0pt;}
@list l1
	{mso-list-id:1894151123;
	mso-list-template-ids:1541185478;}
@list l1:level1
	{mso-level-start-at:3;
	mso-level-tab-stop:.5in;
	mso-level-number-position:left;
	text-indent:-.25in;}
@list l2
	{mso-list-id:2128966655;
	mso-list-template-ids:2029000624;}
ol
	{margin-bottom:0in;}
ul
	{margin-bottom:0in;}
--></style><!--[if gte mso 9]><xml>
<o:shapedefaults v:ext=3D"edit" spidmax=3D"1026" />
</xml><![endif]--><!--[if gte mso 9]><xml>
<o:shapelayout v:ext=3D"edit">
<o:idmap v:ext=3D"edit" data=3D"1" />
</o:shapelayout></xml><![endif]-->
</head>
<body lang=3D"EN-US" link=3D"#0563C1" vlink=3D"#954F72">
<div class=3D"WordSection1">
<p class=3D"MsoNormal"><a name=3D"_MailOriginalBody"><b><span style=3D"font-size:=
16.0pt;background:white">B<span style=3D"color:#333333">azaarvoice Salesforce =
Case Commenting: Custom =E2=80=98New Comment=E2=80=99 Button</span></span></b></a><span =
style=3D"mso-bookmark:_MailOriginalBody"><span style=3D"font-size:16.0pt;color:#=
333333"><br>
<br>
<span style=3D"background:white">The Business Technology team will be rolling=
 out a customized replacement of the Salesforce Case Comment functionality k=
nown as the 'New Comment' button</span></span></span><span style=3D"mso-bookma=
rk:_MailOriginalBody"><span style=3D"font-size:16.0pt">
<span style=3D"color:#333333;background:white">(part of the Email to Case Pre=
mium product).&nbsp;</span><span style=3D"color:#333333"><br>
<br>
<span style=3D"background:white">This in-house solution provides the same cor=
e functionality, with some slight improvements suited to Bazaarvoice=E2=80=99s nee=
ds. The custom =E2=80=98New Comment=E2=80=99 interface leverages the Salesforce Lightnin=
g design look and feel.&nbsp;</span><br>
<br>
<span style=3D"background:white">With this new solution, you will be able to =
update Salesforce tickets with public or private comments, insert pre-define=
d templates, add additional recipients, as well as add attachment files to n=
ew comments.</span></span></span><o:p></o:p></span></p>
<p class=3D"MsoNormal"><span style=3D"mso-bookmark:_MailOriginalBody"><span sty=
le=3D"font-size:16.0pt">&nbsp;</span><o:p></o:p></span></p>
<p class=3D"MsoNormal"><span style=3D"mso-bookmark:_MailOriginalBody"><span sty=
le=3D"font-size:16.0pt">While this should be a seamless transition, there are =
a few things to be aware of.
</span><o:p></o:p></span></p>
<p class=3D"MsoNormal"><span style=3D"mso-bookmark:_MailOriginalBody"><span sty=
le=3D"font-size:16.0pt">&nbsp;</span><o:p></o:p></span></p>
<ol style=3D"margin-top:0in" start=3D"1" type=3D"1">
<li class=3D"MsoNormal" style=3D"mso-list:l0 level1 lfo3"><span style=3D"mso-book=
mark:_MailOriginalBody"><span style=3D"font-size:16.0pt">You can no longer add=
 additional team members to the Salesforce case ticket via the =E2=80=98New Commen=
t=E2=80=99 UI. This must be done from the
 case itself. </span></span><span style=3D"mso-bookmark:_MailOriginalBody"><o=
:p></o:p></span></li><li class=3D"MsoNormal" style=3D"mso-list:l0 level1 lfo3"><=
span style=3D"mso-bookmark:_MailOriginalBody"><span style=3D"font-size:16.0pt">W=
hen adding =E2=80=98Additional To:=E2=80=99, =E2=80=98Additional CC:=E2=80=99, or =E2=80=98Additional BCC:=
=E2=80=99 recipients, you MUST enter a semicolon =E2=80=9C;=E2=80=9D after each email
 address for the UI to lock in the address recipient. This applies even if =
you are only adding a single email address. Once you append the address with=
 a semicolon, or select an email address from the drop down, the recipient a=
ddress will be locked in.
</span></span><span style=3D"mso-bookmark:_MailOriginalBody"><o:p></o:p></spa=
n></li></ol>
<p class=3D"MsoNormal"><span style=3D"mso-bookmark:_MailOriginalBody"><span sty=
le=3D"font-size:16.0pt">&nbsp;</span><o:p></o:p></span></p>
<p class=3D"MsoNormal" style=3D"margin-left:.5in"><span style=3D"mso-bookmark:_Ma=
ilOriginalBody"><b><span style=3D"font-size:16.0pt">Example:</span></b></span>=
<span style=3D"mso-bookmark:_MailOriginalBody"><span style=3D"font-size:16.0pt">=
 Enter semicolon after email address
 or select email address from the drop-down menu. </span><o:p></o:p></span>=
</p>
<p class=3D"MsoNormal" style=3D"text-indent:.5in"><span style=3D"mso-bookmark:_Ma=
ilOriginalBody"><span style=3D"font-size:16.0pt"><img width=3D"370" height=3D"171"=
 style=3D"width:3.8541in;height:1.7812in" id=3D"Picture_x0020_6" src=3D"cid:image0=
01.png@01D3DB1E.98BCD3D0" alt=3D"cid:image001.png@01D3DB1B.B3B638A0"></span><o=
:p></o:p></span></p>
<p class=3D"MsoNormal"><span style=3D"mso-bookmark:_MailOriginalBody"><span sty=
le=3D"font-size:16.0pt">&nbsp;</span><o:p></o:p></span></p>
<p class=3D"MsoNormal"><span style=3D"mso-bookmark:_MailOriginalBody"><span sty=
le=3D"font-size:16.0pt">&nbsp;</span><o:p></o:p></span></p>
<p class=3D"MsoNormal" style=3D"margin-left:.5in"><span style=3D"mso-bookmark:_Ma=
ilOriginalBody"><span style=3D"font-size:16.0pt">Address is locked into =E2=80=9CAdd=
itional To=E2=80=9D field.
</span><o:p></o:p></span></p>
<p class=3D"MsoNormal" style=3D"text-indent:.5in"><span style=3D"mso-bookmark:_Ma=
ilOriginalBody"><span style=3D"font-size:16.0pt"><img width=3D"411" height=3D"138"=
 style=3D"width:4.2812in;height:1.4375in" id=3D"Picture_x0020_5" src=3D"cid:image0=
02.png@01D3DB1E.98BCD3D0" alt=3D"cid:image005.png@01D3DB1B.B3B638A0"></span><o=
:p></o:p></span></p>
<p class=3D"MsoNormal"><span style=3D"mso-bookmark:_MailOriginalBody"><span sty=
le=3D"font-size:16.0pt">&nbsp;</span><o:p></o:p></span></p>
<ol style=3D"margin-top:0in" start=3D"3" type=3D"1">
<li class=3D"MsoNormal" style=3D"mso-list:l0 level1 lfo3"><span style=3D"mso-book=
mark:_MailOriginalBody"><span style=3D"font-size:16.0pt">Within the =E2=80=98Comment=
s=E2=80=99 section of a new comment, the Public/Private check column has changed t=
o an oval image indicating if the
 comment is Public or Private, instead of a check box. The Public or Privat=
e status is now much more obvious at a glance.
</span></span><span style=3D"mso-bookmark:_MailOriginalBody"><o:p></o:p></spa=
n></li><li class=3D"MsoNormal" style=3D"mso-list:l0 level1 lfo3"><span style=3D"ms=
o-bookmark:_MailOriginalBody"><span style=3D"font-size:16.0pt">In the =E2=80=98Comme=
nts=E2=80=99 section of a new comment, the =E2=80=9CCreated by=E2=80=9D hyperlink does not tak=
e you to that user=E2=80=99s Salesforce profile as it
 did in the previous case commenting interface. </span></span><span style=3D"=
mso-bookmark:_MailOriginalBody"><o:p></o:p></span></li><li class=3D"MsoNormal"=
 style=3D"mso-list:l0 level1 lfo3"><span style=3D"mso-bookmark:_MailOriginalBody=
"><span style=3D"font-size:16.0pt">In the =E2=80=98Comments=E2=80=99 section of a new comm=
ent, the =E2=80=9CRecipients=E2=80=9D text is not hyperlinked as it is in legacy Email 2=
 case premium. In
 legacy Email 2 case premium, clicking on the recipient=E2=80=99s email address w=
ould open an email to that recipient in your native email client.
</span></span><span style=3D"mso-bookmark:_MailOriginalBody"><o:p></o:p></spa=
n></li><li class=3D"MsoNormal" style=3D"mso-list:l0 level1 lfo3"><span style=3D"ms=
o-bookmark:_MailOriginalBody"><span style=3D"font-size:16.0pt">In the =E2=80=98Comme=
nts=E2=80=99 section of a new comment: There is a down arrow beside the time/date.=
 If you hover over it, the cursor will change
 to indicate it is selectable, but the UI does not allow you to select it. =
</span>
</span><span style=3D"mso-bookmark:_MailOriginalBody"><o:p></o:p></span></li>=
</ol>
<p class=3D"MsoNormal"><span style=3D"mso-bookmark:_MailOriginalBody"><span sty=
le=3D"font-size:16.0pt">&nbsp;</span><o:p></o:p></span></p>
<p class=3D"MsoNormal"><span style=3D"mso-bookmark:_MailOriginalBody"><b><span =
style=3D"font-size:16.0pt;color:black">Functions the same as legacy case comme=
nting, but worth noting:</span></b><o:p></o:p></span></p>
<p class=3D"MsoNormal"><span style=3D"mso-bookmark:_MailOriginalBody"><span sty=
le=3D"font-size:16.0pt;color:#454545">-Only very specific key words will trigg=
er a warning reminding you to attach a file.&nbsp;These key words are case s=
ensitive.</span><o:p></o:p></span></p>
<p class=3D"MsoNormal"><span style=3D"mso-bookmark:_MailOriginalBody"><span sty=
le=3D"font-size:16.0pt;color:#454545">-The warning is a yellow bar above the C=
omment field. It is no longer red.&nbsp;</span><o:p></o:p></span></p>
<p class=3D"MsoNormal"><span style=3D"mso-bookmark:_MailOriginalBody"><span sty=
le=3D"font-size:16.0pt;color:#454545">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbs=
p;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;=E2=80=9CI have attached=E2=80=9D</span><o:p></o:p></spa=
n></p>
<p class=3D"MsoNormal"><span style=3D"mso-bookmark:_MailOriginalBody"><span sty=
le=3D"font-size:16.0pt;color:#454545">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbs=
p;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;=E2=80=9Csee attached=E2=80=9D. (=E2=80=9CSee attached=E2=80=9D will=
 Not trigger the warning)</span><o:p></o:p></span></p>
<p class=3D"MsoNormal"><span style=3D"mso-bookmark:_MailOriginalBody"><span sty=
le=3D"font-size:16.0pt;color:#454545">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbs=
p;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;=E2=80=9Cattached a file=E2=80=9D</span><o:p></o:p></spa=
n></p>
<p class=3D"MsoNormal"><span style=3D"mso-bookmark:_MailOriginalBody"><span sty=
le=3D"font-size:16.0pt;color:#454545">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbs=
p;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;=E2=80=9CI=E2=80=99ve attached=E2=80=9D</span><o:p></o:p></spa=
n></p>
<p class=3D"MsoNormal"><span style=3D"mso-bookmark:_MailOriginalBody"><span sty=
le=3D"font-size:16.0pt;color:#454545">&nbsp;</span><o:p></o:p></span></p>
<p class=3D"MsoNormal"><span style=3D"mso-bookmark:_MailOriginalBody"><span sty=
le=3D"font-size:16.0pt;color:#454545">&nbsp;</span><o:p></o:p></span></p>
<p class=3D"MsoNormal"><span style=3D"mso-bookmark:_MailOriginalBody"><span sty=
le=3D"font-size:16.0pt;color:#454545">Custom Case Commenting (Lightning Interf=
ace) look.</span><o:p></o:p></span></p>
<p class=3D"MsoNormal"><span style=3D"mso-bookmark:_MailOriginalBody"><span sty=
le=3D"font-size:16.0pt;color:#454545">&nbsp;</span><o:p></o:p></span></p>
<p class=3D"MsoNormal"><span style=3D"mso-bookmark:_MailOriginalBody"><span sty=
le=3D"font-size:16.0pt"><img width=3D"624" height=3D"481" style=3D"width:6.5in;heigh=
t:5.0104in" id=3D"Picture_x0020_4" src=3D"cid:image003.png@01D3DB1E.98BCD3D0" al=
t=3D"cid:image006.png@01D3DB1B.B3B638A0"></span><o:p></o:p></span></p>
<p class=3D"MsoNormal"><span style=3D"mso-bookmark:_MailOriginalBody"><span sty=
le=3D"font-size:11.0pt">&nbsp;</span></span><o:p></o:p></p>
</div>
</body>
</html>
""")


license_list = [e2cp]#, gainsight, workit]

# Create email addresses.
def create_email_address(name):
    email = name.replace(' ', '.')
    email = email + '@bazaarvoice.com'

    return email

# Create the body of the message
def create_license_request_body(full_name, license):
    first_name = full_name.split()[0]
    body = license

    return body


def create_deprovisioning_body(user_list):
    """ Create the HTML body for emailing the data frame that is passed to it.
    :param user_list: Must be a Pandas Dataframe
    :return: sting of the html ready to send in an email.
    """
    html = HTMLParser()
    user_list = user_list.to_html()

    # Get Style sheet for the email.
    f = open('/Users/%s/Downloads/bv_tools/static/styleTags.html' % environ['USER'], 'r')
    style = f.readlines()
    style = ' '.join(style)
    style = html.unescape(style)

    body = '<html><head>%s</head><body>' % (style) + \
           '<h2>Please check and Deprovision as necessary</h2>' + html.unescape(user_list) + '<br><br>'\
           '</body></html>'

    return body

def main():
    try:
        outlook = out_look_email()
    except Exception, exc:
        sys.exit("mail failed1; %s" % str(exc))

    try:
        # Get Active SFDC user
        sfdc_users = sf_users().get_user_list()
        sfdc_users.rename(columns={'Id': 'UserId'}, inplace=True)
        sfdc_users['Email'] = sfdc_users['Email'].apply(lambda x: x.lower())
        sfdc_users = sfdc_users[sfdc_users['IsActive'] == True]

        # Get Workday Users
        workday = Okta_Application(app_name='workday')
        current_emplyee_list = workday.app_users

        current_emplyee_list.rename(columns={'email': 'Email'}, inplace=True)
        current_emplyee_list['Email'] = current_emplyee_list['Email'].apply(lambda x: x.lower())

        print current_emplyee_list.columns

    except IOError, error:
        print 'Try Again ' + str(error)  # give a error message

    # Get list of licenses with user.
    licensed_users = sfdc_licenses().get_license_list()

    # print licensed_users

    users_and_license = licensed_users.merge(sfdc_users, on='UserId', how='inner')
    # print users_and_license
    left_outer_list = users_and_license.merge(current_emplyee_list, on='Email', how='left')
    print "<---------- deprovision_list ---------->"
    deprovision_list = left_outer_list[
        (left_outer_list['employeeID'].isnull())
        &
        (~left_outer_list['UserName'].str.contains(
            'AutoCaseUser|Integration|BizApps|Apttus Cache Warmer|Tableau'))].copy()

    deprovision_list.drop_duplicates(subset=['UserName', 'Email', 'UserId'], keep='first', inplace=True)
    # body = create_deprovisioning_body(deprovision_list[['UserName', 'Email', 'UserId']])
    # outlook.create_helpdesk_ticket(subject='Users not found as active employees.', body=body, html=body)

    # Gather user with E2CP licenses.
    e2cp_users = users_and_license[['PackageLicenseId', 'UserId',
                                    'Email', 'UserName']][users_and_license['PackageLicenseId'] == e2cp[0]]


    # Gather list of user emails that have the license and are not on the deprovision list
    print "<---------- Emailing ---------->"
    users_to_ask = e2cp_users[~e2cp_users['Email'].isin(deprovision_list['Email'].tolist())][['Email', 'UserName']].values.tolist()
    e2cp_users[~e2cp_users['Email'].isin(deprovision_list['Email'].tolist())][['Email', 'UserName']].to_csv('/Users/martin.valenzuela/Downloads/recieved_email_.csv')

    users_to_ask = e2cp_users[~e2cp_users['Email'].isin(deprovision_list['Email'].tolist())][['Email', 'UserName']]
    users_to_ask = users_to_ask.reset_index()
    users_to_ask = users_to_ask[['Email', 'UserName']].values.tolist()  # [users_to_ask['Email'] == 'abigail.schuman@bazaarvoice.com']
    print users_to_ask
    users_to_ask = [['martin', 'martin.valenzuela@bazaarvoice.com']]
    # Request user input...
    response = request_user_input(prompt='Ready to send emails?')
    if response == 'y':
        for each in users_to_ask:
            try:
                print each[0]
                body = create_license_request_body(each[1], e2cp[1])

                outlook.send_email(to='martin.valenzuela@bazaarvoice.com',
                                   subject='License usage in SFDC',
                                   body=body, html=body)# reply_to='helpdesk@bazaarvoice.com', files=['', ''])
            except:
                print "Error did not send."
                # sys.exit("mail failed2; %s" % str(exc))  # give a error message
                pass
    else:
        print 'Good bye!'

if __name__ == '__main__':
    main()


