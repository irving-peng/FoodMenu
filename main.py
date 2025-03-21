#
# Client-side python app for benford app, which is calling
# a set of lambda functions in AWS through API Gateway.
# The overall purpose of the app is to process a PDF and
# see if the numeric values in the PDF adhere to Benford's
# law.
#
# Authors:
#   Irving Peng
#
#   Prof. Joe Hummel (initial template)
#   Northwestern University
#   CS 310
#

import requests
import jsons

import uuid
import pathlib
import logging
import sys
import os
import base64
import time
import random

from configparser import ConfigParser


############################################################
#
# classes
#
class User:

  def __init__(self, row):
    self.userid = row[0]
    self.username = row[1]
    self.gender = row[2]
    self.age = row[3]
    self.height = row[4]
    self.currentweight = row[5]
    self.goalweight = row[6]
    self.weightgoal = row[7]
    self.nutritiongoal = row[8]
    self.period = row[9]




###################################################################
#
# web_service_get
#
# When calling servers on a network, calls can randomly fail. 
# The better approach is to repeat at least N times (typically 
# N=3), and then give up after N tries.
#
def web_service_get(url):
  """
  Submits a GET request to a web service at most 3 times, since 
  web services can fail to respond e.g. to heavy user or internet 
  traffic. If the web service responds with status code 200, 400 
  or 500, we consider this a valid response and return the response.
  Otherwise we try again, at most 3 times. After 3 attempts the 
  function returns with the last response.
  
  Parameters
  ----------
  url: url for calling the web service
  
  Returns
  -------
  response received from web service
  """

  try:
    retries = 0
    
    while True:
      response = requests.get(url)
        
      if response.status_code in [200, 400, 480, 481, 482, 500]:
        #
        # we consider this a successful call and response
        #
        break

      #
      # failed, try again?
      #
      retries = retries + 1
      if retries < 3:
        # try at most 3 times
        time.sleep(retries)
        continue
          
      #
      # if get here, we tried 3 times, we give up:
      #
      break

    return response

  except Exception as e:
    print("**ERROR**")
    logging.error("web_service_get() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return None
    

############################################################
#
# prompt
#
def prompt():
  """
  Prompts the user and returns the command number

  Parameters
  ----------
  None

  Returns
  -------
  Command number entered by user (0, 1, 2, ...)
  """
  try:
    print()
    print(">> Enter a command:")
    print("   0 => end")
    print("   1 => users")
    print("   2 => create user")
    print("   3 => daily calories")
    print("   4 => generate menu")
    print("   5 => customize menu")

    cmd = input()

    if cmd == "":
      cmd = -1
    elif not cmd.isnumeric():
      cmd = -1
    else:
      cmd = int(cmd)

    return cmd

  except Exception as e:
    print("**ERROR")
    print("**ERROR: invalid input")
    print("**ERROR")
    return -1


############################################################
#
# users
#
def users(baseurl):
  """
  Prints out all the users in the database

  Parameters
  ----------
  baseurl: baseurl for web service

  Returns
  -------
  nothing
  """

  try:
    #
    # call the web service:
    #
    user_id = input("enter your user id: ")
    api = '/users/' + user_id
    url = baseurl + api

    # res = requests.get(url)
    res = web_service_get(url)

    #
    # let's look at what we got back:
    #
    if res.status_code == 200: #success
      print("sucess for users")
      pass
    else:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 500:
        # we'll have an error message
        body = res.json()
        print("Error message:", body)
      #
      return

    #
    # deserialize and extract users:
    #
    body = res.json()

    print(body)


    user = User(body)  

    # for user in users:
    print(user.userid)
    print(" ","username:", user.username)
    print(" ","gender:", user.gender)
    print(" ", "age:", str(user.age))
    print(" ", "height:", str(user.height))
    print(" ", "current weight:", str(user.currentweight))
    print(" ", "goal weight:", user.goalweight)
    print(" ", "weight goal:", user.weightgoal)
    print(" ", "nurition goal:", user.nutritiongoal)
    print(" ", "period:", str(user.period))
    #
    return

  except Exception as e:
    logging.error("**ERROR: users() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return
  
############################################################
#
# add user
#
def add_user(baseurl):
    username = input("Enter your username: ")
    gender = input("Enter your gender: ")
    age = int(input("Enter your age: "))
    height = int(input("Enter your height in inches: "))
    currentweight = int(input("Enter your current weight in lbs: "))
    goalweight = int(input("Enter your goal weight in lbs: "))
    weightgoal = input("Enter your goal (lose/maintain/gain): ")
    nutritiongoal = input("Enter your diet goal (regular/body_builder/weight_gain): ")
    period = int(input("Enter your diet period in days: "))

    data = { "username": username, 
            "gender": gender,
            "age": age, 
            "height": height, 
            "currentweight": currentweight, 
            "goalweight": goalweight, 
            "weightgoal": weightgoal, 
            "nutritiongoal": nutritiongoal, 
            "period": period}
    
    api = "/users"
    url = baseurl + api
    res = requests.post(url, json=data)
    body = res.json()


    if res.status_code == 200: 
      #success
      print("your user account have been created with user id:", body)
    else:
      # failed:
      print("Failed with status code:", res.status_code)

def cal(baseurl):
    user_id = input("Please enter your user id: ")
    api = "/cal/" + user_id
    url = baseurl + api
    res = requests.get(url)
    body = res.json()
    if res.status_code == 200:
      # sucess
      print("Goal type:", body["nutritiongoal"])
      print("  Daily calorie:", body["cal_per_day"], "cals")
      print("  Breakfast calorie:", body["breakfast_cal"], "cals")
      print("  Lunch calorie:", body["lunch_cal"], "cals")
      print("  Dinner calorie:", body["dinner_cal"], "cals")
    else:
      #failed
      print("Failed with status code:", res.status_code)

def menu(baseurl):
    user_id = input("Please enter your user id: ")
    api = "/cookbook/" + user_id
    url = baseurl + api
    res = requests.get(url)
    body = res.json()
    breakfast = body["breakfast"]
    lunch = body["lunch"]
    dinner = body["dinner"]

    if res.status_code == 200:
        # sucess
        print("Menu!")
        print("--------------------")
        print("Breakfast")
        print("  Carbs")
        print(f"    {breakfast["carbohydrates"][0][0]}---{breakfast["carbohydrates"][0][1]} g")
        print("  Protein")
        print(f"    {breakfast["protein"][0][0]}---{breakfast["protein"][0][1]} g")
        print("  Fat")
        print(f"    {breakfast["fat"][0][0]}---{breakfast["fat"][0][1]} g")
        print("--------------------")

        print("Lunch")
        carbs_food = lunch["carbohydrates"]
        protein_food = lunch["protein"]
        fat_food = lunch["fat"]
        print("  Carbs")
        for i in range(len(carbs_food)):
            print(f"    {lunch["carbohydrates"][i][0]}---{lunch["carbohydrates"][i][1]} g")
        print("  Protein")
        for i in range(len(protein_food)):
          print(f"    {lunch["protein"][i][0]}---{lunch["protein"][i][1]} g")
        print("  Fat")
        for i in range(len(fat_food)):
          print(f"    {lunch["fat"][i][0]}---{lunch["fat"][i][1]} g")
        print("--------------------")

        print("Dinner")
        carbs_food = dinner["carbohydrates"]
        protein_food = dinner["protein"]
        fat_food = dinner["fat"]
        print("  Carbs")
        for i in range(len(carbs_food)):
            print(f"    {lunch["carbohydrates"][i][0]}---{lunch["carbohydrates"][i][1]} g")
        print("  Protein")
        for i in range(len(protein_food)):
          print(f"    {lunch["protein"][i][0]}---{lunch["protein"][i][1]} g")
        print("  Fat")
        for i in range(len(fat_food)):
          print(f"    {lunch["fat"][i][0]}---{lunch["fat"][i][1]} g")
        print("--------------------")
    else:
        #failed
        print("Failed with status code:", res.status_code)

def customize_menu(baseurl):
    user_id = int(input("Enter your userid: "))
    type = input("Enter a category to customize(like/ dislike/ allergy): ")
    food = input("Enter food name: ")
    data = { 
        "userid": user_id, 
        "food": food,
        "type": type
    }
    api = "/users/customize"
    url = baseurl + api
    res = requests.post(url, json=data)
    body = res.json()

    if res.status_code == 200:
      print("You have sucessfully customize your daily menu!")
    elif res.status_code == 500:
        try:
            body = res.json()
            print("Error message:", body)
        except ValueError:
            print("Error message (raw):", res.text)
    else:
        #failed
        print("Failed with status code:", res.status_code)

  

############################################################
# main
#
try:
  print('** Welcome to BenfordApp **')
  print()

  # eliminate traceback so we just get error message:
  sys.tracebacklimit = 0

  #
  # what config file should we use for this session?
  #
  config_file = 'client_config.ini'

  print("Config file to use for this session?")
  print("Press ENTER to use default, or")
  print("enter config file name>")
  s = input()

  if s == "":  # use default
    pass  # already set
  else:
    config_file = s

  #
  # does config file exist?
  #
  if not pathlib.Path(config_file).is_file():
    print("**ERROR: config file '", config_file, "' does not exist, exiting")
    sys.exit(0)

  #
  # setup base URL to web service:
  #
  configur = ConfigParser()
  configur.read(config_file)
  baseurl = configur.get('client', 'webservice')

  #
  # make sure baseurl does not end with /, if so remove:
  #
  if len(baseurl) < 16:
    print("**ERROR: baseurl '", baseurl, "' is not nearly long enough...")
    sys.exit(0)

  if baseurl == "https://YOUR_GATEWAY_API.amazonaws.com":
    print("**ERROR: update config file with your gateway endpoint")
    sys.exit(0)

  if baseurl.startswith("http:"):
    print("**ERROR: your URL starts with 'http', it should start with 'https'")
    sys.exit(0)

  lastchar = baseurl[len(baseurl) - 1]
  if lastchar == "/":
    baseurl = baseurl[:-1]

  #
  # main processing loop:
  #
  cmd = prompt()

  while cmd != 0:
    #
    if cmd == 1:
      users(baseurl)
    elif cmd == 2:
      add_user(baseurl)
    elif cmd == 3:
      cal(baseurl)
    elif cmd ==4:
      menu(baseurl)
    elif cmd ==5:
      customize_menu(baseurl)    
    else:
      print("** Unknown command, try again...")
    #
    cmd = prompt()

  #
  # done
  #
  print()
  print('** done **')
  sys.exit(0)

except Exception as e:
  logging.error("**ERROR: main() failed:")
  logging.error(e)
  sys.exit(0)
