import discord
from discord.ext import commands
import os
import user
import pull
import asyncio
import error
import prefix
import formatter
import adventure
import threading, time
from replit import db
from keep_alive import keep_alive
import pytz
from datetime import datetime, timedelta

fiveStarWishGifSingle = "Images/Gifs/SingleFiveStar.gif"
fourStarWishGifSingle = "Images/Gifs/SingleThreeStar.gif"
threeStarWishGifSingle = "Images/Gifs/SingleThreeStar.gif"
fiveStarWishGifTen = "Images/Gifs/TenFiveStar.gif"
fourStarWishGifTen = "Images/Gifs/TenFourStar.gif"

tz = pytz.timezone("America/New_York")
pre = prefix.commandPrefix

bot = commands.Bot(f"{pre}", case_insensitive=True)
bot.remove_command("help") # Removing the default help command

async def user_exists(ctx):
  if user.doesExist(str(ctx.author.id)):
    return True
  else:
    await notStarted(ctx)
    return False

def user_already_exists(ctx):
  return not user.doesExist(str(ctx.author.id))

def user_is_me(ctx):
  return str(ctx.author.id) == os.getenv('OWNER_ID')

def updateCommissionsCheck():
  # This function runs periodically every 1 second
  threading.Timer(1, updateCommissionsCheck).start()

  utc_now = pytz.utc.localize(datetime.utcnow())
  now = utc_now.astimezone(tz)

  current_time = now.strftime("%H:%M:%S")

  if(current_time == '00:00:00'):
    print("Updating Commissions")
    user.generateAllUserCommissions()

def updateCounter():
  while True:
    utc_now = pytz.utc.localize(datetime.utcnow())
    now = utc_now.astimezone(tz)
    if db["LastResinTime"] == "":
      updateLastResinTime()
      user.rechargeAllResin()
    old = tz.localize(formatter.getDateTime(db["LastResinTime"]), is_dst=None)
    difference = now-old
    minutes, seconds = divmod(difference.seconds, 60)
    hours, minutes = divmod(minutes, 60)
    minutes += (hours * 60) + (difference.days*24*60)
    if minutes >= 100:
      updateLastResinTime()
      for x in range(5):
        user.rechargeAllResin()
      time.sleep(1200)
    elif minutes >= 20:
      updateLastResinTime()
      user.rechargeAllResin()
      time.sleep(1200)
    else:
      differenceDate = old + timedelta(minutes=20)
      difference = differenceDate-now
      minutes, seconds = divmod(difference.seconds, 60)
      hours, minutes = divmod(minutes, 60)
      time.sleep((60*minutes)+seconds)

def getNextResinTime():
  utc_now = pytz.utc.localize(datetime.utcnow())
  now = utc_now.astimezone(tz)
  old = tz.localize(formatter.getDateTime(db["LastResinTime"]), is_dst=None)
  differenceDate = old + timedelta(minutes=20)
  difference = differenceDate-now
  minutes, seconds = divmod(difference.seconds, 60)
  hours, minutes = divmod(minutes, 60)
  return f"{minutes}M:{seconds}S"

def updateLastResinTime():
  utc_now = pytz.utc.localize(datetime.utcnow())
  now = utc_now.astimezone(tz)
  db["LastResinTime"] = f"{now.year}/{now.month}/{now.day}/{now.hour}/{now.minute}/{now.second}"

async def notStarted(ctx):
  await ctx.send(f"{ctx.author.mention}, Use **[{pre}start]** to begin your adventure")

#When bot turns on
@bot.event
async def on_ready():
  print('We have logged in as {0.user}'.format(bot))
  await bot.change_presence(activity=discord.Game(name=f"{pre}help"))

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f"{ctx.author.mention}This command is on cooldown, you can use it in {round(error.retry_after, 2)} seconds.")

#Resets a users timers or commissions
@bot.command(name="reset")
@commands.check(user_is_me)
async def reset(ctx, arg1, arg2):
  if arg1.lower() == "timers" or arg1.lower() == "t":
    mention_id = formatter.getIDFromMention(str(arg2))
    if user.doesExist(mention_id):
      user.resetTimers(mention_id)
      await ctx.send(f"<@{mention_id}>\'s User timers reset.")
    else:
      e = error.embedUserDoesNotExist()
      await ctx.send(embed=e)
  elif arg1.lower() == "commissions" or arg1.lower() == "c" or arg1.lower() == "coms":
    mention_id = formatter.getIDFromMention(str(arg2))
    if user.doesExist(mention_id):
      user.resetDailyCommissions(mention_id)
      await ctx.send(f"<@{mention_id}>\'s commissions reset.")
    else:
      e = error.embedUserDoesNotExist()
      await ctx.send(embed=e)

#Deletes all user data
@bot.command(name="clear")
@commands.check(user_is_me)
async def clear(ctx):
  user.clearUserData()
  await ctx.send("All User Data Cleared")

#Command to delete a user's data
@bot.command(name="delete", aliases=["del"])
@commands.check(user_is_me)
async def delete(ctx, memberMention):
  mention_id = formatter.getIDFromMention(str(memberMention))
  if user.doesExist(mention_id):
    user.deleteUser(mention_id)
    await ctx.send(f"<@{mention_id}>\'s User data deleted")
  else:
    e = error.embedUserDoesNotExist()
    await ctx.send(embed=e)

#Command to Rob people
@bot.command(name="rob")
@commands.check(user_is_me)
async def rob(ctx, memberMention):
  mention_id = formatter.getIDFromMention(str(memberMention))
  if user.doesExist(mention_id) and user.doesExist(str(ctx.author.id)):
    u = user.getUser(str(ctx.author.id))
    robbedAmnt, robbed = u.rob(user.getUser(mention_id))
    if robbed:
      e=discord.Embed(title=f"{user.getUser(mention_id).nickname} has been Robbed!",color=discord.Color.red())
      e.add_field(name="_ _", value=f"{u.nickname} stole **{robbedAmnt}** Mora from your account.")
      await ctx.send(f"<@{mention_id}>",embed=e)
    else:
      e=error.embedFailedRobbery()
      await ctx.send(embed=e)
  else:
    e = error.embedUserDoesNotExist()
    await ctx.send(embed=e)

#Command to give primo
@bot.command(name="giftprimo", aliases=["giftp"])
@commands.check(user_is_me)
async def giftp(ctx, memberMention, amnt=None):
  mention_id = formatter.getIDFromMention(str(memberMention))
  if user.doesExist(mention_id):
    primo = 16000
    if str(amnt).isdigit() and amnt != None:
      primo = int(amnt)
    u = user.getUser(mention_id)
    e, f = user.embedGivePrimo(u, primo)
    member = await ctx.guild.fetch_member(int(mention_id))
    await ctx.send(member.mention, embed=e, file=f)
  else:
    e = error.embedUserDoesNotExist()
    await ctx.send(embed=e)
    
#Command to give mora
@bot.command(name="giftmora", aliases=["giftm"])
@commands.check(user_is_me)
async def giftm(ctx, memberMention, amnt=None):
  mention_id = formatter.getIDFromMention(str(memberMention))
  if user.doesExist(mention_id):
    mora = 1000000
    if str(amnt).isdigit() and amnt != None:
      mora = int(amnt)
    u = user.getUser(mention_id)
    e, f = user.embedGiveMora(u, mora)
    member = await ctx.guild.fetch_member(int(mention_id))
    await ctx.send(member.mention, embed=e, file=f)
  else:
    e = error.embedUserDoesNotExist()
    await ctx.send(embed=e)

@bot.command(name="start")
@commands.check(user_already_exists)
async def start(ctx):
  user_id = formatter.getIDFromMention(str(ctx.author.id))
  if not user.doesExist(user_id):
    user.createUser(str(ctx.author.name), str(ctx.author.id))
    embed = discord.Embed(title = "Starting Adventure", color = discord.Color.green())
    embed.add_field(name = "_ _", value=f"{ctx.author.mention}\'s adventure has now begun!\nDo **[{pre}help]** to get the list of available commands.")
    embed.set_thumbnail(url=ctx.author.avatar_url)
    await ctx.send(ctx.author.mention, embed=embed)

@bot.command(name="profile", aliases=["prof","p"])
@commands.check(user_exists)
async def profile(ctx, arg2=None, *arg3):
  u = user.getUser(str(ctx.author.id))
  if arg2 != None:
    if arg2.lower().startswith("description") or arg2.lower().startswith("bio") or arg2.lower().startswith("desc"):
      if arg3[0] != "":
        desc = formatter.separate_commands(arg3)
        u.changeDescription(desc[0])
      else:
        u.changeDescription("No Description")
      await ctx.send(f"{ctx.author.mention}\'s description has been changed.")
    elif arg2.startswith("nickname") or arg2.startswith("nick"):
      if arg3[0] != "":
        nickname = formatter.separate_commands(arg3)
        u.changeNickname(nickname[0])
      else:
        u.changeNickname(u.name)
      await ctx.send(f"{ctx.author.mention}\'s nickname has been changed.")
    elif arg2.startswith("favorite") or arg2.lower().startswith("fav"):
      if arg3[0] != "":
        char = formatter.separate_commands(arg3)
        have = u.changeFavoriteChar(char[0])
        if have:
          await ctx.send(f"{ctx.author.mention}\'s favorite Character has been set to: {formatter.nameFormatter(formatter.nameUnformatter(char[0]))}")
        else:
          await ctx.send(embed=error.embedCharIsNotOwned())
    else:
      mention_id = formatter.getIDFromMention(str(arg2))
      if user.doesExist(mention_id):
        member = await ctx.guild.fetch_member(mention_id)
        url = formatter.getAvatar(member)
        u = user.getUser(mention_id)
        e = user.embedProfile(u)
        e.set_thumbnail(url=url)
        e.set_footer(text=f"{ctx.author.mention}")
        await ctx.send(embed=e)
      else:
        e = error.embedUserDoesNotExist()
        await ctx.send(embed=e)
  else:
    _id = formatter.getIDFromMention(str(ctx.author.id))
    member = await ctx.guild.fetch_member(_id)
    url = formatter.getAvatar(member)
    e = user.embedProfile(u)
    e.set_thumbnail(url=url)
    e.set_footer(text=f"{ctx.author.mention}")
    await ctx.send(embed=e)

@bot.command(name="commissions", aliases=["com","c"])
@commands.check(user_exists)
async def commissions(ctx):
  u = user.getUser(str(ctx.author.id))
  await adventure.showCommissions(ctx, u)

@bot.command(name="balance", aliases=["bal","b"])
@commands.check(user_exists)
async def balance(ctx):
  u = user.getUser(str(ctx.author.id))
  e, f = user.embedBal(u)
  e.set_footer(text=f"{ctx.author.mention}")
  await ctx.send(embed=e, file=f)

@bot.command(name="daily", aliases=["day","d"])
@commands.check(user_exists)
async def daily(ctx):
  u = user.getUser(str(ctx.author.id))
  await user.embedDaily(ctx, u)

@bot.command(name="weekly", aliases=["week"])
@commands.check(user_exists)
async def weekly(ctx):
  u = user.getUser(str(ctx.author.id))
  await user.embedWeekly(ctx, u)

@bot.command(name="wish", aliases=["w"])
@commands.check(user_exists)
@commands.cooldown(1, 6, commands.BucketType.user)
async def wish(ctx, arg=None):
  u = user.getUser(str(ctx.author.id))
  if arg == None:
    if u.primogems < 160:
      e = error.embedNotEnoughPrimo()
      await ctx.send(ctx.author.mention, embed=e)
      return
    embed, f, rarity = await pull.embedSinglePull(ctx, u)
    e = discord.Embed()
    if rarity == 5:
      file = discord.File(fiveStarWishGifSingle, "SingleFiveStar.gif")
      e.set_image(url="attachment://SingleFiveStar.gif")
    elif rarity == 4:
      file = discord.File(fourStarWishGifSingle, "SingleThreeStar.gif")
      e.set_image(url="attachment://SingleThreeStar.gif")
    else:
      file = discord.File(threeStarWishGifSingle, "SingleThreeStar.gif")
      e.set_image(url="attachment://SingleThreeStar.gif")
    msg = await ctx.send(embed=e, file=file)
    await asyncio.sleep(7)
    await msg.delete()
    await ctx.send(ctx.author.mention, embed=embed, file=f)
  else:
    if arg == "10":
      if u.primogems < 1600:
        e = error.embedNotEnoughPrimo()
        await ctx.send(ctx.author.mention, embed=e)
        return
      embed, f, rarity = await pull.embedTenPull(ctx, u)
      e = discord.Embed()
      if rarity == 5:
        file = discord.File(fiveStarWishGifTen, "TenFiveStar.gif")
        e.set_image(url="attachment://TenFiveStar.gif")
      else:
        file = discord.File(fourStarWishGifTen, "TenFourStar.gif")
        e.set_image(url="attachment://TenFourStar.gif")
      msg = await ctx.send(embed=e, file=file)
      await asyncio.sleep(7)
      await msg.delete()
      await ctx.send(ctx.author.mention, embed=embed, file=f)

@bot.command(name="free", aliases=["f"])
@commands.check(user_exists)
@commands.cooldown(1, 6, commands.BucketType.user)
async def free(ctx, arg=None):
  u = user.getUser(str(ctx.author.id))
  if arg == None:
    embed, f, rarity = await pull.embedFreeSinglePull(u.name)
    e = discord.Embed()
    if rarity == 5:
      file = discord.File(fiveStarWishGifSingle, "SingleFiveStar.gif")
      e.set_image(url="attachment://SingleFiveStar.gif")
    elif rarity == 4:
      file = discord.File(fourStarWishGifSingle, "SingleThreeStar.gif")
      e.set_image(url="attachment://SingleThreeStar.gif")
    else:
      file = discord.File(threeStarWishGifSingle, "SingleThreeStar.gif")
      e.set_image(url="attachment://SingleThreeStar.gif")
    msg = await ctx.send(embed=e, file=file)
    await asyncio.sleep(7)
    await msg.delete()
    await ctx.send(ctx.author.mention, embed=embed, file=f)
  else:
    if arg == "10":
      embed, f, rarity = await pull.embedFreeTenPull(u.name)
      e = discord.Embed()
      if rarity == 5:
        file = discord.File(fiveStarWishGifTen, "TenFiveStar.gif")
        e.set_image(url="attachment://TenFiveStar.gif")
      else:
        file = discord.File(fourStarWishGifTen, "TenFourStar.gif")
        e.set_image(url="attachment://TenFourStar.gif")
      msg = await ctx.send(embed=e, file=file)
      await asyncio.sleep(7)
      await msg.delete()
      await ctx.send(ctx.author.mention, embed=embed, file=f)

@bot.command(name="resin", aliases=["r", "res"])
@commands.check(user_exists)
async def resin(ctx):
  u = user.getUser(str(ctx.author.id))
  e, f = user.embedResin(u)
  e.set_footer(text=f"Only {getNextResinTime()} till your next {u.getResinRecharge()} Resin.")
  await ctx.send(embed=e, file=f)

@bot.command(name="listCharacter", aliases=["listc", "lc", "listchar"])
@commands.check(user_exists)
@commands.cooldown(1, 3, commands.BucketType.user)
async def listc(ctx, *args):
  u = user.getUser(str(ctx.author.id))
  pg = 1
  if len(args) > 0:
    if args[0].isdigit():
      pg = int(args[0])
    else:
      #show specific character info
      name = formatter.separate_commands(args)[0].lower()
      if u.doesCharExist(name):
        await user.embedShowCharInfo(ctx, u, u.characters[formatter.nameUnformatter(name)])
        return
      else:
        await ctx.send(embed=error.embedCharIsNotOwned())
        return
  e = user.embedCharList(u, pg)
  await ctx.send(embed=e)

@bot.command(name="listWeapon", aliases=["listw", "lw"])
@commands.check(user_exists)
@commands.cooldown(1, 3, commands.BucketType.user)
async def listw(ctx, *args):
  u = user.getUser(str(ctx.author.id))
  pg = 1
  if len(args) > 0:
    if args[0].isdigit():
      pg = int(args[0])
    else:
      #show specific character info
      name = formatter.separate_commands(args)[0]
      if u.doesWeapExist(name):
        e, f = user.embedShowWeapInfo(u, u.weapons[formatter.nameUnformatter(name)])
        await ctx.send(embed=e, file=f)
        return
      else:
        await ctx.send(embed=error.embedWeapIsNotOwned())
        return
  e = user.embedWeapList(u, pg)
  await ctx.send(embed=e)

@bot.command(name="equip", aliases=["e", "eq"])
@commands.check(user_exists)
async def equip(ctx, *args):
  u = user.getUser(str(ctx.author.id))
  commands = formatter.separate_commands(args)
  if len(commands) == 2:
    characterName = formatter.splitInformation(commands[0])[0]
    weaponName = formatter.splitInformation(commands[1])[0]
    worked, reason = u.equipWeapon(characterName, weaponName)
    if not worked:
      if reason == "c":
        e = error.embedCharIsNotOwned()
        await ctx.send(embed=e)
      elif reason == "i":
        e = error.embedWeapIsNotCompatible()
        await ctx.send(embed=e)
      else:
        e = error.embedWeapIsNotOwned()
        await ctx.send(embed=e)
    else:
      await ctx.send("Weapon has been equipped.")

@bot.command(name="givemora", aliases=["givem", "gm"])
@commands.check(user_exists)
async def givem(ctx, mention, amnt):
  giver = user.getUser(str(ctx.author.id))
  taker_ID = formatter.getIDFromMention(str(mention))
  if user.doesExist(taker_ID) and str(taker_ID) != giver.ID:
    if amnt.isdigit():
      member = await ctx.guild.fetch_member(int(taker_ID))
      taker = user.getUser(taker_ID)
      mora = int(amnt)
      e = user.embedDonateMora(giver, taker, mora)
      await ctx.send(member.mention, embed=e)
  else:
    e = error.embedUserDoesNotExist()
    await ctx.send(embed=e)

@bot.command(name="giveprimo", aliases=["givep", "gp"])
@commands.check(user_exists)
async def givep(ctx, mention, amnt):
  giver = user.getUser(str(ctx.author.id))
  taker_ID = formatter.getIDFromMention(str(mention))
  if user.doesExist(taker_ID) and str(taker_ID) != giver.ID:
    if amnt.isdigit():
      member = await ctx.guild.fetch_member(int(taker_ID))
      taker = user.getUser(taker_ID)
      primo = int(amnt)
      e = user.embedDonatePrimo(giver, taker, primo)
      await ctx.send(member.mention, embed=e)
  else:
    e = error.embedUserDoesNotExist()
    await ctx.send(embed=e)

@bot.command(name="condense", aliases=["con"])
@commands.check(user_exists)
async def condense(ctx, arg=None):
  u = user.getUser(str(ctx.author.id))
  amnt = 1
  if arg != None:
    if arg.isdigit():
      amnt = int(arg)
    elif arg.lower().startswith("use"):
      await user.embedUseCondensed(ctx, u)
      return
  await user.embedCondensed(ctx, u, amnt)

@bot.command(name="adventure", aliases=["adv", "a"])
@commands.check(user_exists)
@commands.cooldown(1, 5.0, commands.BucketType.user)
async def _adventure(ctx, *args):
  u = user.getUser(str(ctx.author.id))
  commands = formatter.separate_commands(args)
  if len(commands) > 0 and len(commands) <= 4:
    charList = []
    for i in range(len(commands)):
      charList.append(formatter.splitInformation(commands[i])[0].lower())
    await adventure.embedAdventure(ctx, u, charList)
    
@bot.command(name="trivia", aliases=["triv","t"])
@commands.check(user_exists)
async def trivia(ctx, TID, *answer):
  u = user.getUser(str(ctx.author.id))  
  answerString = formatter.separate_commands(answer)[0]
  await adventure.answerTrivia(ctx, u, TID.upper(), answerString)

@bot.command(name="help", aliases=["h"])
async def help(ctx):
  embed = discord.Embed(title = "Yapa Bot Commands 1", color=discord.Color.dark_red())
  text = f"**[{pre}start]** Allows you to start your Yappa Experience.\n"
  text += f"**[{pre}daily]** Allows you to claim daily rewards.\n"
  text += f"**[{pre}weekly]** Allows you to claim weekly rewards.\n"
  text += f"**[{pre}adventure] | [char_name] | [{pre}cn {pre}cn {pre}cn]** Allows you to go on an adventure with up to 4 of your characters at the cost of 20 resin. You must have atleast 1 character to adventure.\n"
  text += f"**[{pre}resin]** Allows you to look at your current resin.\n"
  text += f"**[{pre}condense] | [use, amnt#]** Allows you to store resin in 40 resin capsules. You can only store up to 10 condensed.\n"
  text += f"**[{pre}listc] | [pg#, char_name]** Allows you to look at your personal character collection.\n"
  text += f"**[{pre}listw] | [pg#, weap_name]** Allows you to look at your personal weapon collection.\n_ _\n_ _"
  embed.add_field(name="Basic Commands", value = text, inline=False)


  text = f"**[{pre}wish] | [10]** Allows you to pull for your favorite genshin wishes at the cost of 160 primogems per wish.\n"
  text += f"**[{pre}free] | [10]** Allows you to pull for your favorite genshin wishes for free. These wishes will not be added to your collection.\n_ _\n_ _"
  embed.add_field(name="Wishing Commands", value = text, inline=False)


  text = f"**[{pre}balance]** Allows you to look at your collected currencies.\n"
  text += f"**[{pre}givem] | [amnt#] | [@user]** Allows you to donate mora to another user.\n"
  text += f"**[{pre}givep] | [amnt#] | [@user]** Allows you to donate primogems to another user.\n_ _\n_ _"
  embed.add_field(name="Economic Commands", value = text, inline=False)


  text = f"**[{pre}equip] | [char_name] | [{pre}weap_name, {pre}none]** Allows you to equip a weapon to a chracter. You can only equip things you own.\n_ _\n_ _"
  embed.add_field(name="Character Commands", value = text, inline=False)


  text = f"**[{pre}profile] | [@user]** Allows you to look at your or other user data.\n"
  text += f"**[{pre}profile] | [favorite] | [char_name]** Allows you to set your favorite character. Character must be owned before favoriting.\n"
  text += f"**[{pre}profile] | [description] | [desc...]** Allows you set your profile description.\n"
  text += f"**[{pre}profile] | [nickname] | [nick...]** Allows you set your profile description."
  embed.add_field(name="Profile Commands", value = text, inline=False)


  await ctx.send(embed=embed)


  embed = discord.Embed(title = "Yapa Bot Commands 2", color=discord.Color.dark_red())
  text = f"**[{pre}commission]** Allows you to look at your commissions and their descriptions.\n"
  text += f"**[{pre}trivia] | [triviaID] | [answer]** Allows you to answer your trivia commissions. Trivia id can be found in the () before every trivia commission."
  embed.add_field(name="Commission Commands", value = text, inline=False)


  await ctx.send(embed=embed)

threading.Thread(target=updateCounter).start()
updateCommissionsCheck()
keep_alive()
bot.run(os.getenv('TOKEN'))