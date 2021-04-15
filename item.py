class Item:
  name = ""
  count = 0
  rarity = 0
  def __init__(self, name, count, rarity):
    self.name = name
    self.count = count
    self.rarity = rarity

  def use(self, amount):
    if(amount > self.count):
      return False
    self.count -= amount
    return True

  def copy(self):
    return Item(self.name, self.count.copy(), self.rarity.copy())