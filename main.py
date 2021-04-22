import discord
import database_mongo
from discord.ext import commands
import os
import user
import pull
import error
import prefix
import formatter
import adventure
import commission
import updater
import threading, time
from dotenv import load_dotenv
import pytz
from datetime import datetime, timedelta

tz = pytz.timezone("America/New_York")
pre = prefix.commandPrefix
load_dotenv()


bot = commands.Bot(f"{pre}", case_insensitive=True)
bot.remove_command("help") # Removing the default help command

def update_commissions_check():
  # This function runs periodically every 1 second
  threading.Timer(1, update_commissions_check).start()

  utc_now = pytz.utc.localize(datetime.utcnow())
  now = utc_now.astimezone(tz)

  current_time = now.strftime("%H:%M:%S")

  if(current_time == '00:00:00' or current_time == '12:00:00'):
    print("Updating Commissions")
    user.generate_all_user_commissions()

def update_counter():
  while True:
    utc_now = pytz.utc.localize(datetime.utcnow())
    now = utc_now.astimezone(tz)
    if database_mongo.get_last_resin_time() == "":
      update_last_resin_time()
      user.recharge_all_resin()
    old = tz.localize(formatter.get_DateTime(database_mongo.get_last_resin_time()), is_dst=None)
    difference = now-old
    minutes, seconds = divmod(difference.seconds, 60)
    hours, minutes = divmod(minutes, 60)
    minutes += (hours * 60) + (difference.days*24*60)
    if minutes >= 100:
      update_last_resin_time()
      for x in range(5):
        user.recharge_all_resin()
      time.sleep(1200)
    elif minutes >= 20:
      update_last_resin_time()
      user.recharge_all_resin()
      time.sleep(1200)
    else:
      differenceDate = old + timedelta(minutes=20)
      difference = differenceDate-now
      minutes, seconds = divmod(difference.seconds, 60)
      hours, minutes = divmod(minutes, 60)
      time.sleep((60*minutes)+seconds)

def get_next_resin_time():
  utc_now = pytz.utc.localize(datetime.utcnow())
  now = utc_now.astimezone(tz)
  old = tz.localize(formatter.get_DateTime(database_mongo.get_last_resin_time()), is_dst=None)
  differenceDate = old + timedelta(minutes=20)
  difference = differenceDate-now
  minutes, seconds = divmod(difference.seconds, 60)
  hours, minutes = divmod(minutes, 60)
  return f"{minutes}M:{seconds}S"

def update_last_resin_time():
  utc_now = pytz.utc.localize(datetime.utcnow())
  now = utc_now.astimezone(tz)
  database_mongo.update_last_resin_time(f"{now.year}/{now.month}/{now.day}/{now.hour}/{now.minute}/{now.second}")





###BOT CHECKS###

async def user_exists(ctx):
  if user.does_exist(ctx.author.id):
    return True
  else:
    await not_started(ctx)
    return False

def user_already_exists(ctx):
  return not user.does_exist(ctx.author.id)

def user_is_me(ctx):
  return str(ctx.author.id) == os.getenv('OWNER_ID')

async def not_started(ctx):
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








###OWNER COMMANDS###

@bot.command(name="update")
@commands.check(user_is_me)
async def update(ctx, arg1, arg2):
    if arg1.lower() == "c" and arg2.lower() == "i":
        print("Getting Character Images")
        updater.get_all_character_images_API()
        await ctx.send(f"{ctx.author.mention}, Character images have been downloaded.")
    elif arg1.lower() == "w" and arg2.lower() == "i":
        print("Getting Weapon Images")
        updater.get_all_weap_images_API()
        await ctx.send(f"{ctx.author.mention}, Weapon images have been downloaded.")

@bot.command(name="test")
@commands.check(user_is_me)
async def test(ctx, mention):
  mention_id = formatter.get_id_from_mention(mention)
  await ctx.send(f"{ctx.author.mention}, <@!{mention_id}>")

#Resets a users timers or commissions
@bot.command(name="reset")
@commands.check(user_is_me)
async def reset(ctx, arg1, arg2):
  if arg1.lower() == "timers" or arg1.lower() == "t":
    mention_id = formatter.get_id_from_mention(arg2)
    if user.does_exist(mention_id):
      user.reset_timers(mention_id)
      await ctx.send(f"<@{mention_id}>\'s User timers reset.")
    else:
      await error.embed_user_does_not_exist(ctx)
  elif arg1.lower() == "commissions" or arg1.lower() == "c" or arg1.lower() == "coms":
    if arg2.lower() == "all":
      user.generate_all_user_commissions()
      await ctx.send(f"{ctx.author.mention}, All commissions have been reset.")
      return
    mention_id = formatter.get_id_from_mention(arg2)
    if user.does_exist(mention_id):
      user.reset_daily_commissions(mention_id)
      await ctx.send(f"<@{mention_id}>\'s commissions reset.")
    else:
      await error.embed_user_does_not_exist(ctx)

#Deletes all user data
@bot.command(name="clear")
@commands.check(user_is_me)
async def clear(ctx):
  database_mongo.wipe_user_collection()
  await ctx.send("All User Data Cleared")

#Command to delete a user's data
@bot.command(name="delete", aliases=["del"])
@commands.check(user_is_me)
async def delete(ctx, memberMention):
  mention_id = formatter.get_id_from_mention(str(memberMention))
  if user.does_exist(mention_id):
    database_mongo.delete_user(mention_id)
    await ctx.send(f"<@{mention_id}>\'s User data deleted")
  else:
    await error.embed_user_does_not_exist(ctx)

#Command to Rob people
@bot.command(name="rob")
@commands.check(user_is_me)
async def rob(ctx, memberMention):
  mention_id = formatter.get_id_from_mention(str(memberMention))
  if user.does_exist(mention_id) and user.does_exist(ctx.author.id):
    u = user.get_user(ctx.author.id)
    user_robbed = user.get_user(mention_id)
    robbedAmnt, robbed = u.rob(user_robbed)
    if robbed:
      e=discord.Embed(title=f"{user.get_user(mention_id).nickname} has been Robbed!",color=discord.Color.red())
      e.add_field(name="_ _", value=f"{u.nickname} stole **{robbedAmnt}** Mora from your account.")
      await ctx.send(f"<@{mention_id}>",embed=e)
      database_mongo.save_user(user_robbed)
      database_mongo.save_user(u)
    else:
      await error.embed_failed_robbery(ctx)
  else:
    await error.embed_user_does_not_exist(ctx)

#Command to give primo
@bot.command(name="giftprimo", aliases=["giftp"])
@commands.check(user_is_me)
async def giftp(ctx, memberMention, amnt=None):
  mention_id = formatter.get_id_from_mention(str(memberMention))
  if user.does_exist(mention_id):
    primo = 16000
    if str(amnt).isdigit() and amnt != None:
      primo = int(amnt)
    u = user.get_user(mention_id)
    member = await ctx.guild.fetch_member(str(mention_id))
    await user.embed_give_primo(ctx, u, primo, member)
    database_mongo.save_user(u)
  else:
    await error.embed_user_does_not_exist(ctx)
    
#Command to give mora
@bot.command(name="giftmora", aliases=["giftm"])
@commands.check(user_is_me)
async def giftm(ctx, memberMention, amnt=None):
  mention_id = formatter.get_id_from_mention(str(memberMention))
  if user.does_exist(mention_id):
    mora = 1000000
    if str(amnt).isdigit() and amnt != None:
      mora = int(amnt)
    u = user.get_user(mention_id)
    member = await ctx.guild.fetch_member(str(mention_id))
    await user.embed_give_mora(ctx, u, mora, member)
    database_mongo.save_user(u)
  else:
    await error.embed_user_does_not_exist(ctx)







###REGULAR USER COMMANDS
@bot.command(name="start")
@commands.check(user_already_exists)
async def start(ctx):
  user.create_user(str(ctx.author.name), ctx.author.id)
  embed = discord.Embed(title = "Starting Adventure", color = discord.Color.green())
  embed.add_field(name = "_ _", value=f"{ctx.author.mention}\'s adventure has now begun!\nDo **[{pre}help]** to get the list of available commands.")
  embed.set_thumbnail(url=ctx.author.avatar_url)
  await ctx.send(ctx.author.mention, embed=embed)

@bot.command(name="profile", aliases=["prof","p"])
@commands.check(user_exists)
async def profile(ctx, arg2=None, *arg3):
  u = user.get_user(ctx.author.id)
  if arg2 != None:
    if arg2.lower().startswith("description") or arg2.lower().startswith("bio") or arg2.lower().startswith("desc"):
      if arg3[0] != "":
        desc = formatter.separate_commands(arg3)
        u.change_description(desc[0])
      else:
        u.change_description("No Description")
      await ctx.send(f"{ctx.author.mention}\'s description has been changed.")
      database_mongo.save_user(u)
    elif arg2.startswith("nickname") or arg2.startswith("nick"):
      if arg3[0] != "":
        nickname = formatter.separate_commands(arg3)
        u.change_nickname(nickname[0])
      else:
        u.change_nickname(u.name)
      await ctx.send(f"{ctx.author.mention}\'s nickname has been changed.")
      database_mongo.save_user(u)
    elif arg2.startswith("favorite") or arg2.lower().startswith("fav"):
      if arg3[0] != "":
        char = formatter.separate_commands(arg3)
        have = u.change_favorite_character(char[0])
        if have:
          await ctx.send(f"{ctx.author.mention}\'s favorite Character has been set to: {formatter.name_unformatter(formatter.name_formatter(char[0]))}")
          database_mongo.save_user(u)
        else:
          await error.embed_get_character_suggestions(ctx, u, char[0])
    else:
      mention_id = formatter.get_id_from_mention(str(arg2))
      if user.does_exist(mention_id):
        member = await ctx.guild.fetch_member(mention_id)
        u = user.get_user(mention_id)
        await user.embed_profile(ctx, u, member)
      else:
        await error.embed_user_does_not_exist(ctx)
  else:
    await user.embed_profile(ctx, u, ctx.author)

@bot.command(name="commissions", aliases=["com","c"])
@commands.check(user_exists)
async def commissions(ctx):
  u = user.get_user(ctx.author.id)
  await commission.show_commissions(ctx, u)

@bot.command(name="balance", aliases=["bal","b"])
@commands.check(user_exists)
async def balance(ctx):
  u = user.get_user(ctx.author.id)
  await user.embed_balance(ctx, u)

@bot.command(name="daily", aliases=["day","d"])
@commands.check(user_exists)
async def daily(ctx):
  u = user.get_user(ctx.author.id)
  await user.embed_daily(ctx, u)
  database_mongo.save_user(u)

@bot.command(name="weekly", aliases=["week"])
@commands.check(user_exists)
async def weekly(ctx):
  u = user.get_user(ctx.author.id)
  await user.embed_weekly(ctx, u)
  database_mongo.save_user(u)

@bot.command(name="wish", aliases=["w"])
@commands.check(user_exists)
@commands.cooldown(1, 6, commands.BucketType.user)
async def wish(ctx, arg=None):
  u = user.get_user(ctx.author.id)
  if arg == "10":
    if u.primogems < 1600:
      await error.embed_not_enough_primo(ctx)
      return
    await pull.embed_ten_pull(ctx, u)
    database_mongo.save_user(u)
  else:
    if u.primogems < 160:
      await error.embed_not_enough_primo(ctx)
      return
    await pull.embed_single_pull(ctx, u)
    database_mongo.save_user(u)
      
      

@bot.command(name="free", aliases=["f"])
@commands.check(user_exists)
@commands.cooldown(1, 6, commands.BucketType.user)
async def free(ctx, arg=None):
  u = user.get_user(ctx.author.id)
  if arg == "10":
    await pull.embed_free_ten_pull(ctx, u.nickname)
  else:
    await pull.embed_free_single_pull(ctx, u.nickname)
      

@bot.command(name="resin", aliases=["r", "res"])
@commands.check(user_exists)
async def resin(ctx):
  u = user.get_user(ctx.author.id)
  e, f = user.embed_resin(u)
  e.set_footer(text=f"Only {get_next_resin_time()} till your next {u.get_resin_recharge()} Resin.")
  await ctx.send(embed=e, file=f)

@bot.command(name="listCharacter", aliases=["listc", "lc", "listchar"])
@commands.check(user_exists)
@commands.cooldown(1, 3, commands.BucketType.user)
async def listc(ctx, *args):
  u = user.get_user(ctx.author.id)
  pg = 1
  if len(args) > 0:
    if args[0].isdigit():
      pg = int(args[0])
    else:
      #show specific character info
      name = formatter.separate_commands(args)[0].lower()
      if u.does_character_exist(name):
        await user.embed_show_char_info(ctx, u, u.characters[formatter.name_formatter(name)])
        return
      else:
        await error.embed_get_character_suggestions(ctx, u, name)
        return
  await user.embed_char_list(ctx, u, pg)

@bot.command(name="listWeapon", aliases=["listw", "lw"])
@commands.check(user_exists)
@commands.cooldown(1, 3, commands.BucketType.user)
async def listw(ctx, *args):
  u = user.get_user(ctx.author.id)
  pg = 1
  if len(args) > 0:
    if args[0].isdigit():
      pg = int(args[0])
    else:
      #show specific character info
      name = formatter.separate_commands(args)[0]
      if u.does_weapon_exist(name):
        await user.embed_show_weap_info(ctx, u, u.weapons[formatter.name_formatter(name)])
        return
      else:
        await error.embed_get_weapon_suggestions(ctx, u, name)
        return
  await user.embed_weap_list(ctx, u, pg)

@bot.command(name="equip", aliases=["e", "eq"])
@commands.check(user_exists)
async def equip(ctx, *args):
  u = user.get_user(ctx.author.id)
  commands = formatter.separate_commands(args)
  if len(commands) == 2:
    characterName = formatter.split_information(commands[0])[0]
    weaponName = formatter.split_information(commands[1])[0]
    worked, reason = u.equip_weapon(characterName, weaponName)
    if not worked:
      if reason == "c":
        await error.embed_get_character_suggestions(ctx, characterName)
      elif reason == "i":
        await error.embed_weap_is_not_compatible(ctx)
      else:
        await error.embed_get_weapon_suggestions(ctx, weaponName)
    else:
      await ctx.send("Weapon has been equipped.")
      database_mongo.save_user(u)

@bot.command(name="givemora", aliases=["givem", "gm"])
@commands.check(user_exists)
async def givem(ctx, mention, amnt):
  giver = user.get_user(ctx.author.id)
  taker_ID = formatter.get_id_from_mention(str(mention))
  if user.does_exist(taker_ID) and str(taker_ID) != giver._id:
    if amnt.isdigit():
      member = await ctx.guild.fetch_member(taker_ID)
      taker = user.get_user(taker_ID)
      mora = int(amnt)
      await user.embed_donate_mora(ctx, giver, taker, mora, member)
      database_mongo.save_user(giver)
      database_mongo.save_user(taker)
  else:
    await error.embed_user_does_not_exist(ctx)

@bot.command(name="giveprimo", aliases=["givep", "gp"])
@commands.check(user_exists)
async def givep(ctx, mention, amnt):
  giver = user.get_user(ctx.author.id)
  taker_ID = formatter.get_id_from_mention(str(mention))
  if user.does_exist(taker_ID) and str(taker_ID) != giver.ID:
    if amnt.isdigit():
      member = await ctx.guild.fetch_member(int(taker_ID))
      taker = user.get_user(taker_ID)
      primo = int(amnt)
      await user.embed_donate_primo(ctx, giver, taker, primo, member)
      database_mongo.save_user(giver)
      database_mongo.save_user(taker)
  else:
    await error.embed_user_does_not_exist(ctx)

@bot.command(name="condense", aliases=["con"])
@commands.check(user_exists)
async def condense(ctx, arg=None):
  u = user.get_user(ctx.author.id)
  amnt = 1
  if arg != None:
    if arg.isdigit():
      amnt = int(arg)
    elif arg.lower().startswith("use"):
      await user.embed_use_condensed(ctx, u)
      database_mongo.save_user(u)
      return
  await user.embed_condensed(ctx, u, amnt)
  database_mongo.save_user(u)

@bot.command(name="adventure", aliases=["adv", "a"])
@commands.check(user_exists)
@commands.cooldown(1, 5.0, commands.BucketType.user)
async def _adventure(ctx, *args):
  u = user.get_user(ctx.author.id)
  commands = formatter.separate_commands(args)
  charList = []
  for i in range(len(commands)):
    charList.append(formatter.split_information(commands[i])[0].lower())
  await adventure.embed_adventure(ctx, u, charList)
  database_mongo.save_user(u)
    
@bot.command(name="trivia", aliases=["triv","t"])
@commands.check(user_exists)
async def trivia(ctx, TID, *answer):
  u = user.get_user(ctx.author.id)  
  answerString = formatter.separate_commands(answer)[0]
  await commission.answer_trivia(ctx, u, TID.upper(), answerString)
  database_mongo.save_user(u)

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

threading.Thread(target=update_counter).start()
update_commissions_check()
bot.run(os.getenv('TOKEN'))