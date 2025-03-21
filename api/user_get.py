import json
import boto3
import os
import uuid
import base64
import pathlib
import datatier

from configparser import ConfigParser

def lambda_handler(event, context):
    try:
        print("**STARTING**")
        print("**lambda: proj03_upload**")
        #
        # setup AWS based on config file:
        #
        config_file = 'cookbook-config.ini'
        os.environ['AWS_SHARED_CREDENTIALS_FILE'] = config_file
        
        configur = ConfigParser()
        configur.read(config_file)
        
        #
        # configure for RDS access
        #
        rds_endpoint = configur.get('rds', 'endpoint')
        rds_portnum = int(configur.get('rds', 'port_number'))
        rds_username = configur.get('rds', 'user_name')
        rds_pwd = configur.get('rds', 'user_pwd')
        rds_dbname = configur.get('rds', 'db_name')

        if "userid" in event:
            userid = event["userid"]
        elif "pathParameters" in event:
            if "userid" in event["pathParameters"]:
                userid = event["pathParameters"]["userid"]
            else:
                raise Exception("requires userid parameter in pathParameters")
        else:
            raise Exception("requires userid parameter in event")
            
        print("userid:", userid)

        #
        # open connection to the database
        #
        print("**Opening connection**")
        dbConn = datatier.get_dbConn(rds_endpoint, rds_portnum, rds_username, rds_pwd, rds_dbname)

        sql = "SELECT * FROM users WHERE userid = %s;"
        result = datatier.retrieve_one_row(dbConn, sql, [userid])
        if result == None:
            raise Exception("Userid not found")
        for row in result:
            print(row)

        #
        # respond in an HTTP-like way, i.e. with a status
        # code and body in JSON format:
        #
        print("**DONE, returning rows**")
        
        return {
        'statusCode': 200,
        'body': json.dumps(result)
        }
        


    except Exception as err:
        print("**ERROR**")
        print(str(err))

        return {
            'statusCode': 500,
            'body': json.dumps(str(err))
        }
