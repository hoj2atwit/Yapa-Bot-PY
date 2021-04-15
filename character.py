import constellation
import json
import requests
import formatter
import math
from replit import db

class Character:
  name = "None"
  urlName = ""
  description = ""
  rarity = 0
  element = ""
  iconURL = ""
  portraitURL = ""
  w = []
  weaponType = ""
  constName = ""
  constellations = {}
  artifacts = {}
  level = 1
  xp = 0
  unlockedC = 0
  totalGot = 0
  attack = 0
  critRate = 0
  critDmg = 0
  elementMastery = 0

  def __init__(self, name, urlName, iconURL, portraitURL, description, rarity, element, w, weaponType,constName, constellations, artifacts, level, xp, unlockedC, totalGot, attack, critRate, critDmg, elementMastery):
    self.name = str(name)
    self.urlName = str(urlName)
    self.iconURL = str(iconURL)
    self.portraitURL = str(portraitURL)
    self.description = str(description)
    self.rarity = int(rarity)
    self.element = str(element)
    self.w = w
    self.weaponType = str(weaponType)
    self.constName = str(constName)
    self.constellations = constellations
    self.artifacts = artifacts
    self.level = int(level)
    self.xp = int(xp)
    self.unlockedC = int(unlockedC)
    self.totalGot = int(totalGot)
    self.attack = int(attack)
    self.critRate = int(critRate)
    self.critDmg = int(critDmg)
    self.elementMastery = int(elementMastery)
    
  def copy(self):
    return Character(self.name, self.urlName, self.iconURL, self.portraitURL, self.description, self.rarity, self.element, self.w, self.weaponType, self.constName, self.constellations, self.artifacts, self.level, self.xp, self.unlockedC, self.totalGot, self.attack, self.critRate, self.critDmg, self.elementMastery)

  def getXPToNextLevel(self):
    return ((30)*(2**(self.level-1)) * (2**int(math.floor(self.level/10))))/2

  def addCopy(self):
    if self.unlockedC != 6:
      self.unlockedC += 1
    self.totalGot += 1
  def getConst(self, index):
    return self.constellations[index]
  def getDict(self):
    return self.__dict__

apiURL = "https://api.genshin.dev/"
charImgURL = "https://github.com/genshindev/api/raw/master/assets/images/characters/{}/portrait"
charIconURL = "https://github.com/genshindev/api/raw/master/assets/images/characters/{}/icon"

def getChar(name):
  if name in db["Characters"].keys():
    c = db["Characters"][name]
    return Character(c["name"], c["urlName"], c["iconURL"], c["portraitURL"], c["description"], c["rarity"], c["element"], c["w"], c["weaponType"], c["constName"], c["constellations"], c["artifacts"], c["level"], c["xp"], c["unlockedC"], c["totalGot"], c["attack"], c["critRate"], c["critDmg"], c["elementMastery"])

def getCharNamesAPI():
    response = requests.get(apiURL + "characters/")
    json_data = json.loads(response.text)
    return json_data

def getAllCharsAPI():
  print("Getting Characters from API")
  allCharNames = getCharNamesAPI()
  allChars = []
  for i in allCharNames:
    print("getting {} data".format(i))
    response = requests.get(apiURL + "characters/" + i)
    json_data = response.json()
    name = formatter.nameFormatter("{}".format(i))
    urlName = "{}".format(i)
    
    iconURL = f"Images/Characters/{urlName}-icon.png"
    portraitURL = f"Images/Characters/{urlName}-portrait.png"

    description = formatter.textFormatter("{}".format(json_data['description']))
    rarity = int("{}".format(json_data['rarity']), base = 10)
    element = formatter.nameFormatter("{}".format(json_data['vision']))
    weaponType = "{}".format(json_data['weapon_type'])
    constName = "{}".format(json_data['constellation'])
    constellations = constellation.getAllConsts(rarity, json_data)
    allChars.append(Character(name, urlName, iconURL, portraitURL, description, rarity, element, [], weaponType, constName, constellations, {}, 1, 0, 0, 0, 6, 1, 50, 20))
    print("finished {} data".format(i))
  print("Finished Getting Characters from API")
  return allChars

def getAllCharImages():
  allCharNames = getCharNamesAPI()
  for i in allCharNames:
    urlName = "{}".format(i)
    url = charIconURL.format(urlName)
    r = requests.get(url)
    with open(f"Images/Characters/{urlName}-icon.png", "wb") as f:
      f.write(r.content)
    url = charImgURL.format(urlName)
    r = requests.get(url)
    with open(f"Images/Characters/{urlName}-portrait.png", "wb") as f:
      f.write(r.content)

def getAllChars():
  allChars = []
  for c in db["Characters"].keys():
    allChars.append(getChar(c))
  return allChars

def updateCharactersDB():
  allChars = getAllCharsAPI()
  if "Characters" not in db.keys():
    db["Characters"] = {}
  for c in allChars:
    db["Characters"][c.urlName] = c.getDict()

def getFiveStarChars():
  allChars = getAllChars()
  chars = []
  for c in allChars:
    if c.rarity == 5:
      chars.append(c)
  return chars

def getFourStarChars():
  allChars = getAllChars()
  chars = []
  for c in allChars:
    if c.rarity == 4:
      chars.append(c)
  return chars

#updateCharactersDB()
#getAllCharImages()