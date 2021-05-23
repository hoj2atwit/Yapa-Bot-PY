import database_mongo
import character
import weapon
import random
import item
import user
import formatter
import discord
import prefix
import commission
import asyncio
import error

sixStarChars = character.get_six_star_characters()
fiveStarChars = character.get_five_star_characters()
fourStarChars = character.get_four_star_characters()
fiveStarWeaps = weapon.get_five_star_weapons()
fourStarWeaps = weapon.get_four_star_weapons()
threeStarWeaps = weapon.get_three_star_weapons()
twoStarWeaps = weapon.get_two_star_weapons()
oneStarWeaps = weapon.get_one_star_weapons()

fiveStarWishGifSingle = "Images/Gifs/SingleFiveStar.gif"
fourStarWishGifSingle = "Images/Gifs/SingleFourStar.gif"
threeStarWishGifSingle = "Images/Gifs/SingleThreeStar.gif"
fiveStarWishGifTen = "Images/Gifs/TenFiveStar.gif"
fourStarWishGifTen = "Images/Gifs/TenFourStar.gif"

wishDelayTime = 7.8

#types
#A = artifact
#W = weapon
#C = character
#M = Mora
#P = Primo
def rand_five_star(u):
  r = random.randint(0, 2)
  if(r > 0):
    r = 0
    if(len(fiveStarChars) > 1):
      r = random.randint(0, len(fiveStarChars)-1)
    u.add_character(fiveStarChars[r].copy())
    return (fiveStarChars[r].copy()), "c"
  else:
    r = 0
    if(len(fiveStarWeaps) > 1):
      r = random.randint(0, len(fiveStarWeaps)-1)
    u.add_weapon(fiveStarWeaps[r].copy())
    return (fiveStarWeaps[r].copy()), "w"

#types
#A = artifact
#W = weapon
#C = character
#M = Mora
#P = Primo
def rand_four_star(u):
  r = random.randint(0, 1)
  if(r > 0):
    r = 0
    if(len(fourStarChars) > 1):
      r = random.randint(0, len(fourStarChars)-1)
    u.add_character(fourStarChars[r].copy())
    return fourStarChars[r].copy(), "c"
  else:
    r = 0
    if(len(fourStarWeaps) > 1):
      r = random.randint(0, len(fourStarWeaps)-1)
    u.add_weapon(fourStarWeaps[r].copy())
    return fourStarWeaps[r].copy(), "w"

#types
#A = artifact
#W = weapon
#C = character
#M = Mora
#P = Primo
def rand_three_star(u):
  r = 0
  if(len(threeStarWeaps) > 1):
    r = random.randint(0, len(threeStarWeaps)-1)
  u.add_weapon(threeStarWeaps[r].copy())
  return threeStarWeaps[r].copy(), "w"

def rand_two_star(u):
  r = 0
  if(len(twoStarWeaps) > 1):
    r = random.randint(0, len(twoStarWeaps)-1)
  u.add_weapon(twoStarWeaps[r].copy())
  return twoStarWeaps[r].copy(), "w"

def rand_one_star(u):
  r = 0
  if(len(oneStarWeaps) > 1):
    r = random.randint(0, len(oneStarWeaps)-1)
  u.add_weapon(oneStarWeaps[r].copy())
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
    return rand_three_star(u)
  if r >= 9000:
    return rand_two_star(u)
  elif r >= 4000:
    return rand_one_star(u)
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
    return (rand_five_star(u), True, True)
  if guarentee:
    r = random.randint(9000, 10000)
  else:
    r = random.randint(0, 10000)
  if r >= 9900:
    return (rand_five_star(u), True, True)
  if r >= 9000:
    return (rand_four_star(u), False, True)
  else:
    return (rand_three_star(u), False, False)
  
def ten_pull(u):
  pity = u.five_pity
  fpity = u.four_pity
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
  u.five_pity = pity
  u.four_pity = fpity
  arr = formatter.reward_list_organizer(arr)
  return (arr, fiveStar)

async def embed_single_pull(ctx, u):
  if u.five_pity >= 89:
    (p, t), five, four = pull(False, True, u)
  elif u.four_pity >= 9:
    (p, t), five, four = pull(True, False, u)
  else:
    (p, t), five, four = pull(False, False, u)
  text = ""

  if five:
    color = discord.Color.gold()
    text =  prefix.fiveStarPrefix + p.name
    u.five_pity = 0
    u.four_pity = 0
  elif four:
    color = discord.Color.purple()
    text =  prefix.fourStarPrefix + p.name
    u.five_pity += 1
    u.four_pity = 0
  else:
    color = discord.Color.blue()
    text =  prefix.threeStarPrefix + p.name
    u.five_pity += 1
    u.four_pity += 1
  if t == "c":
    file = discord.File(p.URL_portrait, f"{p.URL_name}-portrait.png")
    embed = discord.Embed(title=text, color=color)
    embed.set_image(url=f"attachment://{p.URL_name}-portrait.png")
  else:
    file = discord.File(p.URL_icon, f"{p.URL_name}-icon.png")
    embed = discord.Embed(title=text, color=color)
    embed.set_image(url=f"attachment://{p.URL_name}-icon.png")
  u.primogems -= 160
  u.update_equiped_weapons()
  await commission.check_wish_complete(ctx, u, 1)
  
  e = discord.Embed()
  if p.rarity == 5:
    f = discord.File(fiveStarWishGifSingle, "SingleFiveStar.gif")
    e.set_image(url="attachment://SingleFiveStar.gif")
  elif p.rarity == 4:
    f = discord.File(fourStarWishGifSingle, "SingleThreeStar.gif")
    e.set_image(url="attachment://SingleThreeStar.gif")
  else:
    f = discord.File(threeStarWishGifSingle, "SingleThreeStar.gif")
    e.set_image(url="attachment://SingleThreeStar.gif")
    
  msg = await ctx.send(embed=e, file=f)
  await asyncio.sleep(wishDelayTime)
  await msg.delete()
  await ctx.send(ctx.author.mention, embed=embed, file=file)

async def embed_free_single_pull(ctx, name):
  u = user.User(0,name,name,"","none",0,0,0,0,0,0,{},{},{},0,0,0,0,0,"","","",{},{},{},{"1":[], "2":[], "3":[], "4":[]})
  if u.five_pity >= 89:
    (p, t), five, four = pull(False, True, u)
  elif u.four_pity >= 9:
    (p, t), five, four = pull(True, False, u)
  else:
    (p, t), five, four = pull(False, False, u)
  text = ""

  if five:
    color = discord.Color.gold()
    text =  prefix.fiveStarPrefix + p.name
    u.five_pity = 0
    u.four_pity = 0
  elif four:
    color = discord.Color.purple()
    text =  prefix.fourStarPrefix + p.name
    u.five_pity += 1
    u.four_pity = 0
  else:
    color = discord.Color.blue()
    text =  prefix.threeStarPrefix + p.name
    u.five_pity += 1
    u.four_pity += 1
  if t == "c":
    f = discord.File(p.URL_portrait, f"{p.URL_name}-portrait.png")
    embed = discord.Embed(title=text, color=color, description="Free pulls will not be added to your collection.")
    embed.set_image(url=f"attachment://{p.URL_name}-portrait.png")
  else:
    f = discord.File(p.URL_icon, f"{p.URL_name}-icon.png")
    embed = discord.Embed(title=text, color=color, description="Free pulls will not be added to your collection.")
    embed.set_image(url=f"attachment://{p.URL_name}-icon.png")
  
  e = discord.Embed()
  if p.rarity == 5:
    file = discord.File(fiveStarWishGifSingle, "SingleFiveStar.gif")
    e.set_image(url="attachment://SingleFiveStar.gif")
  elif p.rarity == 4:
    file = discord.File(fourStarWishGifSingle, "SingleThreeStar.gif")
    e.set_image(url="attachment://SingleThreeStar.gif")
  else:
    file = discord.File(threeStarWishGifSingle, "SingleThreeStar.gif")
    e.set_image(url="attachment://SingleThreeStar.gif")

  msg = await ctx.send(embed=e, file=file)
  await asyncio.sleep(wishDelayTime)
  await msg.delete()
  await ctx.send(ctx.author.mention, embed=embed, file=f)

async def embed_free_ten_pull(ctx, name):
  u = user.User(0,name,name,"","none",0,0,0,0,0,0,{},{},{},0,0,0,0,0,"","","",{},{},{},{"1":[], "2":[], "3":[], "4":[]})
  pulls, five = ten_pull(u)
  if five:
    color = discord.Color.gold()
  else:
    color = discord.Color.purple()

  f = discord.File(pulls[0].URL_icon, f"{pulls[0].URL_name}-icon.png")
  embed = discord.Embed(title=f"{name}\'s 10x Wish", color=color, description="Free pulls will not be added to your collection.")
  embed.set_thumbnail(url=f"attachment://{pulls[0].URL_name}-icon.png")
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

  e = discord.Embed()
  if pulls[0].rarity == 5:
    file = discord.File(fiveStarWishGifTen, "TenFiveStar.gif")
    e.set_image(url="attachment://TenFiveStar.gif")
  else:
    file = discord.File(fourStarWishGifTen, "TenFourStar.gif")
    e.set_image(url="attachment://TenFourStar.gif")
  
  msg = await ctx.send(embed=e, file=file)
  await asyncio.sleep(wishDelayTime)
  await msg.delete()
  await ctx.send(ctx.author.mention, embed=embed, file=f)

async def embed_ten_pull(ctx, u):
  pulls, five = ten_pull(u)
  if five:
    color = discord.Color.gold()
  else:
    color = discord.Color.purple()

  f = discord.File(pulls[0].URL_icon, f"{pulls[0].URL_name}-icon.png")
  embed = discord.Embed(title=f"{u.nickname}\'s 10x Wish", color=color)
  embed.set_thumbnail(url=f"attachment://{pulls[0].URL_name}-icon.png")
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
  u.update_equiped_weapons()
  await commission.check_wish_complete(ctx, u, 10)

  e = discord.Embed()
  if pulls[0].rarity == 5:
    file = discord.File(fiveStarWishGifTen, "TenFiveStar.gif")
    e.set_image(url="attachment://TenFiveStar.gif")
  else:
    file = discord.File(fourStarWishGifTen, "TenFourStar.gif")
    e.set_image(url="attachment://TenFourStar.gif")
  
  msg = await ctx.send(embed=e, file=file)
  await asyncio.sleep(wishDelayTime)
  await msg.delete()
  await ctx.send(ctx.author.mention, embed=embed, file=f)

async def embed_gamble(ctx, u, amnt, _type, channel):
  if u.resin < 5:
      await error.embed_not_enough_resin(ctx)
      return
  if _type == "m":
      if amnt > u.mora:
          await error.embed_not_enough_mora(ctx)
          return
      else:
          u.mora -= amnt
          await ctx.send(f"You spent {formatter.number_format(amnt)}x Mora to gamble.")
  elif _type == "p":
      if amnt > u.primogems:
          await error.embed_not_enough_primo(ctx)
          return
      else:
          u.primogems -= amnt
          await ctx.send(f"You spent {formatter.number_format(amnt)}x Primogems to gamble.")

  rolls = [random.randint(1, 6), random.randint(1, 6), random.randint(1, 6), random.randint(1, 6), random.randint(1, 6), random.randint(1, 6)]
  jackpot = False
  triple = False
  double = False
  triplePair = False
  doublePair = False
  doubleTriple = False
  quadruple = False
  six = False
  counter = 0
  last = 0
  for i in range(len(rolls)):
      counter = 0
      if rolls[i] != last:
          last = rolls[i]
          for x in range(len(rolls) - i):
              if rolls[i] == rolls[i+x]:
                  counter += 1
          if counter == 6:
              if rolls[i] == 6:
                  jackpot = True
                  break
              else:
                  six = True
                  break
          elif counter >= 4:
              quadruple = True
              break
          elif counter >= 3:
              if triple:
                  doubleTriple = True
              else:
                  triple = True
          elif counter >= 2:
              if double:
                  if doublePair:
                      triplePair = True
                  else:
                      doublePair = True
              else:
                  double = True

  if _type == "m":
      if jackpot and amnt >= 10000:
        u.mora += amnt*100 + database_mongo.get_jackpot_mora()
        embed = discord.Embed(title="JACKPOT--------JACKPOT", description=f"{u.nickname} won the jackpot!")
        embed.add_field(name="Winnings", value=f"**{formatter.number_format(amnt*100 + database_mongo.get_jackpot_mora())}x** Mora")
        embed_jackpot_won_mora(u, (amnt*100+database_mongo.get_jackpot_mora()), channel)
        database_mongo.reset_jackpot_primo()
      elif six:
        u.mora += amnt*10
        embed = discord.Embed(title="MINI-JACKPOT----MINI-JACKPOT", description=f"{u.nickname} won the mini-jackpot!")
        embed.add_field(name="Winnings", value=f"**{formatter.number_format(amnt*10)}x** Mora")
      elif quadruple:
        u.mora += amnt*5
        embed = discord.Embed(title=f"{u.nickname} Won Big!")
        embed.add_field(name="Winnings", value=f"**{formatter.number_format(amnt*5)}x** Mora")
      elif doubleTriple or triplePair:
        u.mora += amnt*2
        embed = discord.Embed(title=f"{u.nickname} Won!")
        embed.add_field(name="Winnings", value=f"**{formatter.number_format(amnt*2)}x** Mora")
      elif triple or doublePair:
        u.mora += amnt
        embed = discord.Embed(title=f"{u.nickname} Won?")
        embed.add_field(name="Winnings", value=f"You got your mora back.")
      else:
        database_mongo.add_to_jackpot_mora(amnt)
        embed = discord.Embed(title=f"{u.nickname} Lost!", description=f"{u.nickname} didn't win any Mora.")
  elif _type == "p":
      if jackpot and amnt >= 160:
        u.primogems += amnt*100 + database_mongo.get_jackpot_primo()
        embed = discord.Embed(title="JACKPOT--------JACKPOT", description=f"{u.nickname} won the jackpot!")
        embed.add_field(name="Winnings", value=f"**{formatter.number_format(amnt*100 + database_mongo.get_jackpot_primo())}x** Primogems")
        embed_jackpot_won_mora(u, (amnt*100+database_mongo.get_jackpot_primo()), channel)
        database_mongo.reset_jackpot_primo()
      elif six:
        u.primogems += amnt*10
        embed = discord.Embed(title="MINI-JACKPOT----MINI-JACKPOT", description=f"{u.nickname} won the mini-jackpot!")
        embed.add_field(name="Winnings", value=f"**{formatter.number_format(amnt*10)}x** Primogems")
      elif quadruple:
        u.primogems += amnt*5
        embed = discord.Embed(title=f"{u.nickname} Won Big!")
        embed.add_field(name="Winnings", value=f"**{formatter.number_format(amnt*5)}x** Primogems")
      elif quadruple or doubleTriple or triplePair:
        u.primogems += amnt*2
        embed = discord.Embed(title=f"{u.nickname} Won!")
        embed.add_field(name="Winnings", value=f"**{formatter.number_format(amnt*2)}x** Primogems")
      elif triple or doublePair:
        u.primogems += amnt
        embed = discord.Embed(title=f"{u.nickname} Won?")
        embed.add_field(name="Winnings", value=f"You got your primogems back.")
      else:
        database_mongo.add_to_jackpot_primo(amnt)
        embed = discord.Embed(title=f"{u.nickname} Lost!", description=f"{u.nickname} didn't win any Primogems.")


  embed.add_field(name="Rolls", value=f"{rolls[0]}, {rolls[1]}, {rolls[2]}, {rolls[3]}, {rolls[4]}, {rolls[5]}")
  u.resin -= 5
  await commission.check_target_complete(ctx, u, "gamble", 1)
  if _type == "p":
    can, timeLeft = u.can_vote()
    userXPReward = int((amnt / 5)*(1.5**(not can)))
    if userXPReward > (u.world_level+1)*100:
        userXPReward = int((u.world_level+1)*100*(1.5**(not can)))
  else:
    can, timeLeft = u.can_vote()
    userXPReward = int((amnt / 1000) * (1.5**(not can)))
    if userXPReward > (u.world_level+1)*50:
        userXPReward = int((u.world_level+1)*50*(1.5**(not can)))
  if userXPReward > 0:
    await u.add_experience(userXPReward, ctx)
    embed.add_field(name="Experience Gained", value=f"**{userXPReward}** Adventure Experience")
  if can:
    embed.set_footer(text=f"You have {formatter.number_format(u.resin)} Resin left.")
  else:
    embed.set_footer(text=f"🔥 Boost Active | You have {formatter.number_format(u.resin)} Resin left.")
  await ctx.send(ctx.author.mention, embed=embed)
  
async def embed_jackpot(ctx):
  embed = discord.Embed(title="Current Jackpots", color=discord.Color.dark_gold())
  embed.add_field(name="Mora Jackpot", value=formatter.number_format(database_mongo.get_jackpot_mora()))
  embed.add_field(name="Primo Jackpot", value=formatter.number_format(database_mongo.get_jackpot_primo()))
  await ctx.send(embed=embed)

async def embed_jackpot_won_primo(u, amount, channel):
  embed = discord.Embed(title=f"{u.nickname} WON THE PRIMOGEMS JACKPOT!", color=discord.Color.blue())
  embed.add_field(name=f"Total Earnings", value=f"{formatter.number_format(amount)}x Primogems")
  await channel.send(f"<@!{u._id}>", embed=embed)

async def embed_jackpot_won_mora(u, amount, channel):
  embed = discord.Embed(title=f"{u.nickname} WON THE PRIMOGEMS JACKPOT!", color=discord.Color.gold())
  embed.add_field(name=f"Total Earnings", value=f"{formatter.number_format(amount)}x Mora")
  await channel.send(f"<@!{u._id}>", embed=embed)