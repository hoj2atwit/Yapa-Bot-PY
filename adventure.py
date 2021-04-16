import random
import error
import discord
import user
import character

# comission types:
# Trivia
# Quest
# Wish
# Buy
def generateComissions():
  comissions = {}

  #Trivia
  comissions["Trivia"] = []

  #Quests
  comissions["Quests"] = {

  }

  #Wish
  comissions["Wish"] = {

  }

  #Buy
  comissions["Buy"] = {

  }

class Trivia():
  title = ""
  question = ""
  answer = ""
  primoReward = 0
  moraReward = 0
  xp = 0
  def __init__(self, title, question, answer, primoReward, moraReward, xp):
    self.title = title
    self.question = question
    self.answer = answer
    self.primoReward = primoReward
    self.moraReward = moraReward
    self.xp = xp
  def getDict(self):
    return self.__dict__

class Quests():
  title = ""
  desc = ""
  targets = {}
  primoReward = 0
  moraReward = 0
  xp = 0
  def __init__(self, title, desc, targets, primoReward, moraReward, xp):
    self.title = title
    self.desc = desc
    self.targets = targets
    self.primoReward = primoReward
    self.moraReward = moraReward
    self.xp = xp
  def getDict(self):
    return self.__dict__

class Wish():
  title = ""
  desc = ""
  amnt = 0
  primoReward = 0
  moraReward = 0
  xp = 0

  def __init__(self, title, desc, amnt, primoReward, moraReward, xp):
    self.title = title
    self.desc = desc
    self.amnt = amnt
    self.primoReward = primoReward
    self.moraReward = moraReward
    self.xp = xp
  def getDict(self):
    return self.__dict__

class Buy():
  title = ""
  desc = ""
  t = ""
  amnt = 0
  primoReward = 0
  moraReward = 0
  xp = 0

  def __init__(self, title, desc, t, amnt, primoReward, moraReward, xp):
    self.title = title
    self.desc = desc
    self.t = t
    self.amnt = amnt
    self.primoReward = primoReward
    self.moraReward = moraReward
    self.xp = xp
  def getDict(self):
    return self.__dict__

async def embedAdventure(ctx, u, characterList):
  if u.resin < 20:
    e = error.embedNotEnoughResin()
    await ctx.send(embed=e)
    return
  characters = []

  for c in characterList:
    if u.doesCharExist(c):
      characters.append(u.getChar(c))
    else:
      e = error.embedCharIsNotOwned()
      await ctx.send(embed=e)
      return
      
  if len(characters) > 0 and len(characters) < 4:
    moraReward = int(random.randint(500, 5000)*int(2**u.WL))
    primoReward = int(random.randint(2,6)*10 + (5*u.WL))
    charXPReward = int(random.randint(4,12)*int(2**u.WL))
    userXPReward = int(random.randint(12,30)*int(2**u.WL))
    e = discord.Embed(title=f"{u.nickname}\'s Adventuring Rewards", color=discord.Color.green())
    u.mora += moraReward
    e.add_field(name="Drops", value=f"{moraReward}x Mora", inline=False)
    text = ""
    for c in characters:
      await c.addXP(charXPReward, ctx)
      u.saveChar(c)
      text += f"{c.name} gained **{charXPReward} exp**\n"
    await u.addXP(userXPReward, ctx)
    text += f"{u.nickname} gained **{userXPReward} ARxp**\n"
    e.add_field(name="Experience", value=text, inline=False)
    u.primogems += primoReward
    e.add_field(name="Primogems", value=f"{primoReward}x Primogems", inline=False)
    u.resin -= 20
    u.saveSelf()
    f = discord.File("Images/Other/Commission.png", "Commission.png")
    e.set_thumbnail(url="attachment://Commission.png")
    await ctx.send(embed=e, file=f)
  elif len(characters) > 4:
    e = error.embedTooManyCharacters()
    await ctx.send(embed=e)
