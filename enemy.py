import database_mongo

class Enemy():
  def __init__(self, name, URL_name, URL_icon, description, attack, health, defense, crit_rate, crit_dmg, element_mastery, preference, level, element, _type, drops):
    self.name = str(name)
    self.URL_name = str(URL_name)
    self.URL_icon = str(URL_icon)
    self.description = str(description)
    self.attack = int(attack)
    self.health = int(health)
    self.defense = int(defense)
    self.crit_rate = int(crit_rate)
    self.crit_dmg = int(crit_dmg)
    self.element_mastery = int(element_mastery)
    self.preference = str(preference)
    self.level = int(level)
    self.element = str(element)
    self._type = str(_type)
    self.drops = drops
  def copy(self):
    return Enemy(self.name, self.URL_name, self.URL_icon, self.description, self.attack, self.health, self.defense, self.crit_rate, self.crit_dmg, self.element_mastery, self.preference, self.level, self.element, self._type, self.drops)

  def get_dict(self):
    return self.__dict__

def get_enemy(name):
  e = database_mongo.get_enemy_dict(name)
  return Enemy(e["name"], e["URL_name"], e["URL_icon"], e["description"], e["attack"], e["health"], e["defense"], e["crit_rate"], e["crit_dmg"], e["element_mastery"], e["preference"], e["level"], e["element"],  e["_type"], e["drops"])

def dict_to_enemy(enemyDict):
  e = enemyDict
  return Enemy(e["name"], e["URL_name"], e["URL_icon"], e["description"], e["attack"], e["health"], e["defense"], e["crit_rate"], e["crit_dmg"], e["element_mastery"], e["preference"], e["level"], e["element"],  e["_type"], e["drops"])

def get_all_enemies():
  allEnemies = []
  allEnemyDicts = database_mongo.get_all_enemies_list()
  for e in allEnemyDicts():
    allEnemies.append(dict_to_enemy(e))
  return allEnemies