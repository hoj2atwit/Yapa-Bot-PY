import requests
import json
import formatter
import math
from replit import db

class Weapon:
  name = "None"
  urlName = ""
  iconURL = ""
  weaponType = ""
  totalGot = 0
  rarity = 0
  refinement = 1
  attack = 0
  substat = ""
  substatVal = 0
  level = 1
  xp = 0

  def __init__(self, name, urlName, iconURL, weaponType, totalGot, rarity, refinement, attack, substat, substatVal, level, xp):
    self.name = str(name)
    self.urlName = str(urlName)
    self.iconURL = str(iconURL)
    self.weaponType = str(weaponType)
    self.totalGot = int(totalGot)
    self.rarity = int(rarity)
    self.refinement = int(refinement)
    self.attack = int(attack)
    self.substat = str(substat)
    self.substatVal = int(substatVal)
    self.level = int(level)
    self.xp = int(xp)

  def copy(self):
    return Weapon(self.name, self.urlName, self.iconURL, self.weaponType, self.totalGot, self.rarity, self.refinement, self.attack, self.substat, self.substatVal, self.level, self.xp)

  def getXPToNextLevel(self):
    return ((30)*(2**(self.level-1)) * (2**int(math.floor(self.level/10))))/2

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

  def getDict(self):
    return self.__dict__

apiURL = "https://api.genshin.dev/"
weapIconURL = "https://raw.github.com/genshindev/api/master/assets/images/weapons/{}/icon"

def getWeap(name):
  if name in db["Weapons"].keys():
    w = db["Weapons"][name]
    return Weapon(w["name"], w["urlName"], w["iconURL"], w["weaponType"], w["totalGot"], w["rarity"], w["refinement"], w["attack"], w["substat"], w["substatVal"], w["level"], w["xp"])

def getWeapNames():
  response = requests.get(apiURL + "weapons/")
  json_data = json.loads(response.text)
  return json_data

def getAllWeapsAPI():
  allWeapNames = getWeapNames()
  allWeaps = []
  print("Getting Weapons")
  for i in allWeapNames:
    print("Getting {} Data".format(i))
    response = requests.get(apiURL + "weapons/" + i)
    json_data = response.json()

    name = formatter.nameFormatter("{}".format(i))
    urlName = "{}".format(i)

    iconURL = f"Images/Weapons/{urlName}-icon.png"

    rarity = int("{}".format(json_data['rarity']))
    weaponType = "{}".format(json_data['type'])
    attack = int("{}".format(json_data['baseAttack']))
    substat = "{}".format(json_data['subStat'])

    allWeaps.append(Weapon(name, urlName, iconURL, weaponType, 0, rarity, 1, attack, substat, 0, 1, 0))
    print("Finished {} Data".format(i))
  print("Finished Weapons")
  return allWeaps

def getAllWeapImages():
  allWeapNames = getWeapNames()
  for i in allWeapNames:
    urlName = "{}".format(i)
    url = weapIconURL.format(urlName)
    r = requests.get(url)
    with open(f"Images/Weapons/{urlName}-icon.png", "wb") as f:
      f.write(r.content)

def getAllWeaps():
  allWeaps = []
  for w in db["Weapons"].keys():
    allWeaps.append(getWeap(w))
  return allWeaps

def updateWeaponsDB():
  allWeapons = getAllWeapsAPI()
  if "Weapons" not in db.keys():
    db["Weapons"] = {}
  for weapon in allWeapons:
    db["Weapons"][weapon.urlName] = weapon.getDict()

def getFiveStarWeaps():
  allWeaps = getAllWeaps()
  weaps = []
  for w in allWeaps:
    if w.rarity == 5:
      weaps.append(w)
  return weaps

def getFourStarWeaps():
  allWeaps = getAllWeaps()
  weaps = []
  for w in allWeaps:
    if w.rarity == 4:
      weaps.append(w)
  return weaps

def getThreeStarWeaps():
  allWeaps = getAllWeaps()
  weaps = []
  for w in allWeaps:
    if w.rarity == 3:
      weaps.append(w)
  return weaps

def getTwoStarWeaps():
  allWeaps = getAllWeaps()
  weaps = []
  for w in allWeaps:
    if w.rarity == 2:
      weaps.append(w)
  return weaps

def getOneStarWeaps():
  allWeaps = getAllWeaps()
  weaps = []
  for w in allWeaps:
    if w.rarity == 1:
      weaps.append(w)
  return weaps

#updateWeaponsDB()
#getAllWeapImages()