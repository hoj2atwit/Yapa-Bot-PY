import formatter
import math
import database_mongo

class Weapon:
  def __init__(self, name, URL_name, URL_icon, weapon_type, total, rarity, refinement, attack, substat, substat_value, level, xp):
    self.name = name
    self.URL_name = URL_name
    self.URL_icon = URL_icon
    self.weapon_type = weapon_type
    self.total = total
    self.rarity = rarity
    self.refinement = refinement
    self.attack = attack
    self.substat = substat
    self.substat_value = substat_value
    self.level = level
    self.xp = xp

  def copy(self):
    return Weapon(self.name, self.URL_name, self.URL_icon, self.weapon_type, self.total, self.rarity, self.refinement, self.attack, self.substat, self.substat_value, self.level, self.xp)

  def get_xp_to_next_level(self):
    return int((30 + (100*(self.level-1)*(int(self.level/5)+1)) + (20**int(self.level/10)))/2)

  def refine(self, user):
    count = 0
    for i in range(len(user.weapons)):
      if self.name == user.weapons[i].name:
        count += 1
      if count >= 2:
        del user.weapons[i]
        self.refinement += 1
        return True
    return False

  def get_dict(self):
    return self.__dict__

def get_weapon_from_dict(weapDict, name):
  n = formatter.name_formatter(name)
  if n in weapDict.keys():
    w = weapDict[n]
    return Weapon(w["name"], w["URL_name"], w["URL_icon"], w["weapon_type"], w["total"], w["rarity"], w["refinement"], w["attack"], w["substat"], w["substat_value"], w["level"], w["xp"])

def get_weap_list_from_dict_list(dictList):
  weapList = []
  for w in dictList:
    weapList.append(Weapon(w["name"], w["URL_name"], w["URL_icon"], w["weapon_type"], w["total"], w["rarity"], w["refinement"], w["attack"], w["substat"], w["substat_value"], w["level"], w["xp"]))
  return weapList

def get_weapon(name):
  w = database_mongo.get_weapon_dict(name)
  return Weapon(w["name"], w["URL_name"], w["URL_icon"], w["weapon_type"], w["total"], w["rarity"], w["refinement"], w["attack"], w["substat"], w["substat_value"], w["level"], w["xp"])


def get_all_Weapons():
  allWeaps = get_weap_list_from_dict_list(database_mongo.get_all_weapons_list())
  return allWeaps

def get_five_star_weapons():
  return get_weap_list_from_dict_list(database_mongo.get_all_weapons_of_criteria("rarity", 5))

def get_four_star_weapons():
  return get_weap_list_from_dict_list(database_mongo.get_all_weapons_of_criteria("rarity", 4))

def get_three_star_weapons():
  return get_weap_list_from_dict_list(database_mongo.get_all_weapons_of_criteria("rarity", 3))

def get_two_star_weapons():
  return get_weap_list_from_dict_list(database_mongo.get_all_weapons_of_criteria("rarity", 2))

def get_one_star_weapons():
  return get_weap_list_from_dict_list(database_mongo.get_all_weapons_of_criteria("rarity", 1))