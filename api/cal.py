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
        print("**lambda: calc cal per day**")
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

        # Calculating calorie each day ##
        gender = result[2]
        age = result[3]
        height = result[4]
        current_weight = result[5]
        goal_weight = result[6]
        weight_goal = result[7]
        nutrition_goal = result[8]
        period = result[9]
        # bmr
        if gender == "male":
            bmr = 66 + (6.23 * current_weight) + (12.7 * height) - (6.8 * age)
        else:
            bmr =  655 + (4.3 * current_weight) + (4.7 * height) - (4.7 * age)
        print("bmr is ", bmr)
        #tdee
        if nutrition_goal == "regular":
            tdee = 1.37 * bmr
        elif nutrition_goal == "body_builder":
            tdee = 1.55 * bmr
        else:
            tdee = 1.2 * bmr
        print("tdee is :", tdee)
        # calorie per day
        if weight_goal == "maintain":
            cal_per_day = tdee

        elif weight_goal == "lose":
            weight_loss = current_weight - goal_weight
            min_days_need = weight_loss / 0.19

            ratio =  period / min_days_need
            cal_per_day = tdee - (500 // ratio) # tdee minus deficit

        else:

            weight_gain = goal_weight - current_weight
            min_days_need = weight_gain / 0.19
            
            ratio = period / min_days_need
            cal_per_day = tdee + (500 // ratio) # tdee plus deficit
    




        meal_distribution = {
            ("maintain", "regular"): (0.3, 0.4, 0.3),
            ("maintain", "body_builder"): (0.35, 0.45, 0.2),
            ("maintain", "weight_gain"): (0.35, 0.4, 0.25),
            ("lose", "regular"): (0.4, 0.4, 0.2),
            ("lose", "body_builder"): (0.35, 0.5, 0.15),
            ("lose", "weight_gain"): (0.4, 0.35, 0.25),
            ("gain", "regular"): (0.3, 0.4, 0.3),
            ("gain", "body_builder"): (0.35, 0.45, 0.2),
            ("gain", "weight_gain"): (0.4, 0.4, 0.2)
            }


        breakfast_ratio, lunch_ratio, dinner_ratio = meal_distribution[(weight_goal, nutrition_goal)]
        breakfast_cal = round(cal_per_day * breakfast_ratio, 2)
        lunch_cal = round(cal_per_day * lunch_ratio, 2)
        dinner_cal = round(cal_per_day * dinner_ratio, 2)

        # wrap result  in json
        data = {
            "nutritiongoal":nutrition_goal,
            "cal_per_day": round(cal_per_day, 2),
            "breakfast_cal": breakfast_cal,
            "lunch_cal": lunch_cal,
            "dinner_cal": dinner_cal
        }
        #
        # respond in an HTTP-like way, i.e. with a status
        # code and body in JSON format:
        #
        print("**DONE, returning rows**")
        
        return {
        'statusCode': 200,
        'body': json.dumps(data)
        }
        


    except Exception as err:
        print("**ERROR**")
        print(str(err))

        return {
            'statusCode': 500,
            'body': json.dumps(str(err))
        }