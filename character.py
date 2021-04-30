import constellation
import formatter
import math
import discord
import database_mongo

class Character:

  def __init__(self, name, URL_name, URL_icon, URL_portrait, description, rarity, element, weapon_equiped, weapon_type, constellation_name, constellations, artifacts_equiped, level, xp, const_amnt, total, attack, crit_rate, crit_dmg, elemental_mastery):
    self.name = name
    self.URL_name = URL_name
    self.URL_icon = URL_icon
    self.URL_portrait = URL_portrait
    self.description = description
    self.rarity = rarity
    self.element = element
    self.weapon_equiped = weapon_equiped
    self.weapon_type = weapon_type
    self.constellation_name = constellation_name
    self.constellations = constellations
    self.artifacts_equiped = artifacts_equiped
    self.level = level
    self.xp = xp
    self.const_amnt = const_amnt
    self.total = total
    self.attack = attack
    self.crit_rate = crit_rate
    self.crit_dmg = crit_dmg
    self.elemental_mastery = elemental_mastery
    
  def copy(self):
    return Character(self.name, self.URL_name, self.URL_icon, self.URL_portrait, self.description, self.rarity, self.element, self.weapon_equiped, self.weapon_type, self.constellation_name, self.constellations, self.artifacts_equiped, self.level, self.xp, self.const_amnt, self.total, self.attack, self.crit_rate, self.crit_dmg, self.elemental_mastery)

  async def add_xp(self, xp, ctx):
    maxXP = self.get_xp_to_next_level()
    if xp + self.xp >= maxXP:
      xpLeftOver = int(-1*(maxXP - self.xp - xp))
      await self.level_up(ctx)
      await self.add_xp(xpLeftOver, ctx)
    else:
      self.xp += int(xp)

  async def level_up(self, ctx):
    self.level += 1
    await embed_level_up_character(ctx, self)
    self.xp = 0

  def equip_weapon(self, weapon):
    if len(self.weapon_equiped) >= 1:
      self.weapon_equiped = weapon.get_dict()
    else:
      self.weapon_equiped = weapon.get_dict()

  def get_xp_to_next_level(self):
    return int((30 + (100*(self.level-1)*(int(self.level/5)+1)) + (20**int(self.level/10)))/2)

  def add_copy(self):
    if self.const_amnt != 6:
      self.const_amnt += 1
    self.total += 1

  def getConst(self, index):
    return self.constellations[index]

  def get_dict(self):
    return self.__dict__

def get_character_from_dict(charsDict, name):
  n = formatter.name_formatter(name)
  c = charsDict[n]
  return Character(c["name"], c["URL_name"], c["URL_icon"], c["URL_portrait"], c["description"], c["rarity"], c["element"], c["weapon_equiped"], c["weapon_type"], c["constellation_name"], c["constellations"], c["artifacts_equiped"], c["level"], c["xp"], c["const_amnt"], c["total"], c["attack"], c["crit_rate"], c["crit_dmg"], c["elemental_mastery"])

def get_character(name):
  c = database_mongo.get_character_dict(name)
  return Character(c["name"], c["URL_name"], c["URL_icon"], c["URL_portrait"], c["description"], c["rarity"], c["element"], c["weapon_equiped"], c["weapon_type"], c["constellation_name"], c["constellations"], c["artifacts_equiped"], c["level"], c["xp"], c["const_amnt"], c["total"], c["attack"], c["crit_rate"], c["crit_dmg"], c["elemental_mastery"])

def dict_to_char(charDict):
  c = charDict
  return Character(c["name"], c["URL_name"], c["URL_icon"], c["URL_portrait"], c["description"], c["rarity"], c["element"], c["weapon_equiped"], c["weapon_type"], c["constellation_name"], c["constellations"], c["artifacts_equiped"], c["level"], c["xp"], c["const_amnt"], c["total"], c["attack"], c["crit_rate"], c["crit_dmg"], c["elemental_mastery"])

def get_all_characters():
  allChars = []
  allCharsDicts = database_mongo.get_all_characters_list()
  for c in allCharsDicts():
    allChars.append(dict_to_char(c))
  return allChars

def get_six_star_characters():
  sixStarChars = database_mongo.get_all_characters_of_criteria("rarity", 6)
  chars = []
  for c in sixStarChars:
    chars.append(dict_to_char(c))
  return chars

def get_five_star_characters():
  fiveStarChars = database_mongo.get_all_characters_of_criteria("rarity", 5)
  chars = []
  for c in fiveStarChars:
    chars.append(dict_to_char(c))
  return chars

def get_four_star_characters():
  fourStarChars = database_mongo.get_all_characters_of_criteria("rarity", 4)
  chars = []
  for c in fourStarChars:
    chars.append(dict_to_char(c))
  return chars

async def embed_level_up_character(ctx, char):
  embed = discord.Embed(title="Character Level Up!", color=discord.Color.gold(),description = f"{char.name} has leveled up to {char.level}")
  f = discord.File(char.URL_icon, f"{char.URL_name}-icon.png")
  embed.set_thumbnail(url=f"attachment://{char.URL_name}-icon.png")
  await ctx.send(embed=embed, file=f)