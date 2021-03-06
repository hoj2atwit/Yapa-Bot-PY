import formatter_custom

class Constellation:
  name = ""
  number = 0
  description = ""
  stat = ""
  statVal = 0

  def __init__(self, name, number, description, stat, statVal):
    self.name = name
    self.number = number
    self.description = description
    self.stat = stat
    self.statVal = statVal

  def get_dict(self):
    return self.__dict__

def get_all_constillations(rarity, json_data):
  charMult = 1
  if rarity == 5:
      charMult = 2
  c1 = Constellation(formatter_custom.nameformatter_custom("{}".format(json_data['constellations'][0]['name'])), 1, formatter_custom.textformatter_custom("{}".format(json_data['constellations'][0]['description'])), "A", 3*charMult).get_dict()
  c2 = Constellation(formatter_custom.nameformatter_custom("{}".format(json_data['constellations'][1]['name'])), 2, formatter_custom.textformatter_custom("{}".format(json_data['constellations'][1]['description'])), "A", 9*charMult).get_dict()
  c3 = Constellation(formatter_custom.nameformatter_custom("{}".format(json_data['constellations'][2]['name'])), 3, formatter_custom.textformatter_custom("{}".format(json_data['constellations'][2]['description'])), "CR", 6*charMult).get_dict()
  c4 = Constellation(formatter_custom.nameformatter_custom("{}".format(json_data['constellations'][3]['name'])), 4, formatter_custom.textformatter_custom("{}".format(json_data['constellations'][3]['description'])), "CR", 10*charMult).get_dict()
  c5 = Constellation(formatter_custom.nameformatter_custom("{}".format(json_data['constellations'][4]['name'])), 5, formatter_custom.textformatter_custom("{}".format(json_data['constellations'][4]['description'])), "CD", 50*charMult).get_dict()
  c6 = Constellation(formatter_custom.nameformatter_custom("{}".format(json_data['constellations'][5]['name'])), 6, formatter_custom.textformatter_custom("{}".format(json_data['constellations'][5]['description'])), "CD", 100*charMult).get_dict()
  constellations = {"c1" : c1, "c2" : c2, "c3" : c3, "c4" : c4, "c5" : c5, "c6" : c6}
  return constellations