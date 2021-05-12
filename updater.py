import json
import requests
from weapon import Weapon
from character import Character
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

async def update_weapons_DB(ctx):
  allWeapons = get_all_weaps_API()
  for weapon in allWeapons:
    await ctx.send(f"Importing {weapon.name} Data")
    database_mongo.save_weapon(weapon)







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
        allChars.append(Character(name, URL_name, iconURL, portraitURL, description, rarity, element, {}, weaponType, constName, constellations, {}, 1, 0, 0, 0, 5, 1, 50, 20))
        print("finished {} data".format(i))
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
            ctx.send(f"Downloading {URL_name} Icon")
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

async def update_all_characters_DB(ctx):
  allChars = get_all_characters_API()
  for c in allChars:
    await ctx.send(f"Importing {c.name} Data")
    database_mongo.save_character(c)