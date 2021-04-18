import discord
import formatter
import prefix
import character
import weapon
import random
import error
import adventure
import pytz
from replit import db
from datetime import datetime, timedelta

tz = pytz.timezone("America/New_York")

class User:
  name = ""
  ID = ""
  nickname = ""
  description = ""
  favoriteChar = ""
  AR = 1
  XP = 0
  WL = 0
  resin = 0
  pity = 0
  lastFour = 0
  characters = {}
  weapons = {}
  artifacts = {}
  mora = 0
  primogems = 0
  starGlitter = 0
  starDust = 0
  condensed = 0
  lastDaily = ""
  lastWeekly = ""
  Commissions = {}

  def __init__(self, name, ID, nickname, description, favoriteChar, AR, XP, WL, resin, pity, lastFour, characters, weapons, artifacts, mora, primogems, starGlitter, starDust, condensed, lastDaily, lastWeekly, bag, gear, Commissions):
    self.name = str(name)
    self.ID = str(ID)
    self.nickname = str(nickname)
    self.description = str(description)
    self.favoriteChar = str(favoriteChar)
    self.AR = int(AR)
    self.XP = int(XP)
    self.WL = int(WL)
    self.resin = int(resin)
    self.pity = int(pity)
    self.lastFour = int(lastFour)
    self.characters = characters
    self.weapons = weapons
    self.artifacts = artifacts
    self.mora = int(mora)
    self.primogems = int(primogems)
    self.starGlitter = int(starGlitter)
    self.starDust = int(starDust)
    self.condensed = condensed
    self.lastDaily = lastDaily
    self.lastWeekly = lastWeekly
    self.bag = bag
    self.gear = gear
    self.Commissions = Commissions

  def saveSelf(self):
    saveUser(self)

  def canDaily(self):
    utc_now = pytz.utc.localize(datetime.utcnow())
    now = utc_now.astimezone(tz)
    if self.lastDaily == "":
      return True, "Now"
    old = tz.localize(formatter.getDateTime(self.lastDaily), is_dst=None)
    difference = now-old
    if difference.days >= 1:
      return True, "Now"
    else:
      differenceDate = old + timedelta(days=1)
      difference = differenceDate-now
      minutes, seconds = divmod(difference.seconds, 60)
      hours, minutes = divmod(minutes, 60)
      return False, f"{hours}H:{minutes}M:{seconds}S"

  def updateDaily(self):
    utc_now = pytz.utc.localize(datetime.utcnow())
    now = utc_now.astimezone(tz)
    self.lastDaily = f"{now.year}/{now.month}/{now.day}/{now.hour}/{now.minute}/{now.second}"

  def updateWeekly(self):
    utc_now = pytz.utc.localize(datetime.utcnow())
    now = utc_now.astimezone(tz)
    self.lastWeekly = f"{now.year}/{now.month}/{now.day}/{now.hour}/{now.minute}/{now.second}"

  def canWeekly(self):
    utc_now = pytz.utc.localize(datetime.utcnow())
    now = utc_now.astimezone(tz)
    if self.lastWeekly == "":
      return True, "Now"
    old = tz.localize(formatter.getDateTime(self.lastWeekly), is_dst=None)
    difference = now-old
    if difference.days >= 7:
      return True, "Now"
    else:
      differenceDate = old + timedelta(days=7)
      difference = differenceDate-now
      minutes, seconds = divmod(difference.seconds, 60)
      hours, minutes = divmod(minutes, 60)
      return False, f"{difference.days}D:{hours}H:{minutes}M:{seconds}S"
  
  def rechargeResin(self):
    if self.resin < self.getResinCap():
      if self.resin + self.getResinRecharge() > self.getResinCap():
        self.resin = self.getResinCap()
      else:
        self.resin += self.getResinRecharge()

  def useCondensed(self):
    if self.condensed > 0:
      self.condensed -= 1
      self.resin += 40
      saveUser(self)
      return True
    else:
      return False

  def condenseResin(self, amnt):
    amntMade = 0
    reason = ""
    for i in range(amnt):
      if self.resin >= 40:
        if self.condensed < 10:
          self.condensed += 1
          self.resin -= 40
          saveUser(self)
          amntMade += 1
        else:
          reason = "t" #for too many
          break
      else:
        reason = "n" #for not enough
        break
    return amntMade, reason

  def getMaxXP(self):
    return int((30 + (10*(self.AR-1)*(10**self.WL))))
  
  def getResinCap(self):
    return int(120 + (20 * self.WL))

  def getResinRecharge(self):
    return int(20 + (5 * self.WL))

  async def addXP(self, xp, ctx):
    maxXP = self.getMaxXP()
    if xp + self.XP >= maxXP:
      xpLeftOver = int(-1*(maxXP - self.XP - xp))
      await self.levelUp(ctx)
      await self.addXP(xpLeftOver, ctx)
    else:
      self.XP += int(xp)

  def giveMora(self, u, amnt):
    if self.mora < amnt:
      return 0, False
    u.mora += amnt
    self.mora -= amnt
    saveUser(u)
    saveUser(self)
    return amnt, True

  def givePrimo(self, u, amnt):
    if self.primogems < amnt:
      return 0, False
    u.primogems += amnt
    self.primogems -= amnt
    saveUser(u)
    saveUser(self)
    return amnt, True

  def rob(self, u):
    if u.mora < 1:
      return 0, False
    robbed = random.randint(1, u.mora)
    u.mora -= robbed
    self.mora += robbed
    saveUser(u)
    saveUser(self)
    return robbed, True

  async def levelUp(self, ctx):
    self.AR += 1
    await embedAdventureRankUp(ctx, self)
    if self.AR % 10 == 0:
      self.WL += 1
      await embedWorldLevelUp(ctx, self)
    self.XP = 0

  def getChar(self, charName):
    c = character.getCharFromDict(self.characters, formatter.nameUnformatter(charName))
    return c
      
  def equipWeapon(self, charName, weapName):
    if not self.doesCharExist(charName):
      return False, "c"
    if not self.doesWeapExist(weapName):
      return False, "w"
    c = character.getCharFromDict(self.characters, charName)
    w = weapon.getWeapFromDict(self.weapons, weapName)
    if c.weaponType.upper() != w.weaponType.upper():
      return False, "i"
    c.equipWeap(w)
    self.saveChar(c)
    saveUser(self)
    return True, "g"

  def saveChar(self, c):
    if c.urlName in self.characters.keys():
      self.characters[c.urlName] = c.getDict()

  def updateEquippedWeaps(self):
    for w in self.weapons.keys():
      for c in self.characters.keys():
        if len(self.characters[c]["w"]) >= 1:
          if self.characters[c]["w"][0]["urlName"] == w:
            self.characters[c]["w"][0] = self.weapons[w]
            break

  def changeNickname(self, nickname):
    self.nickname = nickname
    saveUser(self)
    
  def changeDescription(self, description):
    self.description = description
    saveUser(self)

  def changeFavoriteChar(self, name):
    if formatter.nameUnformatter(name) in self.characters.keys():
      self.favoriteChar = formatter.nameFormatter(formatter.nameUnformatter(name))
      saveUser(self)
      return True
    elif name.lower() == "none":
      self.favoriteChar = "None"
      saveUser(self)
      return True
    else:
      return False

  def doesCharExist(self, charName):
    if formatter.nameUnformatter(charName) in self.characters.keys():
      return True
    else:
      return False

  def doesWeapExist(self, weapName):
    if formatter.nameUnformatter(weapName) in self.weapons.keys():
      return True
    else:
      return False

  def addChar(self, char):
    if char.urlName in self.characters.keys():
      if self.characters[char.urlName]["unlockedC"] < 6:
        self.characters[char.urlName]["unlockedC"] += 1
        if self.characters[char.urlName]["rarity"] == 5:
          self.starGlitter += 5
        else:
          self.starGlitter += 3
      else:
        if self.characters[char.urlName]["rarity"] == 5:
          self.starGlitter += 10
        else:
          self.starGlitter += 5
    else:
      self.characters[char.urlName] = char.getDict()
    self.characters[char.urlName]["totalGot"] += 1
      
  def addWeap(self, weap):
    if weap.urlName in self.weapons.keys():
      if self.weapons[weap.urlName]["refinement"] < 5:
        self.weapons[weap.urlName]["refinement"] += 1
        if self.weapons[weap.urlName]["rarity"] == 5:
          self.starGlitter += 5
        else:
          self.starDust += 10
      else:
        if self.weapons[weap.urlName]["rarity"] == 5:
          self.starGlitter += 10
        else:
          self.starDust += 20
    else:
      self.weapons[weap.urlName] = weap.getDict()
    self.weapons[weap.urlName]["totalGot"] += 1

  def getDict(self):
    return self.__dict__

def doesExist(ID):
  if ID in db["User"].keys():
    return True
  else:
    return False

def deleteUser(ID):
    if ID in db["User"].keys():
      del db["User"][ID]

def saveUser(user):
  if user.ID in db["User"].keys():
    db["User"][user.ID] = user.getDict()
      
def getUser(ID):
  if ID in db["User"].keys():
    u = db["User"][ID]
    return User(u["name"], u["ID"], u["nickname"], u["description"], u["favoriteChar"], u["AR"], u["XP"], u["WL"], u["resin"], u["pity"], u["lastFour"], u["characters"], u["weapons"], u["artifacts"], u["mora"], u["primogems"], u["starGlitter"], u["starDust"], u["condensed"], u["lastDaily"], u["lastWeekly"], u["bag"], u["gear"], u["Commissions"])

def createUser(name, ID):
  newU = User(name, ID, name, "", "none", 1, 0, 0, 240, 0, 0, {}, {}, {}, 50000, 8000, 0, 0, 0, "", "", {}, {}, adventure.makeUserCommissions())
  if "User" not in db.keys():
    db["User"] = {}
  if ID not in db["User"].keys():
    db["User"][ID] = newU.getDict()

def embedBal(u):
  embed = discord.Embed(title=f"{u.nickname}\'s Balance", color=discord.Color.dark_orange())
  embed.add_field(name="Primogems", value=formatter.numberFormat(u.primogems))
  embed.add_field(name="Mora", value=formatter.numberFormat(u.mora))
  embed.add_field(name="Star Glitter", value=formatter.numberFormat(u.starGlitter))
  embed.add_field(name="Star Dust", value=formatter.numberFormat(u.starDust))
  f = discord.File("Images/Other/Balance.png", "Balance.png")
  embed.set_thumbnail(url="attachment://Balance.png")
  return embed, f

def embedResin(u):
  embed = discord.Embed(title=f"{u.nickname}\'s Resin", color=discord.Color.blue())
  embed.add_field(name="_ _", value=f"**{formatter.numberFormat(u.resin)}/{formatter.numberFormat(u.getResinCap())}**\nCondensed: {formatter.numberFormat(u.condensed)}")
  f = discord.File("Images/Other/Resin.png", "Resin.png")
  embed.set_thumbnail(url="attachment://Resin.png")
  return embed, f

def embedProfile(u):
  embed = discord.Embed(title=f"{u.nickname}\'s Profile", color=discord.Color.dark_gold(), description=u.description)
  embed.add_field(name="Favorite Character", value=f"{u.favoriteChar}", inline=False)
  embed.add_field(name="Adventure Rank", value=f"{formatter.numberFormat(u.AR)}", inline=True)
  embed.add_field(name="World Level", value=f"{formatter.numberFormat(u.WL)}", inline=True)
  embed.add_field(name="Current XP:", value=f"{formatter.numberFormat(u.XP)}/{formatter.numberFormat(u.getMaxXP())}", inline=False)
  embed.add_field(name="Pity:", value=f"5:star: | **{u.pity}/90**\n4:star: | **{u.lastFour}/10**", inline=False)
  embed.add_field(name="Currency:", value=f"Primogems: {formatter.numberFormat(u.primogems)}\nMora: {formatter.numberFormat(u.mora)}\nStar Glitter: {formatter.numberFormat(u.starGlitter)}\nStar Dust: {formatter.numberFormat(u.starDust)}", inline=True)
  embed.add_field(name="Resin", value = f"{formatter.numberFormat(u.resin)}/{formatter.numberFormat(u.getResinCap())}\nCondensed: {formatter.numberFormat(u.condensed)}")
  text = ""
  for comID in u.Commissions.keys():
    commissionName = u.Commissions[comID]["commission"]["title"]
    if u.Commissions[comID]["commission"]["completed"]:
      text += f"~~{commissionName}~~ - **Completed**\n"
    else:
      text += f"{commissionName}\n"
  embed.add_field(name="Commissions", value = text, inline=False)
  can, dailyString = u.canDaily()
  can, weeklyString = u.canWeekly()
  embed.add_field(name="Recharge Times", value=f"Daily: {dailyString}\nWeekly: {weeklyString}", inline=False)

  return embed

def embedCharList(u, pg):
  allChars = formatter.organizeByRarity(u.characters)
  charlist = []
  text = ""
  for i in range(len(allChars)):
    char = allChars[i]
    if char["rarity"] == 5:
      text += prefix.fiveStarPrefix
    else:
      text += prefix.fourStarPrefix
    text += "{n} **C{con}** x{c}\n".format(n = char["name"], con=char["unlockedC"] ,c = char["totalGot"])
    if i % 10 == 0 and i != 0:
      charlist.append(text)
      text = ""
  if(len(charlist) == 0 and text == ""):
    text = "none\n"
  if(text != ""):
    charlist.append(text)
  embed = discord.Embed(title=f"{u.nickname}\'s Characters", color=discord.Color.dark_teal())
  if(pg > len(charlist) or pg < 1):
    pg = 1  
  embed.add_field(name="_ _", value=f"{charlist[pg-1]}")
  embed.set_footer(text=f"Page {pg}/{len(charlist)}")
  return embed

def embedWeapList(u, pg):
  allWeaps = formatter.organizeByRarity(u.weapons)
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
    text += "{n} **R{r}** x{c}\n".format(n = weap["name"], r=weap["refinement"] ,c = weap["totalGot"])
    if i % 10 == 0 and i != 0:
      weaplist.append(text)
      text = ""
  if(len(weaplist) == 0 and text == ""):
    text = "none\n"
  if(text != ""):
    weaplist.append(text)
  embed = discord.Embed(title=f"{u.nickname}\'s Weapons", color=discord.Color.dark_teal())
  if(pg > len(weaplist) or pg < 1):
    pg = 1
  embed.add_field(name="_ _", value=f"{weaplist[pg-1]}")
  embed.set_footer(text=f"Page {pg}/{len(weaplist)}")
  return embed

#Shows gift of primo to user
def embedGivePrimo(u, primo):
  embed = discord.Embed(title=f"{u.nickname}\'s Gift", color=discord.Color.blurple())
  u.primogems += primo
  embed.add_field(name = f"Primogems x{primo}", value = "_ _")
  f = discord.File("Images/Other/Primogem.png", "Primogem.png")
  embed.set_thumbnail(url="attachment://Primogem.png")
  saveUser(u)
  return embed, f

#Shows donation of primo to user
def embedDonatePrimo(giver, u, primo):
  embed = discord.Embed(title=f"{u.nickname}\'s Gift from {giver.nickname}", color=discord.Color.blurple())
  amnt, given = giver.givePrimo(u, primo)
  if given:
    embed.add_field(name = f"Primogems x{primo}", value = "_ _")
  else:
    embed = error.embedFailedDonationPrimo()
  return embed
  
#Shows gift of mora to user
def embedGiveMora(u, mora):
  embed = discord.Embed(title=f"{u.nickname}\'s Gift", color=discord.Color.gold())
  u.mora += mora
  embed.add_field(name = f"Mora x{formatter.numberFormat(mora)}", value = "_ _")
  f = discord.File("Images/Other/Mora.png", "Mora.png")
  embed.set_thumbnail(url="attachment://Mora.png")
  saveUser(u)
  return embed, f

#Shows donation of mora to user
def embedDonateMora(giver, u, mora):
  embed = discord.Embed(title=f"{u.nickname}\'s Gift from {giver.nickname}", color=discord.Color.gold())
  amnt, given = giver.giveMora(u, mora)
  if given:
    embed.add_field(name = f"Mora x{formatter.numberFormat(mora)}", value = "_ _")
  else:
    embed = error.embedFailedDonationMora()
  saveUser(u)
  return embed

#Shows user owned character info
def embedShowCharInfo(u, c):
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
  embed.add_field(name="Unique Info", value="**Level:** {l}\n**XP:** {x}/{xm}\n**Constellations Unlocked:** {cu}\n **Total Wished:** {tr}".format(l = formatter.numberFormat(c["level"]), cu = c["unlockedC"], tr = formatter.numberFormat(c["totalGot"]), x = formatter.numberFormat(c["xp"]), xm = formatter.numberFormat(formatter.getXPToNextLevel(c["level"]))))
  if len(c["w"]) == 0:
    text = "None"
  else:
    text = c["w"][0]["name"]
  embed.add_field(name="Equipped Weapon", value=text)

  embed.add_field(name="General Info", value="**Element:** {e}\n**Constellation:** {c}".format(e = c["element"], c = c["constName"]))

  f = discord.File(c["iconURL"], "{}-icon.png".format(c["urlName"]))
  embed.set_thumbnail(url="attachment://{}-icon.png".format(c["urlName"]))

  return embed, f

#Show user owned weapon info
def embedShowWeapInfo(u, w):
  embed = discord.Embed(title = "{un}\'s {cn}".format(un = u.nickname, cn = w["name"]))
  embed.add_field(name="Info", value="**Level:** {l}\n**XP:** {x}/{xm}\n**Refinement:** {cu}\n**Total Wished:** {tr}".format(l = formatter.numberFormat(w["level"]), cu = w["refinement"], tr = formatter.numberFormat(w["totalGot"]), x = formatter.numberFormat(w["xp"]), xm = formatter.numberFormat(formatter.getXPToNextLevel(w["level"]))))

  f = discord.File(w["iconURL"], "{}-icon.png".format(w["urlName"]))
  embed.set_thumbnail(url="attachment://{}-icon.png".format(w["urlName"]))

  return embed, f

async def embedDaily(ctx, u):
  can, timeLeft = u.canDaily()
  embed = discord.Embed(title=f"{u.nickname}\'s Daily Claim")
  if can:
    u.primogems += 800
    u.mora += 10000
    u.condensed += 3
    u.updateDaily()
    embed.add_field(name="Reward", value="**800** Primogems\n**10,000** Mora\n**3** Condensed Resin")
    f = discord.File("Images/Other/Gift.png", "Gift.png")
    embed.set_thumbnail(url="attachment://Gift.png")
    saveUser(u)
    await ctx.send(embed=embed, file=f)
  else:
    embed = error.embedTooEarly(timeLeft)
    await ctx.send(embed=embed)

async def embedWeekly(ctx, u):
  can, timeLeft = u.canWeekly()
  embed = discord.Embed(title=f"{u.nickname}\'s Weekly Claim")
  if can:
    u.primogems += 1600
    u.mora += 500000
    u.condensed += 10
    u.updateWeekly()
    embed.add_field(name="Reward", value="**1,600** Primogems\n**500,000** Mora\n**10** Condensed Resin")
    f = discord.File("Images/Other/Gift.png", "Gift.png")
    embed.set_thumbnail(url="attachment://Gift.png")
    saveUser(u)
    await ctx.send(embed=embed, file=f)
  else:
    embed = error.embedTooEarly(timeLeft)
    await ctx.send(embed=embed)

async def embedCondensed(ctx, u, amnt):
  amntSucc, reason = u.condenseResin(amnt)
  if amntSucc > 0:
    embed = discord.Embed(title="Condensing Resin", color=discord.Color.blue())
    embed.add_field(name="Condensed Successfully Crafted:", value=f"{amntSucc}")
    saveUser(u)
    f = discord.File("Images/Other/Condensed_Resin.png", "Condensed_Resin.png")
    embed.set_thumbnail(url="attachment://Condensed_Resin.png")
    await ctx.send(embed=embed, file=f)
  else:
    if reason == "n":
      embed = error.embedNotEnoughResin()
      await ctx.send(embed=embed)
    else:
      embed = error.embedTooMuchCondensed()
      await ctx.send(embed=embed)

async def embedUseCondensed(ctx, u):
  can = u.useCondensed()
  if can:
    embed = discord.Embed(title="Using Condensed", color=discord.Color.blue())
    embed.add_field(name="Condensed Resin Used", value=f"You now have {u.condensed} remaining.")
    f = discord.File("Images/Other/Condensed_Resin.png", "Condensed_Resin.png")
    embed.set_thumbnail(url="attachment://Condensed_Resin.png")
    await ctx.send(embed=embed, file=f)
  else:
    embed = error.embedNotEnoughCondensed()
    await ctx.send(embed=embed)

def rechargeAllResin():
  for i in db["User"].keys():
    u = getUser(i)
    u.rechargeResin()
    saveUser(u)

async def embedAdventureRankUp(ctx, u):
  embed = discord.Embed(title="Adventure Rank Up", color=discord.Color.green(), description=f"{u.nickname}\'s Adventure Rank has increased to {u.AR}")
  await ctx.send(embed=embed)

async def embedWorldLevelUp(ctx, u):
  embed = discord.Embed(title="World Level Increase", color=discord.Color.green(), description=f"{u.nickname}\'s World Level has increased to {u.WL}\n Your adventuring rewards will increase.")
  await ctx.send(embed=embed)

def clearUserData():
  print("Clearing User Data")
  db["User"] = {}
  print("User Data Cleared")

def resetTimers(i):
  if i in db["User"].keys():
    u = getUser(i)
    u.lastDaily = ""
    u.lastWeekly = ""
    saveUser(u)

def resetDailyCommissions(i):
  if i in db["User"].keys():
    u = getUser(i)
    u.Commissions = {}
    u.Commissions = adventure.makeUserCommissions()
    saveUser(u)

def generateAllUserCommissions():
  for i in db["User"].keys():
    u = getUser(i)
    u.Commissions = {}
    u.Commissions = adventure.makeUserCommissions()
    saveUser(u)