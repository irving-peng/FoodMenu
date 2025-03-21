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
        print("**lambda: customise post**")
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

        if "body" not in event:
            raise Exception("event has no body")
        
        #
        # check body has required fields
        #
        print("**Checking body**")
        body = json.loads(event["body"]) # parse the json

        required_fields = {"userid", "food","type"}
        if not all(field in body for field in required_fields):
            raise Exception("Missing required fields in body")
        body["userid"] = int(body["userid"])
        
        print("**Body has the required fields**")

        type = body["type"]
        food = body["food"]
        userid = body["userid"]

        type_fields = {"allergy", "like", "dislike"}
        if type not in type_fields:
            raise Exception("type is not in the options: allergy, like, dislike") 
        #
        # open connection to the database and insert data
        #
        print("**Opening connection**")
        dbConn = datatier.get_dbConn(rds_endpoint, rds_portnum, rds_username, rds_pwd, rds_dbname)


        food_sql = "SELECT * FROM food WHERE foodname = %s"
        food_result = datatier.retrieve_one_row(dbConn, food_sql, [food])
        print("food result is :",food_result)
        if food_result is None or len(food_result) == 0:
            if type == "like":
                raise Exception("Food not found")
            else:
                return {
                'statusCode': 200,
                'body': json.dumps("success")
                }
        
        #
        #  insert data into the database
        #
        #
        print("**Inserting data**")
        foodid = food_result[0]
        
        insert_sql = "INSERT INTO user_customize (userid, foodid, type) VALUES (%s, %s, %s)"
        datatier.perform_action(dbConn, insert_sql, [userid, foodid, type])
        
        return {
        'statusCode': 200,
        'body': json.dumps(str("success"))
        }


    except Exception as err:
        print("**ERROR**")
        print(str(err))

        return {
            'statusCode': 500,
            'body': json.dumps(str(err))
        }
