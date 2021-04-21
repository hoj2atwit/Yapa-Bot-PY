import pymongo
from pymongo import MongoClient
import formatter

###DELETING###
def wipe_character_collection():
  character_collection = get_character_collection()
  character_collection.delete_many({})

def wipe_weapon_collection():
  weapon_collection = get_weapon_collection()
  weapon_collection.delete_many({})

def wipe_user_collection():
  user_collection = get_user_collection()
  user_collection.delete_many({})

def delete_user(_id):
  user_collection = get_user_collection()
  user_collection.delete_one({"_id":_id})






###SAVING###
def save_user(u):
  user_collection = get_user_collection()
  user_collection.replace_one({"_id" : u._id}, u.get_dict(), upsert=True)

def save_character(c):
  character_collection = get_character_collection()
  character_collection.replace_one({"URL_name" : c.URL_name}, c.get_dict(), upsert=True)

def save_weapon(w):
  weapon_collection = get_weapon_collection()
  weapon_collection.replace_one({"URL_name" : w.URL_name}, w.get_dict(), upsert=True)

def save_commissions(com_dict):
  commission_collection = get_commission_collection()
  commission_collection.replace_one({},com_dict, upsert=True)







###GETTERS###
def get_cluster():
  return MongoClient("mongodb+srv://Yapa-Bot-Official:zdKwyRadkUfZeqj4@yapa-cluster.btsf9.mongodb.net/Yapa-Bot?retryWrites=true&w=majority")

def get_time_collection():
  db_mongo = get_cluster().Yapa
  return db_mongo["Time"]

def get_commission_collection():
  db_mongo = get_cluster().Yapa
  return db_mongo["Commissions"]

def get_weapon_collection():
  db_mongo = get_cluster().Yapa
  return db_mongo["Weapons"]

def get_character_collection():
  db_mongo = get_cluster().Yapa
  return db_mongo["Characters"]

def get_user_collection():
  db_mongo = get_cluster().Yapa
  return db_mongo["Users"]

def get_user_dict(_id):
  user_collection = get_user_collection()
  return user_collection.find_one({"_id": int(_id)})

def get_character_dict(name):
  user_collection = get_user_collection()
  return user_collection.find_one({"URL_name": formatter.name_formatter(name)})

def get_weapon_dict(name):
  user_collection = get_user_collection()
  return user_collection.find_one({"URL_name": formatter.name_formatter(name)})

def get_all_users_list_ids():
  user_collection = get_user_collection()
  users = user_collection.find({})
  users_list = []
  for user in users:
    users_list.append(user['_id'])
  return users_list

def get_all_weapons_list():
  weapon_collection = get_weapon_collection()
  weapons = weapon_collection.find({})
  weapons_list = []
  for weapon in weapons:
    weapons_list.append(weapon)
  return weapons_list

def get_all_characters_list():
  character_collection = get_character_collection()
  characters = character_collection.find({})
  characters_list = []
  for character in characters:
    characters_list.append(character)
  return characters_list

def get_all_characters_of_criteria(search_criteria, value):
  character_collection = get_character_collection()
  characters = character_collection.find({search_criteria : value})
  characters_list = []
  for character in characters:
    characters_list.append(character)
  return characters_list

def get_all_weapons_of_criteria(search_criteria, value):
  weapon_collection = get_weapon_collection()
  weapons = weapon_collection.find({search_criteria : value})
  weapons_list = []
  for weapon in weapons:
    weapons_list.append(weapon)
  return weapons_list

def get_commissions_of_type(comType):
  commission_collection = get_commission_collection()
  commissions = commission_collection.find_one({})
  return commissions[comType]

def get_last_resin_time():
  time_collection = get_time_collection()
  times = time_collection.find_one({})
  return times["last_resin_time"]





###UPDATING###
def update_last_resin_time(time):
  time_collection = get_time_collection()
  time_collection.update_one({}, {"$set":{"last_resin_time": time}})