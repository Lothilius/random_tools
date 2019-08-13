# coding: utf-8
__author__ = 'Lothilius'

import mysql.connector as mysql
from os import environ
import sshtunnel


host = environ['JIRA_DEV2_HOST']
user = environ['JIRA_PROD_RDS_USER']
password = environ['JIRA_DEV2_RDS']
port = 3306
db = environ['JIRA_DEV2_RDS_HOST']

with sshtunnel.SSHTunnelForwarder(
        (host, 22),
        ssh_username='ec2-user',
        ssh_pkey=environ['TF_VAR_ssh_key_path'],
        # local_bind_address=('localhost', 3306),
        remote_bind_address=('127.0.0.1', 3306),
) as tunnel: # See if the network layer is listing on 3306
    print(tunnel.local_bind_port)
    connection = mysql.connect(
        user=user,
        password=password,
        host='127.0.0.1',
        port=port,
        database=db)
    # Example of how to fetch table data:
    connection.query("""SELECT * FROM cwd_user""")
    result = connection.store_result()
    for i in range(result.num_rows()):
        print(result.fetch_row())

    connection.close()


