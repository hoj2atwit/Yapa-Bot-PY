import random
import error
import discord
import formatter
from replit import db

class Target:
  name = ""
  total = 0
  amnt = 0 
  def __init__(self, name, total, amnt):
    self.name = name
    self.total = total
    self.amnt = amnt
  def getDict(self):
    return self.__dict__

class Commission:
  commission = {}
  t = "" #T, Q, W, B
  def __init__(self, commission, t):
    self.commission = commission
    self.t = t
  def getDict(self):
    return self.__dict__

class Trivia:
  ID = ""
  title = ""
  question = ""
  answer = ""
  primoReward = 0
  moraReward = 0
  xp = 0
  completed = False
  def __init__(self, ID, title, question, answer, primoReward, moraReward, xp, completed):
    self.ID = ID
    self.title = title
    self.question = question
    self.answer = answer
    self.primoReward = primoReward
    self.moraReward = moraReward
    self.xp = xp
    self.completed = completed

  def getDict(self):
    return self.__dict__

class Quest:
  ID = ""
  title = ""
  desc = ""
  targets = {}
  primoReward = 0
  moraReward = 0
  xp = 0
  completed = False
  def __init__(self, ID, title, desc, targets, primoReward, moraReward, xp, completed):
    self.ID = ID
    self.title = title
    self.desc = desc
    self.targets = targets
    self.primoReward = primoReward
    self.moraReward = moraReward
    self.xp = xp
    self.completed = completed

  def checkDone(self):
    for tKey in self.targets:
      t = dictToTarget(self.targets[tKey])
      if t.amnt < t.total:
        return False
    self.completed = True
    return True

  def getDict(self):
    return self.__dict__

class Wish:
  ID = ""
  title = ""
  desc = ""
  total = 0
  amnt = 0
  primoReward = 0
  moraReward = 0
  xp = 0
  completed = False
  def __init__(self, ID, title, desc, total, amnt, primoReward, moraReward, xp, completed):
    self.ID = ID
    self.title = title
    self.desc = desc
    self.total = total
    self.amnt = amnt
    self.primoReward = primoReward
    self.moraReward = moraReward
    self.xp = xp
    self.completed = completed

  def checkDone(self):
    if self.amnt < self.total:
      return False
    else:
      self.completed = True
      return True

  def getDict(self):
    return self.__dict__

class Buy:
  ID = ""
  title = ""
  desc = ""
  targets = {}
  primoReward = 0
  moraReward = 0
  xp = 0
  completed = False
  def __init__(self, ID, title, desc, targets, amnt, primoReward, moraReward, xp, completed):
    self.ID = ID
    self.title = title
    self.desc = desc
    self.targets = targets
    self.amnt = amnt
    self.primoReward = primoReward
    self.moraReward = moraReward
    self.xp = xp
    self.completed = completed

  def checkDone(self):
    for tKey in self.targets:
      t = dictToTarget(self.targets[tKey])
      if t.amnt < t.total:
        return False
    self.completed = True
    return True
  
  def getDict(self):
    return self.__dict__

def insertCharacterTrivia(triviaDict, startingIndex):
  newTrivDict = triviaDict
  newestIndex = startingIndex
  for name in db["Characters"].keys():
    c = db["Characters"][name]
    triv = Trivia(f"T{newestIndex}", "(T{ni}) Character Quiz - {n}".format(n = c["name"], ni = newestIndex), "What element is {}?".format(c["name"]), "{}".format(c["element"]), 50, 500, 30, False)
    newTrivDict[f"T{newestIndex}"] = triv.getDict()
    newestIndex += 1
    triv = Trivia(f"T{newestIndex}", "(T{ni}) Character Quiz - {n}".format(n = c["name"], ni = newestIndex), "What weapon type does {} use?".format(c["name"]), "{}".format(c["weaponType"]), 50, 500, 30, False)
    newTrivDict[f"T{newestIndex}"] = triv.getDict()
    newestIndex += 1
    triv = Trivia(f"T{newestIndex}", "(T{ni}) Character Quiz - {n}".format(n = c["name"], ni = newestIndex), "What is the name of {}\'s Constellation?".format(c["name"]), "{}".format(c["constName"]), 160, 1000, 50, False)
    newTrivDict[f"T{newestIndex}"] = triv.getDict()
    newestIndex += 1
  return newTrivDict, newestIndex

def listTargets(tarDict):
  tListStr = ""
  for tKey in tarDict.keys():
    t = dictToTarget(tarDict[tKey])
    if t.amnt >= t.total:
      tListStr += f"~~{formatter.nameFormatter(t.name)}   **{t.amnt}/{t.total}**~~\n"
    else:
      tListStr += f"{formatter.nameFormatter(t.name)}   **{t.amnt}/{t.total}**\n"
  return tListStr

def makeWishCommissions(ID, amnt):
  return Wish(ID, f"Wish Upon A Star - W{amnt}", f"Do {amnt} wishes.", amnt, 0, int(160 * amnt), 0, int(20*amnt), False)

def makeAdventureCommission(ID, amnt):
  t = Target("adventure", amnt, 0)
  targets = {"adventure" : t.getDict()}
  return Quest(ID, f"The Adventure Continues - A{amnt}", f"Go on an adventure {amnt} times.", targets, int(60*amnt), int(3000*amnt), int(45*amnt), False)

async def showCommissions(ctx, u):
  embed = discord.Embed(title = f"{u.nickname}\'s Commissions", color=discord.Color.green(),description="Resets everyday at midnight EST.")
  for k in u.Commissions.keys():
    c = u.Commissions[k]
    if c["t"] == "T":
      t = dictToTrivia(c["commission"])
      if t.completed:
        embed.add_field(name=f"{t.title}",value=f"~~{t.question}~~ - **Completed**", inline=False)
      else:
        embed.add_field(name=f"{t.title}",value=f"{t.question}", inline=False)
    elif c["t"] == "Q":
      q = dictToQuest(c["commission"])
      if q.completed:
        embed.add_field(name=f"{q.title}",value=f"~~{q.desc}~~ - **Completed**\n", inline=False)
      else:
        embed.add_field(name=f"{q.title}",value=f"{q.desc}\n{listTargets(q.targets)}", inline=False)
    elif c["t"] == "W":
      w = dictToWish(c["commission"])
      if w.completed:
        embed.add_field(name=f"{w.title}",value=f"~~{w.desc}~~ - **Completed**\n", inline=False)
      else:
        embed.add_field(name=f"{w.title}",value=f"{w.desc}\n**{w.amnt}/{w.total}** Wishes Made", inline=False)
    elif c["t"] == "B":
      b = dictToBuy(c["commission"])
      if b.completed:
        embed.add_field(name=f"{b.title}",value=f"~~{b.desc}~~ - **Completed**\n", inline=False)
      else:
        embed.add_field(name=f"{b.title}",value=f"{b.desc}\n{listTargets(b.targets)}", inline=False)
  f = discord.File("Images/Other/Adventurers_Guild.png", "Adventurers_Guild.png")
  embed.set_thumbnail(url="attachment://Adventurers_Guild.png")
  await ctx.send(embed=embed, file=f)

# commission types:
# Trivia
# Quest
# Wish
# Buy
def generateAllCommissions():
  commissions = {}

  #Trivia
  commissions["Trivia"] = {}
  commissions["Trivia"], contTriviaIndex = insertCharacterTrivia(commissions["Trivia"], 1)

  #Quests
  commissions["Quest"] = {
    "Q1" : makeAdventureCommission("Q1", 3).getDict(),
    "Q2" : makeAdventureCommission("Q2", 5).getDict(),
    "Q3" : makeAdventureCommission("Q3", 10).getDict()
  }

  #Wish
  commissions["Wish"] = {
    "W1" : makeWishCommissions("W1", 10).getDict(), 
    "W2" : makeWishCommissions("W2", 5).getDict(),
    "W3" : makeWishCommissions("W3", 20).getDict(),
    "W4" : makeWishCommissions("W4", 1).getDict()
  }

  #Buy
  commissions["Buy"] = {}
  db["Commissions"] = {}
  db["Commissions"] = commissions

def makeUserCommissions():
  commissions = {}
  count = 0
  while count < 4:
    typeNum = random.randint(1,3)
    if typeNum == 1:
      comDict = db["Commissions"]["Trivia"]
      comID = "T" + str(random.randint(1, len(comDict.keys())))
      com = Commission(comDict[comID], "T")
    elif typeNum == 2:
      comDict = db["Commissions"]["Quest"]
      comID = "Q" + str(random.randint(1, len(comDict.keys())))
      com = Commission(comDict[comID], "Q")
    elif typeNum == 3:
      comDict = db["Commissions"]["Wish"]
      comID = "W" + str(random.randint(1, len(comDict.keys())))
      com = Commission(comDict[comID], "W")
    else:
      comDict = db["Commissions"]["Buy"]
      comID = "B" + str(random.randint(1, len(comDict.keys())))
      com = Commission(comDict[comID], "B")

    if comID in commissions.keys():
      pass
    else:
      commissions[comID] = com.getDict()
      count += 1
  return commissions

async def checkTargetComplete(ctx, u, targetName, amnt):
  coms = u.Commissions
  for comID in coms.keys():
    cont = False
    if coms[comID]["t"] == "Q":
      c = dictToQuest(coms[comID]["commission"])
      cont = True
    elif coms[comID]["t"] == "B":
      c = dictToBuy(coms[comID]["commission"])
      cont = True

    if cont:
      targets = c.targets
      if targetName in targets.keys():
        if not c.completed:
          t = dictToTarget(targets[targetName])
          t.amnt += amnt
          c.targets[targetName] = t.getDict()
          if c.checkDone():
            await completedCommission(ctx, u, c)
          coms[comID]["commission"] = c.getDict()
          u.Commissions = coms
          await allCommissionsCompleted(ctx, u)

async def checkWishComplete(ctx, u, amnt):
  coms = u.Commissions
  for comID in coms.keys():
    if coms[comID]["t"] == "W":
      c = dictToWish(coms[comID]["commission"])
      if not c.completed:
        c.amnt += amnt
        if c.checkDone():
          await completedCommission(ctx, u, c)
        coms[comID]["commission"] = c.getDict()
        u.Commissions = coms
        await allCommissionsCompleted(ctx, u)

async def completedCommission(ctx, u, c):
  e = discord.Embed(title="Commission Complete!", color=discord.Color.blurple(), description=f"{u.nickname} has completed a commission.")
  text = ""
  if c.xp > 0:
    realXP = int(c.xp * (u.WL+1))
    await u.addXP(realXP, ctx)
    text += f"**{realXP}** Adventurer\'s Experience\n"
  if c.moraReward > 0:
    realMora = int(c.moraReward * (u.WL + 1))
    u.mora += realMora
    text += f"**{realMora}x** Mora\n"
  if c.primoReward > 0:
    realPrimo = int(c.primoReward * (u.WL + 1))
    u.primogems += realPrimo
    text += f"**{realPrimo}x** Primogems\n"
  e.add_field(name=f"{c.title} Reward", value=text)
  f = discord.File("Images/Other/Commission.png", "Commission.png")
  e.set_thumbnail(url="attachment://Commission.png")
  u.saveSelf()
  await ctx.send(embed=e, file=f)

async def allCommissionsCompleted(ctx, u):
  coms = u.Commissions
  for cKey in coms.keys():
    if coms[cKey]["t"] == "T":
      com = dictToTrivia(coms[cKey]["commission"])
    elif coms[cKey]["t"] == "Q":
      com = dictToQuest(coms[cKey]["commission"])
    elif coms[cKey]["t"] == "W":
      com = dictToWish(coms[cKey]["commission"])
    elif coms[cKey]["t"] == "B":
      com = dictToBuy(coms[cKey]["commission"])

    if com.completed:
      pass
    else:
      return

  realXP = int(100 * (u.WL + 1))
  await u.addXP(realXP, ctx)
  realPrimo = int(800 * (u.WL + 1))
  u.primogems += realPrimo
  realMora = int(5000 * (u.WL + 1))
  u.mora += realMora
  u.saveSelf()
  e = discord.Embed(title="All Commissions Complete!", color=discord.Color.blurple(), description=f"{u.nickname} has completed all of their daily commissions.")
  text = ""
  text += f"**{realXP}** Adventurer\'s Experience\n"
  text += f"**{realMora}x** Mora\n"
  text += f"**{realPrimo}x** Primogems\n"
  e.add_field(name=f"Daily Commissions Reward", value=text)
  f = discord.File("Images/Other/Commission.png", "Commission.png")
  e.set_thumbnail(url="attachment://Commission.png")
  await ctx.send(embed=e, file=f)

def dictToQuest(d):
  return Quest(d["ID"], d["title"], d["desc"], d["targets"], d["primoReward"], d["moraReward"], d["xp"], d["completed"])

def dictToTrivia(d):
  return Trivia(d["ID"], d["title"], d["question"], d["answer"], d["primoReward"], d["moraReward"], d["xp"], d["completed"])

def dictToWish(d):
  return Wish(d["ID"], d["title"], d["desc"], d["total"], d["amnt"], d["primoReward"], d["moraReward"], d["xp"], d["completed"])

def dictToBuy(d):
  return Buy(d["ID"], d["title"], d["desc"], d["targets"], d["primoReward"], d["moraReward"], d["xp"], d["completed"])

def dictToTarget(d):
  return Target(d["name"], d["total"], d["amnt"])

async def answerTrivia(ctx, u, cid, answer):
  coms = u.Commissions
  if cid in coms.keys():
    if coms[cid]["t"] == "T":
      t = dictToTrivia(coms[cid]["commission"])
      if not t.completed:
        if t.answer.lower() == answer.lower():
          t.completed = True
          await completedCommission(ctx, u, t)
          coms[cid]["commission"] = t.getDict()
          u.Commissions = coms
          u.saveSelf()
          await allCommissionsCompleted(ctx, u)
        else:
          await ctx.send(embed=error.embedWrongAnswer())

#allows adventuring
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
      
  if len(characters) > 0 and len(characters) <= 4:
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
    await checkTargetComplete(ctx, u, "adventure", 1)
    u.saveSelf()
    f = discord.File("Images/Other/Drops.png", "Drops.png")
    e.set_thumbnail(url="attachment://Drops.png")
    await ctx.send(embed=e, file=f)
  elif len(characters) > 4:
    e = error.embedTooManyCharacters()
    await ctx.send(embed=e)

#generateAllCommissions()