import json
import requests
from weapon import Weapon, get_weapon, get_weapon_from_dict
from character import Character, get_character, get_character_from_dict
from enemy import Enemy, get_enemy
from user import get_user
import database_mongo
import formatter
import sys
import constellation

apiURL = "https://api.genshin.dev/"


###WEAPONS###

weapURL_icon = "https://raw.github.com/genshindev/api/master/assets/images/weapons/{}/icon"

def get_weapon_names_API():
  print("Getting weapons json")
  response = requests.get(apiURL + "weapons/")
  print("Loading weapons json")
  return json.loads(response.text)

def get_all_weaps_API():
  allWeapNames = get_weapon_names_API()
  allWeaps = []
  for i in allWeapNames:
    URL_name = "{}".format(i)
    weapList = database_mongo.get_all_weapons_of_criteria("URL_name", URL_name)
    if len(weapList) == 0:
      print("Getting {} Data".format(i))
      response = requests.get(apiURL + "weapons/" + i)
      json_data = response.json()

      name = formatter.name_unformatter("{}".format(i))
      URL_icon = f"Images/Weapons/{URL_name}-icon.png"

      rarity = int("{}".format(json_data['rarity']))
      weapon_type = "{}".format(json_data['type'])
      attack = int("{}".format(json_data['baseAttack']))
      substat = "{}".format(json_data['subStat'])

      allWeaps.append(Weapon(name, URL_name, URL_icon, weapon_type, 0, rarity, 1, attack, substat, 0, 1, 0))
      print("Finished {} Data".format(i))
    else:
      allWeaps.append(get_weapon(URL_name))
  print("Finished Weapons")
  return allWeaps

async def get_all_weap_images_API(ctx):
  allWeapNames = database_mongo.get_all_weapon_names_list()
  for i in allWeapNames:
    URL_name = "{}".format(i)
    url = weapURL_icon.format(URL_name)
    r = requests.get(url)
    try:
        with open(f"Images/Weapons/{URL_name}-icon.png", "xb") as f:
            await ctx.send(f"Downloading {URL_name} Icon")
            f.write(r.content)
    except FileExistsError:
        continue

def update_weapons_DB_from_api():
  allWeapons = get_all_weaps_API()
  for weapon in allWeapons:
    database_mongo.save_weapon(weapon)

def update_weapons_DB():
  allWeapons = get_all_weaps_API()
  for weapon in allWeapons:
    database_mongo.save_weapon(weapon)

def update_user_weapons():
  user_ids = database_mongo.get_all_users_list_ids()
  for _id in user_ids:
    u = get_user(_id)
    weaps = u.weapons
    for name in weaps.keys():
      weaps[name] = get_weapon_from_dict(weaps, name).get_dict()
    u.weapons = weaps
    database_mongo.save_user(u)





###CHARACTERS###

charImgURL = "https://github.com/genshindev/api/raw/master/assets/images/characters/{}/portrait"
charIconURL = "https://github.com/genshindev/api/raw/master/assets/images/characters/{}/icon"

def get_character_names_API():
    response = requests.get(apiURL + "characters/")
    return json.loads(response.text)

def get_all_characters_API():
  print("Getting Characters from API")
  allCharNames = get_character_names_API()
  allChars = []
  for i in allCharNames:
    URL_name = "{}".format(i)
    charList = database_mongo.get_all_characters_of_criteria("URL_name", URL_name)
    if len(charList) == 0:
      print("getting {} data".format(i))
      response = requests.get(apiURL + "characters/" + i)
      json_data = response.json()
      name = formatter.name_unformatter("{}".format(i))
  
      iconURL = f"Images/Characters/{URL_name}-icon.png"
      portraitURL = f"Images/Characters/{URL_name}-portrait.png"

      description = formatter.text_formatter("{}".format(json_data['description']))
      rarity = int("{}".format(json_data['rarity']), base = 10)
      element = formatter.name_unformatter("{}".format(json_data['vision']))
      weaponType = "{}".format(json_data['weapon_type'])
      constName = "{}".format(json_data['constellation'])
      constellations = constellation.get_all_constillations(rarity, json_data)
      allChars.append(Character(name, URL_name, iconURL, portraitURL, description, rarity, element, {}, weaponType, constName, constellations, {}, 1, 0, 0, 0, 5, 100, 0, 50, 20))
      print("finished {} data".format(i))
    else:
      allChars.append(get_character(URL_name))
  print("Finished Getting Characters from API")
  return allChars

async def get_all_character_images_API(ctx):
  allCharNames = database_mongo.get_all_character_names_list()
  for i in allCharNames:
    URL_name = "{}".format(i)
    url = charIconURL.format(URL_name)
    r = requests.get(url)
    try:
        with open(f"Images/Characters/{URL_name}-icon.png", "xb") as f:
            await ctx.send(f"Downloading {URL_name} Icon")
            f.write(r.content)
    except FileExistsError:
        continue
    url = charImgURL.format(URL_name)
    r = requests.get(url)
    try:
        with open(f"Images/Characters/{URL_name}-portrait.png", "xb") as f:
            await ctx.send(f"Downloading {URL_name} Portrait")
            f.write(r.content)
    except FileExistsError:
        continue

def update_all_characters_DB():
  allChars = get_all_characters_API()
  for c in allChars:
    database_mongo.save_character(c)

def update_user_characters():
  user_ids = database_mongo.get_all_users_list_ids()
  for _id in user_ids:
    u = get_user(_id)
    chars = u.characters
    for name in chars.keys():
      chars[name] = get_character_from_dict(chars, name).get_dict()
    u.characters = chars
    database_mongo.save_user(u)