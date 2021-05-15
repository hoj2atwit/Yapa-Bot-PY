import discord
import error
import database_mongo
import formatter
import item
import character
import weapon


class Shop:
  def __init__(self, _id, inventory):
    self._id = int(_id)
    self.inventory = inventory
  
  def add_item(self, shop_item):
    if shop_item.item["URL_name"] not in self.inventory.keys():
      self.inventory[shop_item.item["URL_name"]] = shop_item.get_dict()

  def remove_item(self, name):
    if formatter.name_formatter(name) not in self.inventory.keys():
      del self.inventory[formatter.name_formatter(name)]

  async def get_item(self, ctx, name):
    if formatter.name_formatter(name) in self.inventory.keys():
      return get_shop_item(self.inventory[formatter.name_formatter(name)])
    else:
      await error.embed_unknown_item(ctx)
      return None

  def get_dict(self):
    return self.__dict__

class Shop_Item:
  def __init__(self, item, cost, cost_type, amount, max):
    self.item = item
    self.cost = int(cost)
    self.cost_type = str(cost_type)
    self.amount = int(amount)
    self.max = int(max)

  async def buy(self, ctx, u, amount):

    if self.amount == 0:
      await error.embed_out_of_stock(ctx)
      return
    
    if self.amount != -1 and self.amount < amount:
      await error.embed_not_enough_items_to_purchase(ctx, self.item["name"])
      return

    if self.cost_type=="p":
      currency = u.primogems
      e = error.embed_not_enough_primo
    elif self.cost_type=="m":
      currency = u.mora
      e = error.embed_not_enough_mora
    elif self.cost_type=="sd":
      currency = u.star_dust
      e = error.embed_not_enough_star_dust
    elif self.cost_type=="sg":
      currency = u.star_glitter
      e = error.embed_not_enough_star_glitter

    amnt = amount
    if currency < (amnt*self.cost):
      await e(ctx)
      return
    
    currency -= (amnt*self.cost)
    if self.cost_type=="p":
      u.primogems = currency
    elif self.cost_type=="m":
      u.mora = currency
    elif self.cost_type=="sd":
      u.star_dust = currency
    elif self.cost_type=="sg":
      u.star_glitter = currency
    
    my_item = item.get_item(self.item)

    for i in range(amnt):
      if my_item.group == "currency":
        if my_item.URL_name == "primogems":
          u.primogems += my_item.count
        elif my_item.URL_name == "mora":
          u.mora += my_item.count
      elif my_item.group == "character":
        u.add_character(character.get_character(my_item.URL_name))
      elif my_item.group == "weapon":
        u.add_weapon(weapon.get_weapon(my_item.URL_name))
      else:
        u.add_item(my_item)

      if self.amount != -1:
        self.amount -= 1
    
    database_mongo.save_user(u)

    embed = discord.Embed(title="Purchase Successful", description=f"{u.nickname} purchased {formatter.number_format(int(my_item.count * amount))} {my_item.name}.", color=discord.Color.green())
    await ctx.send(embed=embed)

  def get_dict(self):
    return self.__dict__

def get_shop_item(shop_item_dict):
  return Shop_Item(shop_item_dict["item"], shop_item_dict["cost"], shop_item_dict["cost_type"], shop_item_dict["amount"], shop_item_dict["max"])

def get_shop(shop_dict):
  return Shop(shop_dict["_id"], shop_dict["inventory"])

async def shop_buy(ctx, u, name, amount):
  shop = get_shop(database_mongo.get_shop_dict(u._id))
  SI = await shop.get_item(ctx, name)
  if SI != None:
    await SI.buy(ctx, u, amount)
    shop.inventory[SI.item["URL_name"]] = SI
    database_mongo.save_shop(shop)

async def embed_show_shop(ctx, u, _type):
  shop = get_shop(database_mongo.get_shop_dict(u._id))

  primo_text = "None"
  mora_text = "None"
  sg_text = "None"
  sd_text = "None"
  for i in shop.inventory.keys():
    if shop.inventory[i]["amount"] > 0:
      text = "({})".format(shop.inventory[i]["amount"])
    else:
      text = ""
    
    x=formatter.number_format(shop.inventory[i]["item"]["count"])
    y=shop.inventory[i]["item"]["name"]
    z=formatter.number_format(shop.inventory[i]["cost"])
    ct=shop.inventory[i]["cost_type"].upper()
    text += f"{x}x {y} --------- **{z} {ct}**\n"

    if shop.inventory[i]["amount"] == 0:
      text = "~~" + text + "~~ **SOLDOUT**"

    if shop.inventory[i]["cost_type"] == "p":
      if primo_text == "None":
        primo_text = text
      else:
        primo_text += text
    if shop.inventory[i]["cost_type"] == "m":
      if mora_text == "None":
        mora_text = text
      else:
        mora_text += text
    if shop.inventory[i]["cost_type"] == "sd":
      if sd_text == "None":
        sd_text = text
      else:
        sd_text += text
    if shop.inventory[i]["cost_type"] == "sg":
      if sg_text == "None":
        sg_text = text
      else:
        sg_text += text
  
  embed = discord.Embed(title=f"{u.nickname}'s Shop", color=discord.Color.dark_green())
  if _type == "all":
    embed.add_field(name="Primogems Shop",value=primo_text, inline=False)
    embed.add_field(name="Mora Shop",value=mora_text, inline=False)
    embed.add_field(name="Stardust Shop",value=sd_text, inline=False)
    embed.add_field(name="Starglitter Shop",value=sg_text, inline=False)
  elif _type == "p":
    embed.add_field(name="Primogems Shop",value=primo_text, inline=False)
  elif _type == "m":
    embed.add_field(name="Mora Shop",value=mora_text, inline=False)
  elif _type == "sd":
    embed.add_field(name="Stardust Shop",value=sd_text, inline=False)
  elif _type == "sg":
    embed.add_field(name="Starglitter Shop",value=sg_text, inline=False)
  
  await ctx.send(embed=embed)

def does_exist(_id):
  u = database_mongo.get_shop_dict(_id)
  if u == None:
    return False
  else:
    return True

def generate_shop(_id):
  SI_list = database_mongo.get_all_shop_items_list()
  shop = Shop(int(_id), {})
  for SI in SI_list:
    shop.add_item(get_shop_item(SI))
  database_mongo.save_shop(shop)

def generate_all_shops():
  id_list = database_mongo.get_all_users_list_ids()
  for i in id_list:
    generate_shop(i)

def generate_shop_items():
  database_mongo.save_shop_item(Shop_Item(item.Item("Primogems", "primogems", "160 Primogems", 160, 6, "currency").get_dict(), 5, "sg", -1, -1))