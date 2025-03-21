import json
import datatier
import requests
import os
import random
from configparser import ConfigParser

# dataset analysis 
food_category = {
    "meat": "protein",
    "dairy": "fat",
    "oil": "fat",
    "other": "carbohydrates",
    "side": "carbohydrates",
    "fruits": "carbohydrates",
    "mainfood": "carbohydrates",
    "Soups": "carbohydrates",
    "dessert": "fat"
}
#

# retio
macro_distribution = {
    "regular": {
        "breakfast": (0.50, 0.20, 0.30),
        "lunch": (0.45, 0.25, 0.30),
        "dinner": (0.40, 0.30, 0.30)
    },
    "body_builder": {
        "breakfast": (0.50, 0.25, 0.25),
        "lunch": (0.45, 0.30, 0.25),
        "dinner": (0.40, 0.35, 0.25)
    },
    "weight_gain": {
        "breakfast": (0.65, 0.15, 0.20),
        "lunch": (0.60, 0.20, 0.20),
        "dinner": (0.55, 0.25, 0.20)
    }
}


def lambda_handler(event, context):
  try:
    print("**STARTING**")
    print("**lambda: proj03_jobs**")
    
    #
    # setup AWS based on config file:
    #
    config_file = 'cookbook-config.ini'
    os.environ['AWS_SHARED_CREDENTIALS_FILE'] = config_file
    config_file_cal = 'cal-config.ini'

    configur = ConfigParser()
    configur.read(config_file)
    configur_cal = ConfigParser()
    configur_cal.read(config_file_cal)

    #
    # configure for RDS access
    #
    rds_endpoint = configur.get('rds', 'endpoint')
    rds_portnum = int(configur.get('rds', 'port_number'))
    rds_username = configur.get('rds', 'user_name')
    rds_pwd = configur.get('rds', 'user_pwd')
    rds_dbname = configur.get('rds', 'db_name')

    cal_endpoint = configur_cal.get('client', 'webservice')


    if "userid" in event:
        userid = event["userid"]
    elif "pathParameters" in event:
        if "userid" in event["pathParameters"]:
            userid = event["pathParameters"]["userid"]
        else:
            raise Exception("requires userid parameter in pathParameters")
    else:
        raise Exception("requires userid parameter in event")

    #
    # open connection to the database
    #
    print("**Opening connection**")
    dbConn = datatier.get_dbConn(rds_endpoint, rds_portnum, rds_username, rds_pwd, rds_dbname)
    
    #
    # get user cal per day
    #
    cal = requests.get(cal_endpoint + "/cal/" + str(userid))
    if cal.status_code != 200:
      return {
      'statusCode': 500,
      'body': json.dumps(str("Unable to get user cal"))
      }
    
    cal = cal.json()
    cal_meal = {
      "breakfast": cal["breakfast_cal"],
      "lunch": cal["lunch_cal"],
      "dinner": cal["dinner_cal"],
    }

    nutrition_goal = cal["nutritiongoal"]
    
    print("** get cal per day the cal is:" + str(cal) + "**")


    with open("food_combine.json", "r") as file:
      food_data = json.load(file)
    three_meals = ["breakfast", "lunch", "dinner"]
    
    cookbook = {
      "breakfast": {
        "carbohydrates": [],
        "fat": [],
        "protein": []
      },
      "lunch": {
        "carbohydrates": [],
        "fat": [],
        "protein": []
      },
      "dinner": {
        "carbohydrates": [],
        "fat": [],
        "protein": []
      }
    }
    for meal in three_meals:
      # cal ratio
      ratio = macro_distribution[nutrition_goal][meal]  
      carb_cal = round(cal_meal[meal] * ratio[0], 2)   
      protein_cal = round(cal_meal[meal] * ratio[1], 2)  
      fat_cal = round(cal_meal[meal] * ratio[2], 2)       

      food_choice = random.choice(food_data[meal])
      categorized_foods = classify_food_choices(food_choice)
      food_type = ["carbohydrates", "fat", "protein"]
      # carb
      for typ in food_type:
        print("** processing ", typ)
        food_cat  = categorized_foods[typ]
        foodid = []
        for food in food_cat:
          cal_sql = "SELECT foodid FROM food_type WHERE Category = %s"
          cab_rows = datatier.retrieve_all_rows(dbConn, cal_sql,[food])
          foodid.append(cab_rows[random.randint(0, len(cab_rows) - 1)][0])
        print(foodid)
        food_with_cal = []
        for food in foodid:
          sql = "SELECT foodname,calories FROM food WHERE foodid = %s"
          row = datatier.retrieve_one_row(dbConn, sql,[food])
          food_with_cal.append(row)
        print(food_with_cal)
        print("** processing food with cal")
        if typ == "carbohydrates":
          target_cal = carb_cal
        elif typ == "fat":
          target_cal = fat_cal
        else:
          target_cal = protein_cal
        per_food_cal = target_cal / len(food_with_cal)
        food_with_gram = [[fc[0], round(per_food_cal/fc[1], 1)] for fc in food_with_cal]
        print("** food with gram in", meal, typ, food_with_gram)
        cookbook[meal][typ] = food_with_gram

    print(cookbook)
    return {
      'statusCode': 200,
      'body': json.dumps(cookbook)
    }
  except Exception as err:
    print("**ERROR**")
    print(str(err))
    
    return {
      'statusCode': 500,
      'body': json.dumps(str(err))
    }

def classify_food_choices(food_choice):
    categorized_foods = {
        "carbohydrates": [],
        "fat": [],
        "protein": []
    }

    for category in food_choice:
        if category in food_category:
            nutrient_type = food_category[category]  # 获取对应的营养类别
            categorized_foods[nutrient_type].append(category)

    return categorized_foods