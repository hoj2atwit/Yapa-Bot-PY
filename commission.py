import formatter
import error
import discord
import random
import database_mongo

class Target:
  name = ""
  total = 0
  amnt = 0 
  def __init__(self, name, total, amnt):
    self.name = name
    self.total = total
    self.amnt = amnt
  def get_dict(self):
    return self.__dict__

class Commission:
  commission = {}
  c_id = ""
  t = "" #T, Q, W, B
  def __init__(self, commission, t):
    self.commission = commission
    self.t = t

  def get_dict(self):
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

  def get_dict(self):
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

  def check_done(self):
    for tKey in self.targets:
      t = dict_to_target(self.targets[tKey])
      if t.amnt < t.total:
        return False
    self.completed = True
    return True

  def get_dict(self):
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

  def check_done(self):
    if self.amnt < self.total:
      return False
    else:
      self.completed = True
      return True

  def get_dict(self):
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

  def check_done(self):
    for tKey in self.targets:
      t = dict_to_target(self.targets[tKey])
      if t.amnt < t.total:
        return False
    self.completed = True
    return True
  
  def get_dict(self):
    return self.__dict__

def insert_character_trivia(triviaDict, startingIndex):
  newTrivDict = triviaDict
  newestIndex = startingIndex
  allCharDicts = database_mongo.get_all_characters_list()
  for char in allCharDicts:
    c = char
    triv = Trivia(f"T{newestIndex}", "(T{ni}) Character Quiz - {n}".format(n = c["name"], ni = newestIndex), "What element is {}?".format(c["name"]), "{}".format(c["element"]), 30, 500, 30, False)
    newTrivDict[f"T{newestIndex}"] = triv.get_dict()
    newestIndex += 1
    triv = Trivia(f"T{newestIndex}", "(T{ni}) Character Quiz - {n}".format(n = c["name"], ni = newestIndex), "What weapon type does {} use?".format(c["name"]), "{}".format(c["weapon_type"]), 30, 500, 30, False)
    newTrivDict[f"T{newestIndex}"] = triv.get_dict()
    newestIndex += 1
    triv = Trivia(f"T{newestIndex}", "(T{ni}) Character Quiz - {n}".format(n = c["name"], ni = newestIndex), "What is the name of {}\'s Constellation?".format(c["name"]), "{}".format(c["constellation_name"]), 160, 1000, 50, False)
    newTrivDict[f"T{newestIndex}"] = triv.get_dict()
    newestIndex += 1
  return newTrivDict, newestIndex

def list_targets(tarDict):
  tListStr = ""
  for tKey in tarDict.keys():
    t = dict_to_target(tarDict[tKey])
    if t.amnt >= t.total:
      tListStr += f"~~{formatter.name_unformatter(t.name)}   **{t.amnt}/{t.total}**~~\n"
    else:
      tListStr += f"{formatter.name_unformatter(t.name)}   **{t.amnt}/{t.total}**\n"
  return tListStr

def make_wish_commissions(ID, amnt):
  return Wish(ID, f"Wish Upon A Star - W{amnt}", f"Do {amnt} wishes.", amnt, 0, int(80 * amnt), 0, int(5*amnt), False)

def make_adventure_commission(ID, amnt):
  t = Target("adventure", amnt, 0)
  targets = {"adventure" : t.get_dict()}
  return Quest(ID, f"The Adventure Continues - A{amnt}", f"Go on an adventure {amnt} times.", targets, int(20*amnt), int(500*amnt), int(10*amnt), False)

def make_gamble_commission(ID, amnt):
  t = Target("gamble", amnt, 0)
  targets = {"gamble" : t.get_dict()}
  return Quest(ID, f"The Gambler's Frenzy - G{amnt}", f"Gamble {amnt} times.", targets, int(20*amnt), int(500*amnt), int(10*amnt), False)

async def show_commissions(ctx, u):
  embed = discord.Embed(title = f"{u.nickname}\'s Commissions", color=discord.Color.green(),description="Resets everyday at Midnight and Noon EST.")
  for k in u.commissions.keys():
    c = u.commissions[k]
    if c["t"] == "T":
      t = dict_to_trivia(c["commission"])
      if t.completed:
        embed.add_field(name=f"{t.title}",value=f"~~{t.question}~~ - **Completed**", inline=False)
      else:
        embed.add_field(name=f"{t.title}",value=f"{t.question}", inline=False)
    elif c["t"] == "Q":
      q = dict_to_quest(c["commission"])
      if q.completed:
        embed.add_field(name=f"{q.title}",value=f"~~{q.desc}~~ - **Completed**\n", inline=False)
      else:
        embed.add_field(name=f"{q.title}",value=f"{q.desc}\n{list_targets(q.targets)}", inline=False)
    elif c["t"] == "W":
      w = dict_to_wish(c["commission"])
      if w.completed:
        embed.add_field(name=f"{w.title}",value=f"~~{w.desc}~~ - **Completed**\n", inline=False)
      else:
        embed.add_field(name=f"{w.title}",value=f"{w.desc}\n**{w.amnt}/{w.total}** Wishes Made", inline=False)
    elif c["t"] == "B":
      b = dict_to_buy(c["commission"])
      if b.completed:
        embed.add_field(name=f"{b.title}",value=f"~~{b.desc}~~ - **Completed**\n", inline=False)
      else:
        embed.add_field(name=f"{b.title}",value=f"{b.desc}\n{list_targets(b.targets)}", inline=False)
  embed.set_footer(text="Use ?t [ID] [answer] to answer trivia commissions.")
  f = discord.File("Images/Other/Adventurers_Guild.png", "Adventurers_Guild.png")
  embed.set_thumbnail(url="attachment://Adventurers_Guild.png")
  await ctx.send(embed=embed, file=f)

# commission types:
# Trivia
# Quest
# Wish
# Buy
def generate_all_commissions():
  commissions = {}

  #Trivia
  commissions["Trivia"] = {}
  commissions["Trivia"], contTriviaIndex = insert_character_trivia(commissions["Trivia"], 1)

  #Quests
  commissions["Quest"] = {
    "Q1" : make_adventure_commission("Q1", 3).get_dict(),
    "Q2" : make_adventure_commission("Q2", 5).get_dict(),
    "Q3" : make_adventure_commission("Q3", 10).get_dict(),
    "Q4" : make_gamble_commission("Q4", 3).get_dict(),
    "Q5" : make_gamble_commission("Q5", 5).get_dict(),
    "Q6" : make_gamble_commission("Q6", 10).get_dict()
  }

  #Wish
  commissions["Wish"] = {
    "W1" : make_wish_commissions("W1", 10).get_dict(), 
    "W2" : make_wish_commissions("W2", 5).get_dict(),
    "W3" : make_wish_commissions("W3", 20).get_dict(),
    "W4" : make_wish_commissions("W4", 1).get_dict()
  }

  #Buy
  commissions["Buy"] = {}
  database_mongo.save_commissions(commissions)

def make_user_commissions():
  commissions = {}
  count = 0
  while count < 4:
    typeNum = random.randint(1,3)
    if typeNum == 1:
      comDict = database_mongo.get_commissions_of_type("Trivia")
      comID = "T" + str(random.randint(1, len(comDict.keys())))
      com = Commission(comDict[comID], "T")
    elif typeNum == 2:
      comDict = database_mongo.get_commissions_of_type("Quest")
      comID = "Q" + str(random.randint(1, len(comDict.keys())))
      com = Commission(comDict[comID], "Q")
    elif typeNum == 3:
      comDict = database_mongo.get_commissions_of_type("Wish")
      comID = "W" + str(random.randint(1, len(comDict.keys())))
      com = Commission(comDict[comID], "W")
    else:
      comDict = database_mongo.get_commissions_of_type("Buy")
      comID = "B" + str(random.randint(1, len(comDict.keys())))
      com = Commission(comDict[comID], "B")

    if comID in commissions.keys():
      pass
    else:
      commissions[comID] = com.get_dict()
      count += 1
  return commissions

async def check_target_complete(ctx, u, targetName, amnt):
  coms = u.commissions
  for comID in coms.keys():
    cont = False
    if coms[comID]["t"] == "Q":
      c = dict_to_quest(coms[comID]["commission"])
      cont = True
    elif coms[comID]["t"] == "B":
      c = dict_to_buy(coms[comID]["commission"])
      cont = True

    if cont:
      targets = c.targets
      if targetName in targets.keys():
        if not c.completed:
          t = dict_to_target(targets[targetName])
          t.amnt += amnt
          c.targets[targetName] = t.get_dict()
          if c.check_done():
            await completed_commission(ctx, u, c)
          coms[comID]["commission"] = c.get_dict()
          u.commissions = coms
          await all_commissions_completed(ctx, u)

async def check_wish_complete(ctx, u, amnt):
  coms = u.commissions
  for comID in coms.keys():
    if coms[comID]["t"] == "W":
      c = dict_to_wish(coms[comID]["commission"])
      if not c.completed:
        c.amnt += amnt
        if c.check_done():
          await completed_commission(ctx, u, c)
        coms[comID]["commission"] = c.get_dict()
        u.commissions = coms
        await all_commissions_completed(ctx, u)

async def completed_commission(ctx, u, c):
  e = discord.Embed(title="Commission Complete!", color=discord.Color.blurple(), description=f"{u.nickname} has completed a commission.")
  text = ""
  if c.xp > 0:
    can, timeLeft = u.can_vote()
    realXP = int(c.xp * (u.world_level+1)*(1.5**(not can)))
    await u.add_experience(realXP, ctx)
    text += f"**{formatter.number_format(realXP)}** Adventurer\'s Experience\n"
  if c.moraReward > 0:
    realMora = int(c.moraReward * (u.world_level + 1))
    u.mora += realMora
    text += f"**{formatter.number_format(realMora)}x** Mora\n"
  if c.primoReward > 0:
    realPrimo = int(c.primoReward)
    u.primogems += realPrimo
    text += f"**{formatter.number_format(realPrimo)}x** Primogems\n"
  e.add_field(name=f"{c.title} Reward", value=text)
  f = discord.File("Images/Other/Commission.png", "Commission.png")
  e.set_thumbnail(url="attachment://Commission.png")
  await ctx.send(embed=e, file=f)

async def all_commissions_completed(ctx, u):
  coms = u.commissions
  for cKey in coms.keys():
    if coms[cKey]["t"] == "T":
      com = dict_to_trivia(coms[cKey]["commission"])
    elif coms[cKey]["t"] == "Q":
      com = dict_to_quest(coms[cKey]["commission"])
    elif coms[cKey]["t"] == "W":
      com = dict_to_wish(coms[cKey]["commission"])
    elif coms[cKey]["t"] == "B":
      com = dict_to_buy(coms[cKey]["commission"])

    if com.completed:
      pass
    else:
      return

  can, timeLeft = u.can_vote()
  realXP = int(200 * (u.world_level + 1)*(1.5**(not can)))
  await u.add_experience(realXP, ctx)
  realPrimo = int(800 * (u.world_level + 1))
  u.primogems += realPrimo
  realMora = int(5000 * (u.world_level + 1))
  u.mora += realMora
  e = discord.Embed(title="All Commissions Complete!", color=discord.Color.blurple(), description=f"{u.nickname} has completed all of their commissions.")
  text = ""
  text += f"**{formatter.number_format(realXP)}** Adventurer\'s Experience\n"
  text += f"**{formatter.number_format(realMora)}x** Mora\n"
  text += f"**{formatter.number_format(realPrimo)}x** Primogems\n"
  e.add_field(name=f"Daily Commissions Reward", value=text)
  f = discord.File("Images/Other/Commission.png", "Commission.png")
  e.set_thumbnail(url="attachment://Commission.png")
  await ctx.send(embed=e, file=f)

def dict_to_quest(d):
  return Quest(d["ID"], d["title"], d["desc"], d["targets"], d["primoReward"], d["moraReward"], d["xp"], d["completed"])

def dict_to_trivia(d):
  return Trivia(d["ID"], d["title"], d["question"], d["answer"], d["primoReward"], d["moraReward"], d["xp"], d["completed"])

def dict_to_wish(d):
  return Wish(d["ID"], d["title"], d["desc"], d["total"], d["amnt"], d["primoReward"], d["moraReward"], d["xp"], d["completed"])

def dict_to_buy(d):
  return Buy(d["ID"], d["title"], d["desc"], d["targets"], d["primoReward"], d["moraReward"], d["xp"], d["completed"])

def dict_to_target(d):
  return Target(d["name"], d["total"], d["amnt"])

async def answer_trivia(ctx, u, cid, answer):
  coms = u.commissions
  if cid in coms.keys():
    if coms[cid]["t"] == "T":
      t = dict_to_trivia(coms[cid]["commission"])
      if not t.completed:
        if t.answer.lower() == answer.lower():
          t.completed = True
          await completed_commission(ctx, u, t)
          coms[cid]["commission"] = t.get_dict()
          u.commissions = coms
          await all_commissions_completed(ctx, u)
        else:
          await error.embed_wrong_answer(ctx)