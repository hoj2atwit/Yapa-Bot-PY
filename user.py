import discord
import formatter
import prefix
import character
import weapon
import random
import error
import commission
import pytz
import database_mongo
from datetime import datetime, timedelta

tz = pytz.timezone("America/New_York")

class User:
  def __init__(self, _id, name, nickname, description, favorite_character, adventure_rank, experience, world_level, resin, five_pity, four_pity, characters, weapons, artifacts, mora, primogems, star_glitter, star_dust, condensed, last_daily, last_weekly, bag, gear, commissions, teams):
    self._id = int(_id)
    self.name = str(name)
    self.nickname = str(nickname)
    self.description = str(description)
    self.favorite_character = str(favorite_character)
    self.adventure_rank = int(adventure_rank)
    self.experience = int(experience)
    self.world_level = int(world_level)
    self.resin = int(resin)
    self.five_pity = int(five_pity)
    self.four_pity = int(four_pity)
    self.characters = characters
    self.weapons = weapons
    self.artifacts = artifacts
    self.mora = int(mora)
    self.primogems = int(primogems)
    self.star_glitter = int(star_glitter)
    self.star_dust = int(star_dust)
    self.condensed = int(condensed) 
    self.last_daily = str(last_daily)
    self.last_weekly = str(last_weekly)
    self.bag = bag
    self.gear = gear
    self.commissions = commissions
    self.teams = teams

  def can_daily(self):
    utc_now = pytz.utc.localize(datetime.utcnow())
    now = utc_now.astimezone(tz)
    if self.last_daily == "":
      return True, "Now"
    old = tz.localize(formatter.get_DateTime(self.last_daily), is_dst=None)
    difference = now-old
    if difference.days >= 1:
      return True, "Now"
    else:
      differenceDate = old + timedelta(days=1)
      difference = differenceDate-now
      minutes, seconds = divmod(difference.seconds, 60)
      hours, minutes = divmod(minutes, 60)
      return False, f"{hours}H:{minutes}M:{seconds}S"

  def set_team(self, teamNum, characters):
      for name in characters:
          if not self.does_character_exist(name):
              return False, name
      self.teams[str(teamNum)] = {}
      for i in range(len(characters)):
          self.teams[str(teamNum)][str(i+1)] = formatter.name_unformatter(formatter.name_formatter(characters[i]))
      return True, "None"

  def update_daily(self):
    utc_now = pytz.utc.localize(datetime.utcnow())
    now = utc_now.astimezone(tz)
    self.last_daily = f"{now.year}/{now.month}/{now.day}/{now.hour}/{now.minute}/{now.second}"

  def update_weekly(self):
    utc_now = pytz.utc.localize(datetime.utcnow())
    now = utc_now.astimezone(tz)
    self.last_weekly = f"{now.year}/{now.month}/{now.day}/{now.hour}/{now.minute}/{now.second}"

  def can_weekly(self):
    utc_now = pytz.utc.localize(datetime.utcnow())
    now = utc_now.astimezone(tz)
    if self.last_weekly == "":
      return True, "Now"
    old = tz.localize(formatter.get_DateTime(self.last_weekly), is_dst=None)
    difference = now-old
    if difference.days >= 7:
      return True, "Now"
    else:
      differenceDate = old + timedelta(days=7)
      difference = differenceDate-now
      minutes, seconds = divmod(difference.seconds, 60)
      hours, minutes = divmod(minutes, 60)
      return False, f"{difference.days}D:{hours}H:{minutes}M:{seconds}S"
  
  def recharge_resin(self):
    if self.resin < self.get_resin_cap():
      if self.resin + self.get_resin_recharge() > self.get_resin_cap():
        self.resin = self.get_resin_cap()
      else:
        self.resin += self.get_resin_recharge()

  def use_condensed(self):
    if self.condensed > 0:
      self.condensed -= 1
      self.resin += 40
      return True
    else:
      return False

  def condense_resin(self, amnt):
    amnt_made = 0
    reason = ""
    for i in range(amnt):
      if self.resin >= 40:
        if self.condensed < 10:
          self.condensed += 1
          self.resin -= 40
          amnt_made += 1
        else:
          reason = "t" #for too many
          break
      else:
        reason = "n" #for not enough
        break
    return amnt_made, reason

  def get_max_experience(self):
    return int(30 + (100*(self.adventure_rank-1)*(self.world_level+1)) + (20**int(self.world_level/2)))
  
  def get_resin_cap(self):
    return int(120 + (20 * self.world_level))

  def get_resin_recharge(self):
    return int(20 + (5 * self.world_level))

  async def add_experience(self, xp, ctx):
    maxXP = self.get_max_experience()
    if xp + self.experience >= maxXP:
      xpLeftOver = int(-1*(maxXP - self.experience - xp))
      await self.level_up(ctx)
      await self.add_experience(xpLeftOver, ctx)
    else:
      self.experience += int(xp)

  def give_mora(self, u, amnt):
    if self.mora < amnt:
      return 0, False
    u.mora += amnt
    self.mora -= amnt
    return amnt, True

  def give_primo(self, u, amnt):
    if self.primogems < amnt:
      return 0, False
    u.primogems += amnt
    self.primogems -= amnt
    return amnt, True

  def rob(self, u):
    if u.mora < 5000:
      return 0, False
    robbed = random.randint(1, int(u.mora/2))
    u.mora -= robbed
    self.mora += robbed
    return robbed, True
  
  def reset_level(self):
      self.adventure_rank = 1
      self.world_level = 0
      self.experience = 0

  async def level_up(self, ctx):
    self.adventure_rank += 1
    await embed_adventure_rank_up(ctx, self)
    if self.adventure_rank % 5 == 0:
      self.world_level += 1
      await embed_world_level_up(ctx, self)
    self.experience = 0

  def get_character(self, charName):
    c = character.get_character_from_dict(self.characters, formatter.name_formatter(charName))
    return c
      
  def equip_weapon(self, charName, weapName):
    if not self.does_character_exist(charName):
      return False, "c"
    if not self.does_weapon_exist(weapName):
      return False, "w"
    c = character.get_character_from_dict(self.characters, charName)
    w = weapon.get_weapon_from_dict(self.weapons, weapName)
    if c.weapon_type.upper() != w.weapon_type.upper():
      return False, "i"
    c.equip_weapon(w)
    self.save_character(c)
    return True, "g"

  def save_character(self, c):
    if c.URL_name in self.characters.keys():
      self.characters[c.URL_name] = c.get_dict()

  def update_equiped_weapons(self):
    for w in self.weapons.keys():
      for c in self.characters.keys():
        if len(self.characters[c]["weapon_equiped"]) > 0:
          if self.characters[c]["weapon_equiped"]["URL_name"] == w:
            self.characters[c]["weapon_equiped"] = self.weapons[w]
            break

  def change_nickname(self, nickname):
    self.nickname = nickname
    
  def change_description(self, description):
    self.description = description

  def change_favorite_character(self, name):
    if formatter.name_formatter(name) in self.characters.keys():
      self.favorite_character = formatter.name_unformatter(formatter.name_formatter(name))
      return True
    elif name.lower() == "none":
      self.favorite_character = "None"
      return True
    else:
      return False

  def does_character_exist(self, charName):
    if formatter.name_formatter(charName) in self.characters.keys():
      return True
    else:
      return False

  def does_weapon_exist(self, weapName):
    if formatter.name_formatter(weapName) in self.weapons.keys():
      return True
    else:
      return False

  def add_character(self, char):
    if char.URL_name in self.characters.keys():
      if self.characters[char.URL_name]["const_amnt"] < 6:
        self.characters[char.URL_name]["const_amnt"] += 1
        if self.characters[char.URL_name]["rarity"] == 5:
          self.star_glitter += 5
        else:
          self.star_glitter += 3
      else:
        if self.characters[char.URL_name]["rarity"] == 5:
          self.star_glitter += 10
        else:
          self.star_glitter += 5
    else:
      self.characters[char.URL_name] = char.get_dict()
    self.characters[char.URL_name]["total"] += 1
      
  def add_weapon(self, weap):
    if weap.URL_name in self.weapons.keys():
      if self.weapons[weap.URL_name]["refinement"] < 5:
        self.weapons[weap.URL_name]["refinement"] += 1
        if self.weapons[weap.URL_name]["rarity"] == 5:
          self.star_glitter += 5
        else:
          self.star_dust += 10
      else:
        if self.weapons[weap.URL_name]["rarity"] == 5:
          self.star_glitter += 10
        else:
          self.star_dust += 20
    else:
      self.weapons[weap.URL_name] = weap.get_dict()
    self.weapons[weap.URL_name]["total"] += 1

  def get_dict(self):
    return self.__dict__
      
def get_user(_id):
  u = database_mongo.get_user_dict(_id)
  return User(u["_id"], u["name"], u["nickname"], u["description"], u["favorite_character"], u["adventure_rank"], u["experience"], u["world_level"], u["resin"], u["five_pity"], u["four_pity"], u["characters"], u["weapons"], u["artifacts"], u["mora"], u["primogems"], u["star_glitter"], u["star_dust"], u["condensed"], u["last_daily"], u["last_weekly"], u["bag"], u["gear"], u["commissions"], u["teams"])

def does_exist(_id):
  u = database_mongo.get_user_dict(_id)
  if u == None:
    return False
  else:
    return True

def create_user(name, ID):
  newU = User(ID, name, name, "", "none", 1, 0, 0, 240, 0, 0, {}, {}, {}, 50000, 8000, 0, 0, 0, "", "", {}, {}, commission.make_user_commissions(),{"1":{}, "2":{}, "3":{}, "4":{}})
  database_mongo.save_user(newU)

async def embed_balance(ctx, u):
  embed = discord.Embed(title=f"{u.nickname}\'s Balance", color=discord.Color.dark_orange())
  embed.add_field(name="Primogems", value=formatter.number_format(u.primogems))
  embed.add_field(name="Mora", value=formatter.number_format(u.mora))
  embed.add_field(name="Star Glitter", value=formatter.number_format(u.star_glitter))
  embed.add_field(name="Star Dust", value=formatter.number_format(u.star_dust))
  f = discord.File("Images/Other/Balance.png", "Balance.png")
  embed.set_thumbnail(url="attachment://Balance.png")
  await ctx.send(embed=embed, file=f)

def embed_resin(u):
  embed = discord.Embed(title=f"{u.nickname}\'s Resin", color=discord.Color.blue())
  embed.add_field(name="_ _", value=f"**{formatter.number_format(u.resin)}/{formatter.number_format(u.get_resin_cap())}**\nCondensed: {formatter.number_format(u.condensed)}")
  f = discord.File("Images/Other/Resin.png", "Resin.png")
  embed.set_thumbnail(url="attachment://Resin.png")
  return embed, f

async def embed_profile(ctx, u, member):
  embed = discord.Embed(title=f"{u.nickname}\'s Profile", color=discord.Color.dark_gold(), description=u.description)
  embed.add_field(name="Favorite Character", value=f"{u.favorite_character}", inline=False)
  embed.add_field(name="Adventure Rank", value=f"{formatter.number_format(u.adventure_rank)}", inline=True)
  embed.add_field(name="World Level", value=f"{formatter.number_format(u.world_level)}", inline=True)
  embed.add_field(name="Current XP:", value=f"{formatter.number_format(u.experience)}/{formatter.number_format(u.get_max_experience())}", inline=False)
  embed.add_field(name="Pity:", value=f"5:star: | **{u.five_pity}/90**\n4:star: | **{u.four_pity}/10**", inline=False)
  embed.add_field(name="Currency:", value=f"Primogems: {formatter.number_format(u.primogems)}\nMora: {formatter.number_format(u.mora)}\nStar Glitter: {formatter.number_format(u.star_glitter)}\nStar Dust: {formatter.number_format(u.star_dust)}", inline=True)
  embed.add_field(name="Resin", value = f"{formatter.number_format(u.resin)}/{formatter.number_format(u.get_resin_cap())}\nCondensed: {formatter.number_format(u.condensed)}")
  text = ""
  for comID in u.commissions.keys():
    commissionName = u.commissions[comID]["commission"]["title"]
    if u.commissions[comID]["commission"]["completed"]:
      text += f"~~{commissionName}~~ - **Completed**\n"
    else:
      text += f"{commissionName}\n"
  embed.add_field(name="Commissions", value = text, inline=False)

  can, dailyString = u.can_daily()
  can, weeklyString = u.can_weekly()
  embed.add_field(name="Recharge Times", value=f"Daily: {dailyString}\nWeekly: {weeklyString}", inline=False)

  url = formatter.get_avatar(member)
  embed.set_thumbnail(url=url)

  await ctx.send(embed=embed)

async def embed_char_list(ctx, u, pg, bot):
  allChars = formatter.organize_by_rarity(u.characters)
  charlist = []
  text = ""
  for i in range(len(allChars)):
    char = allChars[i]
    if char["rarity"] == 5:
      text += prefix.fiveStarPrefix
    else:
      text += prefix.fourStarPrefix
    text += "{n} **C{con}** x{c}\n".format(n = char["name"], con=char["const_amnt"] ,c = char["total"])
    if i % 10 == 0 and i != 0:
      charlist.append(text)
      text = ""
  if(len(charlist) == 0 and text == ""):
    text = "none\n"
  if(text != ""):
    charlist.append(text)
  if(pg > len(charlist) or pg < 1):
    pg = 1  
  charListPages = []
  for i in range(len(charlist)):
      embed = discord.Embed(title=f"{u.nickname}\'s Characters", color=discord.Color.dark_teal())
      if i+pg > len(charlist):
          pageNum = i+pg - len(charlist)
      else:
          pageNum = i+pg
      embed.add_field(name="_ _", value=f"{charlist[pageNum-1]}")
      embed.set_footer(text=f"Page {pageNum}/{len(charlist)}")
      charListPages.append(embed)
  await formatter.pages(ctx, bot,  charListPages)

async def embed_weap_list(ctx, u, pg, bot):
  allWeaps = formatter.organize_by_rarity(u.weapons)
  weaplist = []
  text = ""
  for i in range(len(allWeaps)):
    weap = allWeaps[i]
    if weap["rarity"] == 5:
      text += prefix.fiveStarPrefix
    elif weap["rarity"] == 4:
      text += prefix.fourStarPrefix
    elif weap["rarity"] == 3:
      text += prefix.threeStarPrefix
    elif weap["rarity"] == 2:
      text += prefix.twoStarPrefix
    else:
      text += prefix.oneStarPrefix
    text += "{n} **R{r}** x{c}\n".format(n = weap["name"], r=weap["refinement"] ,c = weap["total"])
    if i % 10 == 0 and i != 0:
      weaplist.append(text)
      text = ""
  if(len(weaplist) == 0 and text == ""):
    text = "none\n"
  if(text != ""):
    weaplist.append(text)
  
  if(pg > len(weaplist) or pg < 1):
    pg = 1
  weapListPages = []
  for i in range(len(weaplist)):
      embed = discord.Embed(title=f"{u.nickname}\'s Weapons", color=discord.Color.dark_teal())
      if i+pg > len(weaplist):
          pageNum = i+pg - len(weaplist)
      else:
          pageNum = i+pg
      embed.add_field(name="_ _", value=f"{weaplist[pageNum-1]}")
      embed.set_footer(text=f"Page {pageNum}/{len(weaplist)}")
      weapListPages.append(embed)

  await formatter.pages(ctx, bot,  weapListPages)

#Shows gift of primo to user
async def embed_give_primo(ctx, u, primo, member):
  embed = discord.Embed(title=f"{u.nickname}\'s Gift", color=discord.Color.blurple())
  u.primogems += primo
  embed.add_field(name = f"Primogems x{primo}", value = "_ _")
  f = discord.File("Images/Other/Primogem.png", "Primogem.png")
  embed.set_thumbnail(url="attachment://Primogem.png")
  await ctx.send(member.mention, embed=embed, file=f)

#Shows donation of primo to user
async def embed_donate_primo(ctx, giver, u, primo, member):
  embed = discord.Embed(title=f"{u.nickname}\'s Gift from {giver.nickname}", color=discord.Color.blurple())
  amnt, given = giver.give_primo(u, primo)
  if given:
    embed.add_field(name = f"Primogems x{formatter.number_format(primo)}", value = "_ _")
    f = discord.File("Images/Other/Primogem.png", "Primogem.png")
    embed.set_thumbnail(url="attachment://Primogem.png")
    await ctx.send(member.mention, embed=embed, file=f)
  else:
    await error.embed_failed_donation_primo(ctx)
  
#Shows gift of mora to user
async def embed_give_mora(ctx, u, mora, member):
  embed = discord.Embed(title=f"{u.nickname}\'s Gift", color=discord.Color.gold())
  u.mora += mora
  embed.add_field(name = f"Mora x{formatter.number_format(mora)}", value = "_ _")
  f = discord.File("Images/Other/Mora.png", "Mora.png")
  embed.set_thumbnail(url="attachment://Mora.png")
  await ctx.send(member.mention, embed=embed, file=f)

#Shows donation of mora to user
async def embed_donate_mora(ctx, giver, u, mora, member):
  embed = discord.Embed(title=f"{u.nickname}\'s Gift from {giver.nickname}", color=discord.Color.gold())
  amnt, given = giver.give_mora(u, mora)
  if given:
    embed.add_field(name = f"Mora x{formatter.number_format(mora)}", value = "_ _")
    f = discord.File("Images/Other/Mora.png", "Mora.png")
    embed.set_thumbnail(url="attachment://Mora.png")
    await ctx.send(member.mention, embed=embed, file=f)
  else:
    await error.embed_failed_donation_mora(ctx)

#Shows user owned character info
async def embed_show_char_info(ctx, u, c):
  color = discord.Color.red()
  if c["element"] == "Anemo":
    color = discord.Color.green()
  elif c["element"] == "Dendro":
    color = discord.Color.dark_green()
  elif c["element"] == "Electro":
    color = discord.Color.purple()
  elif c["element"] == "Hydro":
    color = discord.Color.dark_blue()
  elif c["element"] == "Geo":
    color = discord.Color.orange()
  elif c["element"] == "Cryo":
    color = discord.Color.blue()

  embed = discord.Embed(title = "{un}\'s {cn}".format(un = u.nickname, cn = c["name"]), color=color, description=c["description"])
  level = formatter.number_format(c["level"])
  currXP = formatter.number_format(c["xp"])
  maxXP = formatter.number_format(formatter.get_xp_to_next_level(c["level"]))
  embed.add_field(name="Level {l}".format(l = level), value = "**XP:** {x}/{xm}".format(x=currXP, xm=maxXP))
  embed.add_field(name="Amount Info", value="**Constellations Unlocked:** {cu}\n**Total Wished:** {tr}".format(cu = c["const_amnt"], tr = formatter.number_format(c["total"])))
  if len(c["weapon_equiped"]) == 0:
    text = "None"
  else:
    text = c["weapon_equiped"]["name"]
  embed.add_field(name="Equiped Weapon", value=text)
  embed.add_field(name="Trivia Info", value="**Element:** {e}\n**Constellation:** {c}\n**Weapon Type:** {w}".format(e = c["element"], c = c["constellation_name"], w=formatter.name_unformatter(formatter.name_formatter(c["weapon_type"]))))
  f = []
  f.append(discord.File(c["URL_icon"], "{}-icon.png".format(c["URL_name"])))
  f.append(discord.File(c["URL_portrait"], "{}-portrait.png".format(c["URL_name"])))
  embed.set_image(url="attachment://{}-portrait.png".format(c["URL_name"]))
  embed.set_thumbnail(url="attachment://{}-icon.png".format(c["URL_name"]))

  await ctx.send(embed=embed, files=f)

#Show user owned weapon info
async def embed_show_weap_info(ctx, u, w):
  embed = discord.Embed(title = "{un}\'s {cn}".format(un = u.nickname, cn = w["name"]))
  embed.add_field(name="Info", value="**Level:** {l}\n**XP:** {x}/{xm}\n**Refinement:** {cu}\n**Total Wished:** {tr}".format(l = formatter.number_format(w["level"]), cu = w["refinement"], tr = formatter.number_format(w["total"]), x = formatter.number_format(w["xp"]), xm = formatter.number_format(formatter.get_xp_to_next_level(w["level"]))))
  embed.add_field(name="Type", value = "{}".format(w["weapon_type"]))
  f = discord.File(w["URL_icon"], "{}-icon.png".format(w["URL_name"]))
  embed.set_thumbnail(url="attachment://{}-icon.png".format(w["URL_name"]))

  await ctx.send(embed=embed, file=f)

async def embed_daily(ctx, u):
  can, timeLeft = u.can_daily()
  embed = discord.Embed(title=f"{u.nickname}\'s Daily Claim")
  if can:
    u.primogems += 800
    u.mora += 10000
    u.condensed += 3
    u.update_daily()
    embed.add_field(name="Reward", value="**800** Primogems\n**10,000** Mora\n**3** Condensed Resin")
    f = discord.File("Images/Other/Gift.png", "Gift.png")
    embed.set_thumbnail(url="attachment://Gift.png")
    
    await ctx.send(embed=embed, file=f)
  else:
    await error.embed_too_early(ctx, timeLeft)

async def embed_weekly(ctx, u):
  can, timeLeft = u.can_weekly()
  embed = discord.Embed(title=f"{u.nickname}\'s Weekly Claim")
  if can:
    u.primogems += 1600
    u.mora += 500000
    u.condensed += 10
    u.update_weekly()
    embed.add_field(name="Reward", value="**1,600** Primogems\n**500,000** Mora\n**10** Condensed Resin")
    f = discord.File("Images/Other/Gift.png", "Gift.png")
    embed.set_thumbnail(url="attachment://Gift.png")
    await ctx.send(embed=embed, file=f)
  else:
    await error.embed_too_early(ctx, timeLeft)

async def embed_condensed(ctx, u, amnt):
  amntSucc, reason = u.condense_resin(amnt)
  if amntSucc > 0:
    embed = discord.Embed(title="Condensing Resin", color=discord.Color.blue())
    embed.add_field(name="Condensed Successfully Crafted:", value=f"{amntSucc}")
    f = discord.File("Images/Other/Condensed_Resin.png", "Condensed_Resin.png")
    embed.set_thumbnail(url="attachment://Condensed_Resin.png")
    await ctx.send(embed=embed, file=f)
  else:
    if reason == "n":
      await error.embed_not_enough_resin(ctx)
    else:
      await error.embed_too_much_condensed(ctx)

async def embed_use_condensed(ctx, u):
  can = u.use_condensed()
  if can:
    embed = discord.Embed(title="Using Condensed", color=discord.Color.blue())
    embed.add_field(name="Condensed Resin Used", value=f"You now have {u.condensed} remaining.")
    f = discord.File("Images/Other/Condensed_Resin.png", "Condensed_Resin.png")
    embed.set_thumbnail(url="attachment://Condensed_Resin.png")
    await ctx.send(embed=embed, file=f)
  else:
    await error.embed_not_enough_condensed(ctx)

def recharge_all_resin():
  users_ids = database_mongo.get_all_users_list_ids()
  for i in range(len(users_ids)):
    u = get_user(users_ids[i])
    u.recharge_resin()
    database_mongo.save_user(u)

async def embed_adventure_rank_up(ctx, u):
  embed = discord.Embed(title="Adventure Rank Up", color=discord.Color.green(), description=f"{u.nickname}\'s Adventure Rank has increased to {u.adventure_rank}")
  await ctx.send(embed=embed)

async def embed_world_level_up(ctx, u):
  embed = discord.Embed(title="World Level Increase", color=discord.Color.green(), description=f"{u.nickname}\'s World Level has increased to {u.world_level}\n Your adventuring rewards will increase.")
  await ctx.send(embed=embed)

async def embed_show_team(ctx, u, teamNum):
    embed = discord.Embed(title=f"{u.nickname}\'s Team")
    text = ""
    for i in u.teams[str(teamNum)].keys():
        text += f"{i}: {u.teams[str(teamNum)][i]}\n"
    if len(u.teams[str(teamNum)]) < 4:
        for i in range(4-len(u.teams[str(teamNum)])):
            text += f"{len(u.teams[str(teamNum)])+i+1}: None\n"
    embed.add_field(name=f"Team {teamNum}", value=text)
    await ctx.send(embed=embed)

async def embed_show_all_teams(ctx, u):
    embed = discord.Embed(title=f"{u.nickname}\'s Teams")
    for x in range(4):
        realVal = x+1
        text = ""
        length = len(u.teams[str(realVal)])
        for i in u.teams[str(realVal)].keys():
            text += f"{i}: {u.teams[str(realVal)][i]}\n"
        if length < 4:
            difference = 4 - length
            for i in range(difference):
                text += f"{length+i+1}: None\n"
        embed.add_field(name=f"Team {realVal}", value=text, inline=False)
    await ctx.send(embed=embed)

async def embed_set_team(ctx, u, teamNum, charList):
    if formatter.has_identicals(charList):
        await error.embed_dublicate_characters(ctx)
    else:
        set, failedName = u.set_team(teamNum, charList)
        if not set:
            await error.embed_get_character_suggestions(ctx, u, failedName)
        else:
            embed = discord.Embed(title = "Team set Successfull", description=f"Team {teamNum} has successfully been set.")
            await ctx.send(ctx.author.mention, embed=embed)

def reset_timers(_id):
  u = get_user(_id)
  u.last_daily = ""
  u.last_weekly = ""
  database_mongo.save_user(u)

def reset_daily_commissions(_id):
  
  u = get_user(_id)
  u.commissions = {}
  u.commissions = commission.make_user_commissions()
  database_mongo.save_user(u)

def generate_all_user_commissions():
  users_ids = database_mongo.get_all_users_list_ids()
  for i in range(len(users_ids)):
    u = get_user(users_ids[i])
    u.commissions = {}
    u.commissions = commission.make_user_commissions()
    database_mongo.save_user(u)

def update_users():
  users_ids = database_mongo.get_all_users_list_ids()
  for i in range(len(users_ids)):
    u = get_user(users_ids[i])
    database_mongo.save_user(u)