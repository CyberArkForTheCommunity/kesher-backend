import os

from mysql.connector import MySQLConnection
import mysql.connector

from service.access_layer.utils.get_from_ssm import get_creds, RdsConnectionParams


SECRET_PATH = "rds-cdk"
REGION = "us-east-1"
#rds settings
DBNAME = 'Kesher'

CONENCTION: MySQLConnection = None

def create_connection_to_rds() -> MySQLConnection:
    print('started create_connection_to_rds')
    secret_params: RdsConnectionParams = get_creds(os.getenv('RDS_SECRET_PATH', SECRET_PATH), os.getenv('REGION', REGION))
    print('got secret_params')
    # we want to raise the origin exception
    try:
        return mysql.connector.connect(host=secret_params.host, user=secret_params.username,
         passwd=secret_params.password.get_secret_value(), port=secret_params.port, database=DBNAME)
    except Exception as exc:
        print("Database connection failed due to {}".format(exc))
        raise exc

def get_connection_to_rds() -> MySQLConnection:
    global CONENCTION
    if CONENCTION is None or not CONENCTION.is_connected():
        CONENCTION = create_connection_to_rds()
    return CONENCTION

