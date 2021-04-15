import json
import discord
import formatter
import prefix
import character
import weapon
from replit import db

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

  def __init__(self, name, ID, nickname, description, favoriteChar, AR, XP, WL, resin, pity, lastFour, characters, weapons, artifacts, mora, primogems, starGlitter, starDust):
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

  def getMaxXP(self):
    return int((30 + 10**(2**(self.AR-1))) * (2**(self.WL)))
  
  def getResinCap(self):
    return 120 + (20 * self.WL)

  def addXP(self, xp):
    maxXP = self.getMaxXP()
    if xp + self.xp >= maxXP:
      xpLeftOver = -1*(maxXP - self.xp - xp)
      self.levelUp()
      self.addXP(xpLeftOver)
    else:
      self.xp += xp

  def levelUp(self):
    self.AR += 1
    if self.AR % 10 == 0:
      self.WL += 1
    self.xp = 0

  def changeNickname(self, nickname):
    self.nickname = nickname
    
  def changeDescription(self, description):
    self.description = description

  def changeFavoriteChar(self, char):
    if char.urlName in self.characters.keys():
        self.favoriteChar = char.name
        return True
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
    return User(u["name"], u["ID"], u["nickname"], u["description"], u["favoriteChar"], u["AR"], u["XP"], u["WL"], u["resin"], u["pity"], u["lastFour"], u["characters"], u["weapons"], u["artifacts"], u["mora"], u["primogems"], u["starGlitter"], u["starDust"])

def createUser(name, ID):
  newU = User(name, ID, name, "", "none", 1, 0, 0, 240, 0, 0, {}, {}, {}, 50000, 1600, 0, 0)
  if "User" not in db.keys():
    db["User"] = {}
  if ID not in db["User"].keys():
    db["User"][ID] = newU.getDict()

def embedBal(u):
  embed = discord.Embed(title=f"{u.nickname}\'s Balance", color=discord.Color.dark_orange())
  embed.add_field(name="Primogems", value=u.primogems)
  embed.add_field(name="Mora", value=u.mora)
  embed.add_field(name="Star Glitter", value=u.starGlitter)
  embed.add_field(name="Star Dust", value=u.starDust)
  f = discord.File("Images/Other/Balance.png", "Balance.png")
  embed.set_thumbnail(url="attachment://Balance.png")
  return embed, f

def embedResin(u):
  embed = discord.Embed(title=f"{u.nickname}\'s Resin", color=discord.Color.blue())
  embed.add_field(name="_ _", value=f"**{u.resin}/{u.getResinCap()}**")
  f = discord.File("Images/Other/Resin.png", "Resin.png")
  embed.set_thumbnail(url="attachment://Resin.png")
  return embed, f

def embedProfile(u):
  embed = discord.Embed(title=f"{u.nickname}\'s Profile", color=discord.Color.dark_gold(), description=u.description)
  embed.add_field(name="Favorite Character", value=f"{u.favoriteChar}", inline=False)
  embed.add_field(name="Adventure Rank", value=f"{u.AR}", inline=True)
  embed.add_field(name="World Level", value=f"{u.WL}", inline=True)
  embed.add_field(name="Current XP:", value=f"{u.XP}/{u.getMaxXP()}", inline=False)
  embed.add_field(name="Pity:", value=f"{u.pity}/90\n{u.lastFour}/10", inline=False)
  embed.add_field(name="Currency:", value=f"Primogems: {u.primogems}\nMora: {u.mora}\nStar Glitter: {u.starGlitter}\nStar Dust: {u.starDust}", inline=True)
  embed.add_field(name="Resin", value = f"{u.resin}/{u.getResinCap()}")
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
    else:
      text += prefix.fourStarPrefix
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
  
#Shows gift of mora to user
def embedGiveMora(u, mora):
  embed = discord.Embed(title=f"{u.nickname}\'s Gift", color=discord.Color.gold())
  u.mora += mora
  embed.add_field(name = f"Mora x{mora}", value = "_ _")
  f = discord.File("Images/Other/Mora.png", "Mora.png")
  embed.set_thumbnail(url="attachment://Mora.png")
  saveUser(u)
  return embed, f

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

  embed = discord.Embed(title = "{un}\'s {cn}".format(un = u.name, cn = c["name"]), color=color, description=c["description"])
  embed.add_field(name="Unique Info", value="**Level:** {l}\n**XP:** {x}/{xm}\n**Constellations Unlocked:** {cu}\n **Total Wished:** {tr}".format(l = c["level"], cu = c["unlockedC"], tr = c["totalGot"], x = c["xp"], xm = formatter.getXPToNextLevel(c["level"])))
  if len(c["w"]) == 0:
    text = "None"
  else:
    text = c["w"]["name"]
  embed.add_field(name="Equipped Weapon", value=text)

  embed.add_field(name="General Info", value="**Element:** {e}\n**Constellation:** {c}".format(e = c["element"], c = c["constName"]))

  f = discord.File(c["iconURL"], "{}-icon.png".format(c["urlName"]))
  embed.set_thumbnail(url="attachment://{}-icon.png".format(c["urlName"]))

  return embed, f

#Show user owned weapon info
def embedShowWeapInfo(u, w):
  embed = discord.Embed(title = "{un}\'s {cn}".format(un = u.name, cn = w["name"]))
  embed.add_field(name="Info", value="**Level:** {l}\n**XP:** {x}/{xm}\n**Refinement:** {cu}\n**Total Wished:** {tr}".format(l = w["level"], cu = w["refinement"], tr = w["totalGot"], x = w["xp"], xm = formatter.getXPToNextLevel(w["level"])))

  f = discord.File(w["iconURL"], "{}-icon.png".format(w["urlName"]))
  embed.set_thumbnail(url="attachment://{}-icon.png".format(w["urlName"]))

  return embed, f

def clearUserData():
  print("Clearing User Data")
  db["User"] = {}
  print("User Data Cleared")

#clearUserData()