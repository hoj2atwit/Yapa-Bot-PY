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