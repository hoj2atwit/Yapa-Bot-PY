import character
import weapon
import random
import item
import user
import formatter
import discord
import prefix
import adventure

fiveStarChars = character.getFiveStarChars()
fourStarChars = character.getFourStarChars()
fiveStarWeaps = weapon.getFiveStarWeaps()
fourStarWeaps = weapon.getFourStarWeaps()
threeStarWeaps = weapon.getThreeStarWeaps()
twoStarWeaps = weapon.getTwoStarWeaps()
oneStarWeaps = weapon.getOneStarWeaps()

#types
#A = artifact
#W = weapon
#C = character
#M = Mora
#P = Primo
def randFiveStar(u):
  r = random.randint(0, 2)
  if(r > 0):
    r = 0
    if(len(fiveStarChars) > 1):
      r = random.randint(0, len(fiveStarChars)-1)
    u.addChar(fiveStarChars[r].copy())
    return (fiveStarChars[r].copy()), "c"
  else:
    r = 0
    if(len(fiveStarWeaps) > 1):
      r = random.randint(0, len(fiveStarWeaps)-1)
    u.addWeap(fiveStarWeaps[r].copy())
    return (fiveStarWeaps[r].copy()), "w"

#types
#A = artifact
#W = weapon
#C = character
#M = Mora
#P = Primo
def randFourStar(u):
  r = random.randint(0, 1)
  if(r > 0):
    r = 0
    if(len(fourStarChars) > 1):
      r = random.randint(0, len(fourStarChars)-1)
    u.addChar(fourStarChars[r].copy())
    return fourStarChars[r].copy(), "c"
  else:
    r = 0
    if(len(fourStarWeaps) > 1):
      r = random.randint(0, len(fourStarWeaps)-1)
    u.addWeap(fourStarWeaps[r].copy())
    return fourStarWeaps[r].copy(), "w"

#types
#A = artifact
#W = weapon
#C = character
#M = Mora
#P = Primo
def randThreeStar(u):
  r = 0
  if(len(threeStarWeaps) > 1):
    r = random.randint(0, len(threeStarWeaps)-1)
  u.addWeap(threeStarWeaps[r].copy())
  return threeStarWeaps[r].copy(), "w"

def randTwoStar(u):
  r = 0
  if(len(twoStarWeaps) > 1):
    r = random.randint(0, len(twoStarWeaps)-1)
  u.addWeap(twoStarWeaps[r].copy())
  return twoStarWeaps[r].copy(), "w"

def randOneStar(u):
  r = 0
  if(len(oneStarWeaps) > 1):
    r = random.randint(0, len(oneStarWeaps)-1)
  u.addWeap(oneStarWeaps[r].copy())
  return oneStarWeaps[r].copy(), "w"

#types
#A = artifact
#W = weapon
#C = character
#M = Mora
#P = Primo
def dropSingle(u):
  r = random.randint(0, 10000)
  if r >= 9900:
    return randThreeStar(u)
  if r >= 9000:
    return randTwoStar(u)
  elif r >= 4000:
    return randOneStar(u)
  else:
    r = random.randInt(100, 1000)
    return item.Item("Mora", r)

#types
#A = artifact
#W = weapon
#C = character
#M = Mora
#P = Primo
def drop():
  r = random.randInt(3,9)
  drops = []
  for i in range(r):
    drops.append(dropSingle())
  return drops

#types
#A = artifact
#W = weapon
#C = character
#M = Mora
#P = Primo
def pull(guarentee, guarenteeFive, u):
  if guarenteeFive:
    return (randFiveStar(u), True, True)
  if guarentee:
    r = random.randint(9000, 10000)
  else:
    r = random.randint(0, 10000)
  if r >= 9900:
    return (randFiveStar(u), True, True)
  if r >= 9000:
    return (randFourStar(u), False, True)
  else:
    return (randThreeStar(u), False, False)
  
def tenPull(u):
  pity = u.pity
  fpity = u.lastFour
  arr = []
  fiveStar = False
  fourStar = False
  for i in range(10):
    if pity >= 89:
      ((p, t), fiveStar, fourStar) = pull(True, True, u)
      pity = 0
      fpity = 0
    elif(i == 9) & (not fourStar) & (not fiveStar):
      ((p, t), fiveStar, fourStar) = pull(True, False, u)
      if fiveStar:
        pity = 0
      else:
        pity += 1
      fpity = 0
    else:
      ((p, t), five, four) = pull(False, False, u)
      if ((not fiveStar) & five):
        fiveStar = True
      if((not fourStar) & four):
        fourStar = True
      if five:
        pity = 0
        fpity = 0
      elif four:
        pity += 1
        fpity = 0
      else:
        pity += 1
        fpity += 1
    arr.append(p)
  u.pity = pity
  u.lastFour = fpity
  arr = formatter.rewardListOrganizer(arr)
  return (arr, fiveStar)

async def embedSinglePull(ctx, u):
  if u.pity >= 89:
    (p, t), five, four = pull(False, True, u)
  elif u.lastFour >= 9:
    (p, t), five, four = pull(True, False, u)
  else:
    (p, t), five, four = pull(False, False, u)
  text = ""

  if five:
    color = discord.Color.gold()
    text =  prefix.fiveStarPrefix + p.name
    u.pity = 0
    u.lastFour = 0
  elif four:
    color = discord.Color.purple()
    text =  prefix.fourStarPrefix + p.name
    u.pity += 1
    u.lastFour = 0
  else:
    color = discord.Color.blue()
    text =  prefix.threeStarPrefix + p.name
    u.pity += 1
    u.lastFour += 1
  if t == "c":
    file = discord.File(p.portraitURL, f"{p.urlName}-portrait.png")
    embed = discord.Embed(title=text, color=color)
    embed.set_image(url=f"attachment://{p.urlName}-portrait.png")
  else:
    file = discord.File(p.iconURL, f"{p.urlName}-icon.png")
    embed = discord.Embed(title=text, color=color)
    embed.set_image(url=f"attachment://{p.urlName}-icon.png")
  u.primogems -= 160
  u.updateEquippedWeaps()
  await adventure.checkWishComplete(ctx, u, 1)
  user.saveUser(u)
  return embed, file, p.rarity

async def embedFreeSinglePull(name):
  u = user.User(name,"","","","",0,0,0,0,0,0,{},{},{},0,0,0,0,0,"","",{},{},{})
  if u.pity >= 89:
    (p, t), five, four = pull(False, True, u)
  elif u.lastFour >= 9:
    (p, t), five, four = pull(True, False, u)
  else:
    (p, t), five, four = pull(False, False, u)
  text = ""

  if five:
    color = discord.Color.gold()
    text =  prefix.fiveStarPrefix + p.name
    u.pity = 0
    u.lastFour = 0
  elif four:
    color = discord.Color.purple()
    text =  prefix.fourStarPrefix + p.name
    u.pity += 1
    u.lastFour = 0
  else:
    color = discord.Color.blue()
    text =  prefix.threeStarPrefix + p.name
    u.pity += 1
    u.lastFour += 1
  if t == "c":
    file = discord.File(p.portraitURL, f"{p.urlName}-portrait.png")
    embed = discord.Embed(title=text, color=color, description="Free pulls will not be added to your collection.")
    embed.set_image(url=f"attachment://{p.urlName}-portrait.png")
  else:
    file = discord.File(p.iconURL, f"{p.urlName}-icon.png")
    embed = discord.Embed(title=text, color=color, description="Free pulls will not be added to your collection.")
    embed.set_image(url=f"attachment://{p.urlName}-icon.png")
  return embed, file, p.rarity

async def embedFreeTenPull(name):
  u = user.User(name,"","","","",0,0,0,0,0,0,{},{},{},0,0,0,0,0,"","",{},{},{})
  pulls, five = tenPull(u)
  if five:
    color = discord.Color.gold()
  else:
    color = discord.Color.purple()

  file = discord.File(pulls[0].iconURL, f"{pulls[0].urlName}-icon.png")
  embed = discord.Embed(title=f"{name}\'s 10x Wish", color=color, description="Free pulls will not be added to your collection.")
  embed.set_thumbnail(url=f"attachment://{pulls[0].urlName}-icon.png")
  text = ""
  for i in pulls:
    if i.rarity == 5:
      text += prefix.fiveStarPrefix
    if i.rarity == 4:
      text += prefix.fourStarPrefix
    if i.rarity == 3:
      text += prefix.threeStarPrefix
    text += i.name + "\n"
  embed.add_field(name = "_ _", value = text, inline=False)
  return embed, file, pulls[0].rarity

async def embedTenPull(ctx, u):
  pulls, five = tenPull(u)
  if five:
    color = discord.Color.gold()
  else:
    color = discord.Color.purple()

  file = discord.File(pulls[0].iconURL, f"{pulls[0].urlName}-icon.png")
  embed = discord.Embed(title=f"{u.name}\'s 10x Wish", color=color)
  embed.set_thumbnail(url=f"attachment://{pulls[0].urlName}-icon.png")
  text = ""
  for i in pulls:
    if i.rarity == 5:
      text += prefix.fiveStarPrefix
    if i.rarity == 4:
      text += prefix.fourStarPrefix
    if i.rarity == 3:
      text += prefix.threeStarPrefix
    text += i.name + "\n"
  embed.add_field(name = "_ _", value = text, inline=False)
  u.primogems -= 1600
  u.updateEquippedWeaps()
  await adventure.checkWishComplete(ctx, u, 10)
  user.saveUser(u)
  return embed, file, pulls[0].rarity