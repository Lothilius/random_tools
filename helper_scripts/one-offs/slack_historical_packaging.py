# coding: utf-8
__author__ = 'Lothilius'

import pandas as pd
from datetime import datetime


file_name = 'history.json'
path = '~/Downloads/720199/'
file_path = path + file_name

now = datetime.now().strftime('%Y-%m-%d_%H_%M_%S')

data = pd.read_json(file_path, orient='records')

chats_df = pd.DataFrame(columns=pd.DataFrame([data['PrivateUserMessage'][0]]).columns.to_list())

for each in data.PrivateUserMessage.to_list():
    chats_df = chats_df.append(each, ignore_index=True)

chats_df['Receiver'] = chats_df['receiver'].apply(lambda x: x['name'])
chats_df['Sender'] = chats_df['sender'].apply(lambda x: x['name'])

file_name_to_send = path + "user_chat_history_" + now + '.csv'
chats_df[['message', 'timestamp', 'Receiver', 'Sender']].to_csv(file_name_to_send, index=False, encoding='utf-8')
