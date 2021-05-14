class Item:
  def __init__(self, name, URL_name, description, count, rarity, group):
    self.name = name
    self.URL_name = URL_name
    self.description = description
    self.count = count
    self.rarity = rarity
    self.group = group

  def get_dict(self):
    return self.__dict__

def get_item(item_dict):
  return Item(item_dict["name"], item_dict["URL_name"], item_dict["description"], item_dict["count"], item_dict["rarity"], item_dict["group"])