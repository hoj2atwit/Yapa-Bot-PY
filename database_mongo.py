import pymongo
from pymongo import MongoClient
import formatter_custom

###COLLECTION GETTERS###
def get_cluster():
  return MongoClient("mongodb+srv://Yapa-Bot-Official:zdKwyRadkUfZeqj4@yapa-cluster.btsf9.mongodb.net/Yapa-Bot?retryWrites=true&w=majority")

def get_time_collection():
  db_mongo = get_cluster().Yapa
  return db_mongo["Time"]

def get_prefix_collection():
  db_mongo = get_cluster().Yapa
  return db_mongo["Prefix"]

def get_leaderboards_collection():
  db_mongo = get_cluster().Yapa
  return db_mongo["Leaderboards"]

def get_gambling_collection():
  db_mongo = get_cluster().Yapa
  return db_mongo["Gamble"]

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

def get_shop_item_collection():
  db_mongo = get_cluster().Yapa
  return db_mongo["Shop_Items"]

def get_shop_collection():
  db_mongo = get_cluster().Yapa
  return db_mongo["Shops"]



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

def wipe_shop_item_collection():
  shop_item_collection = get_shop_item_collection()
  shop_item_collection.delete_many({})

def wipe_shop_item_characters():
  shop_item_collection = get_shop_item_collection()
  shop_items_list = get_all_shop_items_list()
  for si in shop_items_list:
    try:
      if si["item"]["group"] == "character":
        shop_item_collection.delete_many({"item": si["item"]})
    except KeyError:
      pass





###SAVING###
def save_user(u):
  user_collection = get_user_collection()
  user_collection.replace_one({"_id" : u._id}, u.get_dict(), upsert=True)

def save_prefix(guild_id,pre):
  prefix_collection = get_prefix_collection()
  prefix_collection.replace_one({"guild_id": guild_id}, {"guild_id": guild_id, "prefix":pre}, upsert=True)

def save_character(c):
  character_collection = get_character_collection()
  character_collection.replace_one({"URL_name" : c.URL_name}, c.get_dict(), upsert=True)

def save_weapon(w):
  weapon_collection = get_weapon_collection()
  weapon_collection.replace_one({"URL_name" : w.URL_name}, w.get_dict(), upsert=True)

def save_commissions(com_dict):
  commission_collection = get_commission_collection()
  commission_collection.replace_one({},com_dict, upsert=True)

def save_shop_item(si):
  shop_items_collection = get_shop_item_collection()
  shop_items_collection.replace_one({"item": si.item}, si.get_dict(), upsert=True)

def save_shop(shop):
  shop_collection = get_shop_collection()
  shop_collection.replace_one({"_id" : shop._id}, shop.get_dict(), upsert=True)

def setup_jackpot():
  gambling_collection = get_gambling_collection()
  gambling_collection.replace_one({}, {"jackpot_primo": 10000, "jackpot_mora": 10000000}, upsert=True)

def setup_leaderboard():
  leaderboards_collection = get_leaderboards_collection()
  leaderboards_collection.replace_one({}, {"top_10":{}}, upsert=True)


###GETTERS###

def get_user_dict(_id):
  user_collection = get_user_collection()
  return user_collection.find_one({"_id": int(_id)})

def get_prefix(guild_id):
  prefix_collection = get_prefix_collection()
  return prefix_collection.find_one({"guild_id":guild_id})

def get_shop_dict(_id):
  shop_collection = get_shop_collection()
  return shop_collection.find_one({"_id": int(_id)})

def get_shop_item_dict(name):
  user_collection = get_shop_item_collection()
  return user_collection.find_one({"item": {"URL_name" : formatter_custom.name_formatter(name)}})

def get_character_dict(name):
  user_collection = get_character_collection()
  return user_collection.find_one({"URL_name": formatter_custom.name_formatter(name)})

def get_weapon_dict(name):
  user_collection = get_weapon_collection()
  return user_collection.find_one({"URL_name": formatter_custom.name_formatter(name)})

def get_all_users_list_ids():
  user_collection = get_user_collection()
  users = user_collection.find({})
  users_list = [user['_id'] for user in users]
  return users_list

def get_all_users():
  user_collection = get_user_collection()
  users = user_collection.find({})
  return users

def get_all_shop_items_list():
  shop_item_collection = get_shop_item_collection()
  shop_items = shop_item_collection.find({})
  shop_items_list = []
  for shop_item in shop_items:
    shop_items_list.append(shop_item)
  return shop_items_list

def get_all_weapons_list():
  weapon_collection = get_weapon_collection()
  weapons = weapon_collection.find({})
  weapons_list = []
  for weapon in weapons:
    weapons_list.append(weapon)
  return weapons_list

def get_all_weapon_names_list():
  weapon_collection = get_weapon_collection()
  weapons = weapon_collection.find({})
  weapons_list = []
  for weapon in weapons:
    weapons_list.append(weapon["URL_name"])
  return weapons_list

def get_all_characters_list():
  character_collection = get_character_collection()
  characters = character_collection.find({})
  characters_list = []
  for character in characters:
    characters_list.append(character)
  return characters_list

def get_all_character_names_list():
  character_collection = get_character_collection()
  characters = character_collection.find({})
  characters_list = []
  for character in characters:
    characters_list.append(character["URL_name"])
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

def get_jackpot_primo():
  gambling_collection = get_gambling_collection()
  jackpots = gambling_collection.find_one({})
  return jackpots["jackpot_primo"]

def get_jackpot_mora():
  gambling_collection = get_gambling_collection()
  jackpots = gambling_collection.find_one({})
  return jackpots["jackpot_mora"]

def get_leaderboards():
  leaderboards_collection = get_leaderboards_collection()
  leaderboard = leaderboards_collection.find_one({})
  return leaderboard["top_10"]

###UPDATING###
def update_last_resin_time(time):
  time_collection = get_time_collection()
  time_collection.update_one({}, {"$set":{"last_resin_time": time}})

def add_to_jackpot_primo(amnt):
  gambling_collection = get_gambling_collection()
  gambling_collection.update_one({}, {"$inc":{"jackpot_primo": amnt}})

def add_to_jackpot_mora(amnt):
  gambling_collection = get_gambling_collection()
  gambling_collection.update_one({}, {"$inc":{"jackpot_mora": amnt}})

def reset_jackpot_mora():
  gambling_collection = get_gambling_collection()
  gambling_collection.update_one({}, {"$set":{"jackpot_mora": 10000000}})

def reset_jackpot_primo():
  gambling_collection = get_gambling_collection()
  gambling_collection.update_one({}, {"$set":{"jackpot_primo": 10000}})

def update_leaderboards(top_10_dicts):
  leaderboards_collection = get_leaderboards_collection()
  leaderboards_collection.update_one({}, {"$set":{"top_10": top_10_dicts}})