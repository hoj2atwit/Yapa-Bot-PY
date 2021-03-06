
import formatter_custom
import math
import database_mongo
import discord

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
    return int((100 + (3**(int(self.level/10)+1)) * self.level)/2)

  async def add_xp(self, xp, ctx):
    maxXP = self.get_xp_to_next_level()
    xp_extra = int(xp)
    curr_level = self.level
    while xp_extra + self.xp >= maxXP:
      xp_extra = int(-1*(maxXP - self.xp - xp))
      maxXP = self.get_xp_to_next_level()
      self.level_up()
    self.xp += xp_extra
    if curr_level != self.level:
      await embed_level_up_weapon(ctx, self, curr_level)

  def level_up(self):
    self.level += 1
    self.xp = 0

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
  n = formatter_custom.name_formatter(name)
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

async def embed_level_up_weapon(ctx, weap, old_level):
  embed = discord.Embed(title="Weapon Level Up!", color=discord.Color.gold(),description = f"{weap.name} has leveled up! **Lvl {old_level} ??? Lvl {weap.level}**")
  f = discord.File(weap.URL_icon, f"{weap.URL_name}-icon.png")
  embed.set_thumbnail(url=f"attachment://{weap.URL_name}-icon.png")
  await ctx.send(embed=embed, file=f)

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

def does_weap_exist(name):
  real_weap = database_mongo.get_all_weapons_of_criteria("URL_name", formatter_custom.name_formatter(name))
  if real_weap == []:
    return False
  return True