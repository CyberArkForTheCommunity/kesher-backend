import os
import boto3
from typing import Optional
import mysql.connector

from aws_lambda_powertools.utilities import parameters as ssm_params
#rds settings
ENDPOINT  = "kesher.cluster-cqjsrrc4cikc.us-east-1.rds.amazonaws.com"
PORT = 3306
USR = 'admin'
REGION = 'us-east-1'
DBNAME = 'Kesher'
PASSWORD = 'Cyber123'

CONENCTION = None

def get_user_password() -> Optional[str]:
    try:
        client_name = ssm_params.get_parameter(os.getenv('USER_PASSWORD_SSM_PATH'), decrypt=True)
    except Exception as e:
        print('unable to retrieve idaptive client name from SSMdue to {}'.format(e))
        client_name = None
    return client_name


def create_connection_to_rds():
    session = boto3.Session()
    client = session.client('rds')
    token = client.generate_db_auth_token(DBHostname=ENDPOINT, Port=PORT, DBUsername=USR, Region=REGION)

    # we want to raise the origin exception
    try:
        return mysql.connector.connect(host=ENDPOINT, user=USR, passwd=get_user_password(), port=PORT, database=DBNAME)
    except Exception as exc:
        print("Database connection failed due to {}".format(exc))
        raise exc

def get_connection_to_rds():
    global CONENCTION
    if CONENCTION is None or not CONENCTION.is_connected():
        CONENCTION = create_connection_to_rds()
    return CONENCTION

def lambda_handler(event, context):
    connection = get_connection_to_rds()
    try:
        cur = connection.cursor()
        cur.execute("""SELECT now()""")
        query_results = cur.fetchall()
        print(query_results)
    except Exception as exc:
        print("Database connection failed due to {}".format(exc))     

lambda_handler({},{})