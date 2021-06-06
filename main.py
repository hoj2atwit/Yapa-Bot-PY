from random import randint
import discord
from discord.ext.commands.core import command, is_owner
import database_mongo
from discord.ext import commands
from discord.ext import tasks
import os
import user
import pull
import error
import prefix
import formatter
import adventure
import commission
import updater
import asyncio
import threading, time
import shop
import dbl
from dotenv import load_dotenv
import pytz
import blackjack
from datetime import datetime, timedelta

tz = pytz.timezone("America/New_York")
pre = prefix.commandPrefix
load_dotenv()



bot = commands.Bot(f"{pre}", case_insensitive=True, owner_id=int(os.getenv('OWNER_ID')))
bot.remove_command("help") # Removing the default help command
dbl_token = os.getenv('TOP_TOKEN')  # set this to your bot's top.gg token
bot.dblpy = dbl.DBLClient(bot, dbl_token, webhook_path='/dblwebhook', webhook_auth="yapa_pass", webhook_port=5000)

locks = {}

def update_commissions_check():
  # This function runs periodically every 1 second
  threading.Timer(1, update_commissions_check).start()

  utc_now = pytz.utc.localize(datetime.utcnow())
  now = utc_now.astimezone(tz)

  current_time = now.strftime("%H:%M:%S")
  weekno = now.weekday()
  if(current_time == '00:00:00' or current_time == '12:00:00'):
    print("Updating Commissions")
    user.generate_all_user_commissions()
    user.update_leaderboards()
    if current_time == '00:00:00':
      if weekno == 0:
        shop.generate_all_shops()

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

def not_DM(ctx):
    return ctx.author.guild != None

def user_already_exists(ctx):
  return not user.does_exist(ctx.author.id)

async def user_is_me(ctx):
  return await bot.is_owner(ctx.author)

async def not_started(ctx):
  await ctx.send(f"{ctx.author.mention}, Use **[{pre}start]** to begin your adventure")

def lock_exists(ctx):
  global locks
  if str(ctx.author.id) not in locks.keys():
      locks_copy = locks
      locks_copy[str(ctx.author.id)] = asyncio.Lock()
      locks = locks_copy
  return True

def shop_exists(ctx):
  if shop.does_exist(ctx.author.id):
    return True
  else:
    shop.generate_shop(ctx.author.id)
    return True

async def is_minimum_WL(ctx):
  if user.get_user(ctx.author.id).world_level >= 5:
    return True
  else:
    await error.embed_world_level_requirement_error(ctx, 5)
    return False

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
@commands.check(lock_exists)
async def update(ctx, arg1, arg2=None):
    async with locks[str(ctx.author.id)]:
        if arg1.lower() == "c":
          if arg2 == None:
            await ctx.send(f"{ctx.author.mention}, Searching new character data.")
            updater.update_all_characters_DB()
            await ctx.send(f"{ctx.author.mention}, New character data downloaded.")
          elif arg2.lower() == "i":
            await ctx.send(f"{ctx.author.mention}, Searching for new character images.")
            await updater.get_all_character_images_API(ctx)
            await ctx.send(f"{ctx.author.mention}, New character images have been downloaded.")
            
        elif arg1.lower() == "w":
          if arg2 == None:
            await ctx.send(f"{ctx.author.mention}, Searching for new weapon data.")
            updater.update_weapons_DB()
            await ctx.send(f"{ctx.author.mention}, New weapon data downloaded.")
          elif arg2.lower() == "i":
            await ctx.send(f"{ctx.author.mention}, Searching for new weapon images.")
            await updater.get_all_weap_images_API(ctx)
            await ctx.send(f"{ctx.author.mention}, Weapon images have been downloaded.")
            
        elif arg1.lower() == "u":
          if arg2 == None:
            await ctx.send(f"{ctx.author.mention}, Updating All Users.")
            user.update_users()
            await ctx.send(f"{ctx.author.mention}, All users have been updated.")
          elif arg2.lower() == "c":
            await ctx.send(f"{ctx.author.mention}, Updating All User Characters.")
            updater.update_user_characters()
            await ctx.send(f"{ctx.author.mention}, All User Characters have been updated.")
          elif arg2.lower() == "w":
            await ctx.send(f"{ctx.author.mention}, Updating All User Weapons.")
            updater.update_user_weapons()
            await ctx.send(f"{ctx.author.mention}, All User Weapons have been updated.")
        elif arg1.lower() == "com":
          await ctx.send(f"{ctx.author.mention}, Updating All Commissions.")
          commission.generate_all_commissions()
          await ctx.send(f"{ctx.author.mention}, All commissions have been updated.")
        elif arg1.lower() == "shop":
          if arg2 == None:
            await ctx.send(f"{ctx.author.mention}, Updating All Shops.")
            shop.generate_all_shops()
            await ctx.send(f"{ctx.author.mention}, All Shops have been updated.")
          elif arg2.lower() == "i":
            await ctx.send(f"{ctx.author.mention}, Updating All Shop Items.")
            shop.generate_shop_items()
            await ctx.send(f"{ctx.author.mention}, All Shop Items have been updated.")
        elif arg1.lower() == "jp":
          if arg2 == None:
            await ctx.send(f"{ctx.author.mention}, Resetting All Jackpots.")
            database_mongo.setup_jackpot()
            await ctx.send(f"{ctx.author.mention}, All jackpots have been reset.")
          if arg2.lower() == "m":
            await ctx.send(f"{ctx.author.mention}, Resetting Mora Jackpots.")
            database_mongo.reset_jackpot_mora()
            await ctx.send(f"{ctx.author.mention}, Mora jackpot have been reset.")
          if arg2.lower() == "p":
            await ctx.send(f"{ctx.author.mention}, Resetting Primo Jackpots.")
            database_mongo.reset_jackpot_primo()
            await ctx.send(f"{ctx.author.mention}, Primo jackpot have been reset.")
        elif arg1.lower() == "lb":
          await ctx.send(f"{ctx.author.mention}, Updating Leader Boards")
          database_mongo.setup_leaderboard()
          user.update_leaderboards()
          await ctx.send(f"{ctx.author.mention}, All leader Boards have been updated.")
        elif arg1.lower() == "replace":
          await ctx.send(f"{ctx.author.mention}, Replacing with correct thing.")
          try:
            user.replace_weapon_name("prototype-grudge", "prototype-starglitter", "Prototype Starglitter")
          except Exception as e:
            print(e)
          await ctx.send(f"{ctx.author.mention}, Replacing with correct thing.")

@bot.command(name="clear")
@commands.check(not_DM)
@commands.check(user_is_me)
@commands.check(lock_exists)
async def clear(ctx, arg1):
  if arg1 == "shop_items":
    async with locks[str(ctx.author.id)]:
      await ctx.send("Clearing Shop Items")
      database_mongo.wipe_shop_item_collection()
      await ctx.send("Shop Items Cleared")

@bot.command(name="stats")
@commands.check(not_DM)
@commands.check(user_is_me)
@commands.check(lock_exists)
async def stats(ctx):
  async with locks[str(ctx.author.id)]:
    embed = discord.Embed(title="Yapa Top.gg Stats", color = discord.Color.dark_teal())
    bot_info = await bot.dblpy.get_bot_info()
    upvotes = bot_info["points"]
    shard_count = bot_info["shard_count"]
    text = f"**Servers:** {bot.dblpy.guild_count()}\n**Users:** {database_mongo.get_user_collection().count_documents({})}\n**Upvotes:** {upvotes}\n**Shards:** {shard_count}\n"
    embed.add_field(name="Stats", value=text)
    await ctx.send(embed=embed)

@bot.command(name="test")
@commands.check(not_DM)
@commands.check(user_is_me)
@commands.check(lock_exists)
async def test(ctx, mention):
  global locks
  async with locks[str(ctx.author.id)]:
    u = user.get_user(ctx.author.id)
    receiver_id = formatter.get_id_from_mention(mention)
    if user.does_exist(receiver_id) and receiver_id != u._id:
      if str(receiver_id) not in locks.keys():
        locks_copy = locks
        locks_copy[str(receiver_id)] = asyncio.Lock()
        locks = locks_copy
      async with locks[str(receiver_id)]:
        receiver = user.get_user(receiver_id)
        asyncio.get_event_loop().create_task(user.embed_char_list(ctx, u, 1, bot))
        confirm, char1_name = await formatter.request_character_name(ctx, bot, u)
        if not confirm:
          await ctx.send("Trade Cancelled.")
          return
        asyncio.get_event_loop().create_task(user.embed_char_list(ctx, receiver, 1, bot))
        confirm, char2_name = await formatter.request_character_name(ctx, bot, receiver)
        if not confirm:
          await ctx.send("Trade Cancelled.")
          return
        await user.embed_exchange(ctx, bot, u, char1_name, receiver, char2_name)

#Resets a users timers or commissions
@bot.command(name="reset")
@commands.check(not_DM)
@commands.check(user_is_me)
@commands.check(lock_exists)
async def reset(ctx, arg1, arg2):
    async with locks[str(ctx.author.id)]:
      if arg1.lower() == "timers" or arg1.lower() == "t":
        mention_id = formatter.get_id_from_mention(arg2)
        if user.does_exist(mention_id):
          confirm = await formatter.confirmation(ctx, bot)
          if confirm:
              user.reset_timers(mention_id)
              await ctx.send(f"<@{mention_id}>\'s User timers reset.")
          else:
              await ctx.send("Action Cancelled.")
        else:
          await error.embed_user_does_not_exist(ctx)


      elif arg1.lower() == "commissions" or arg1.lower() == "c" or arg1.lower() == "coms":
        if arg2.lower() == "all":
          confirm = await formatter.confirmation(ctx, bot)
          if confirm:
            user.generate_all_user_commissions()
            await ctx.send(f"{ctx.author.mention}, All commissions have been reset.")
            return
          else:
            await ctx.send("Action Cancelled.")

        mention_id = formatter.get_id_from_mention(arg2)
        if user.does_exist(mention_id):
          confirm = await formatter.confirmation(ctx, bot)
          if confirm:
            user.reset_daily_commissions(mention_id)
            await ctx.send(f"<@{mention_id}>\'s commissions reset.")
          else:
            await ctx.send("Action Cancelled.")
        else:
          await error.embed_user_does_not_exist(ctx)


      elif arg1.lower() == "level" or arg1.lower() == "l":
        mention_id = formatter.get_id_from_mention(arg2)
        if user.does_exist(mention_id):
          confirm = await formatter.confirmation(ctx, bot)
          if confirm:
              u = user.get_user(mention_id)
              member = await ctx.guild.fetch_member(str(mention_id))
              u.reset_level()
              await ctx.send(f"{member.mention}\'s adventure rank and world level have been reset.")
              database_mongo.save_user(u)
          else:
            await ctx.send("Action Cancelled.")
        else:
          await error.embed_user_does_not_exist(ctx)


#Command to delete a user's data
@bot.command(name="delete", aliases=["del"])
@commands.check(not_DM)
@commands.check(user_is_me)
@commands.check(lock_exists)
async def delete(ctx, memberMention):
    async with locks[str(ctx.author.id)]:
      mention_id = formatter.get_id_from_mention(str(memberMention))
      if user.does_exist(mention_id):
        confirm = await formatter.confirmation(ctx, bot)
        if confirm:
            database_mongo.delete_user(mention_id)
            await ctx.send(f"<@{mention_id}>\'s User data deleted")
        else:
            await ctx.send("Action Cancelled.")
      else:
        await error.embed_user_does_not_exist(ctx)

#Command to Rob people
@bot.command(name="rob")
@commands.check(not_DM)
@commands.check(user_is_me)
@commands.check(lock_exists)
async def rob(ctx, memberMention):
    async with locks[str(ctx.author.id)]:
      mention_id = formatter.get_id_from_mention(str(memberMention))
      if user.does_exist(mention_id) and user.does_exist(ctx.author.id):
        u = user.get_user(ctx.author.id)
        user_robbed = user.get_user(mention_id)
        robbedAmnt, robbed = u.rob(user_robbed)
        if robbed:
          e=discord.Embed(title=f"{user.get_user(mention_id).nickname} has been Robbed!",color=discord.Color.red())
          e.add_field(name="_ _", value=f"{u.nickname} stole **{formatter.number_format(robbedAmnt)}** Mora from your account.")
          await ctx.send(f"<@{mention_id}>",embed=e)
          database_mongo.save_user(user_robbed)
          database_mongo.save_user(u)
        else:
          await error.embed_failed_robbery(ctx)
      else:
        await error.embed_user_does_not_exist(ctx)

@bot.command(name="giftxp")
@commands.check(not_DM)
@commands.check(user_is_me)
@commands.check(lock_exists)
async def giftxp(ctx, memberMention, amnt=None):
    async with locks[str(ctx.author.id)]:
      mention_id = formatter.get_id_from_mention(str(memberMention))
      if user.does_exist(mention_id):
          exp = 10000
          if str(amnt).isdigit() and amnt != None:
              exp = int(amnt)
          u = user.get_user(mention_id)
          member = await ctx.guild.fetch_member(str(mention_id))
          await u.add_experience(exp, ctx)
          await ctx.send(f"{member.mention} has been gifted {formatter.number_format(exp)} Adventurer's Experience.")
          database_mongo.save_user(u)
      else:
          await error.embed_user_does_not_exist(ctx)

#Command to give primo
@bot.command(name="giftprimo", aliases=["giftp"])
@commands.check(not_DM)
@commands.check(user_is_me)
@commands.check(lock_exists)
async def giftp(ctx, memberMention, amnt=None):
    async with locks[str(ctx.author.id)]:
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
@commands.check(not_DM)
@commands.check(user_is_me)
@commands.check(lock_exists)
async def giftm(ctx, memberMention, amnt=None):
    async with locks[str(ctx.author.id)]:
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
@commands.check(not_DM)
@commands.check(user_already_exists)
@commands.check(lock_exists)
async def start(ctx):
    async with locks[str(ctx.author.id)]:
      user.create_user(str(ctx.author.name), ctx.author.id)
      embed = discord.Embed(title = "Starting Adventure", color = discord.Color.green())
      embed.add_field(name = "_ _", value=f"{ctx.author.mention}\'s adventure has now begun!\nDo **[{pre}help]** or **[{pre}help p]**to get the list of available commands.")
      embed.set_thumbnail(url=ctx.author.avatar_url)
      await ctx.send(ctx.author.mention, embed=embed)

@bot.command(name="server")
@commands.check(not_DM)
async def server(ctx):
  await ctx.send(f"{ctx.author.mention}, https://discord.gg//WRBbgP4q3V \nFeel free to join this server for developments or to submit suggestions.")

@bot.command(name="profile", aliases=["prof","p"])
@commands.check(not_DM)
@commands.check(user_exists)
@commands.check(lock_exists)
async def profile(ctx, arg2=None, *arg3):
    async with locks[str(ctx.author.id)]:
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
        elif arg2.lower().startswith("nickname") or arg2.lower().startswith("nick"):
          if arg3[0] != "":
            nickname = formatter.separate_commands(arg3)
            u.change_nickname(nickname[0])
          else:
            u.change_nickname(u.name)
          await ctx.send(f"{ctx.author.mention}\'s nickname has been changed.")
          database_mongo.save_user(u)
        elif arg2.lower().startswith("favorite") or arg2.lower().startswith("fav"):
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
@commands.check(not_DM)
@commands.check(user_exists)
@commands.check(lock_exists)
async def commissions(ctx):
    async with locks[str(ctx.author.id)]:
      u = user.get_user(ctx.author.id)
      await commission.show_commissions(ctx, u)

@bot.command(name="balance", aliases=["bal","b"])
@commands.check(not_DM)
@commands.check(user_exists)
@commands.check(lock_exists)
async def balance(ctx):
    async with locks[str(ctx.author.id)]:
      u = user.get_user(ctx.author.id)
      await user.embed_balance(ctx, u)

@bot.command(name="daily", aliases=["day","d"])
@commands.check(not_DM)
@commands.check(user_exists)
@commands.check(lock_exists)
async def daily(ctx):
    async with locks[str(ctx.author.id)]:
      u = user.get_user(ctx.author.id)
      await user.embed_daily(ctx, u)
      database_mongo.save_user(u)

@bot.command(name="weekly", aliases=["week"])
@commands.check(not_DM)
@commands.check(user_exists)
@commands.check(lock_exists)
async def weekly(ctx):
    async with locks[str(ctx.author.id)]:
      u = user.get_user(ctx.author.id)
      await user.embed_weekly(ctx, u)
      database_mongo.save_user(u)

@bot.command(name="wish", aliases=["w"])
@commands.check(not_DM)
@commands.check(user_exists)
@commands.check(lock_exists)
async def wish(ctx, arg=None):
  async with locks[str(ctx.author.id)]:
    if arg == "10":
      await pull.embed_ten_pull(ctx)
    else:
      await pull.embed_single_pull(ctx)
        
      

@bot.command(name="free", aliases=["f"])
@commands.check(not_DM)
@commands.check(user_exists)
@commands.check(lock_exists)
async def free(ctx, arg=None):
    u = user.get_user(ctx.author.id)
    if arg == "10":
      await pull.embed_free_ten_pull(ctx, u.nickname)
    else:
      await pull.embed_free_single_pull(ctx, u.nickname)
      

@bot.command(name="resin", aliases=["r", "res"])
@commands.check(not_DM)
@commands.check(user_exists)
@commands.check(lock_exists)
async def resin(ctx):
    u = user.get_user(ctx.author.id)
    e, f = user.embed_resin(u)
    e.set_footer(text=f"Only {get_next_resin_time()} till your next {u.get_resin_recharge()} Resin.")
    await ctx.send(embed=e, file=f)

@bot.command(name="listCharacters", aliases=["listc", "lc", "listchar"])
@commands.check(not_DM)
@commands.check(user_exists)
@commands.check(lock_exists)
async def listc(ctx, *args):
      u = user.get_user(ctx.author.id)
      pg = 1
      if len(args) > 0:
        if args[0].isdigit():
          pg = int(args[0])
          if len(args) > 1:
            mention_ID = formatter.get_id_from_mention(str(args[1]))
            if user.does_exist(mention_ID):
              u = user.get_user(mention_ID)

        elif user.does_exist(formatter.get_id_from_mention(str(args[0]))):
          u = user.get_user(formatter.get_id_from_mention(str(args[0])))
          if len(args) > 1:
            if args[1].isdigit():
              pg = int(args[1])

        else:
          #show specific character info
          name = formatter.separate_commands(args)[0].lower()
          if u.does_character_exist(name):
            await user.embed_show_char_info(ctx, u, u.characters[formatter.name_formatter(name)])
            return
          else:
            await error.embed_get_character_suggestions(ctx, u, name)
            return
      await user.embed_char_list(ctx, u, pg, bot)

@bot.command(name="listWeapons", aliases=["listw", "lw"])
@commands.check(not_DM)
@commands.check(user_exists)
@commands.check(lock_exists)
async def listw(ctx, *args):
    u = user.get_user(ctx.author.id)
    pg = 1
    if len(args) > 0:
      if args[0].isdigit():
        pg = int(args[0])
        if len(args) > 1:
          mention_ID = formatter.get_id_from_mention(str(args[1]))
          if user.does_exist(mention_ID):
            u = user.get_user(mention_ID)

      elif user.does_exist(formatter.get_id_from_mention(str(args[0]))):
        u = user.get_user(formatter.get_id_from_mention(str(args[0])))
        if len(args) > 1:
          if args[1].isdigit():
            pg = int(args[1])

      else:
        #show specific weapon info
        name = formatter.separate_commands(args)[0]
        if u.does_weapon_exist(name):
          await user.embed_show_weap_info(ctx, u, u.weapons[formatter.name_formatter(name)])
          return
        else:
          await error.embed_get_weapon_suggestions(ctx, u, name)
          return
    await user.embed_weap_list(ctx, u, pg, bot)


@bot.command(name="equip", aliases=["e", "eq"])
@commands.check(not_DM)
@commands.check(user_exists)
@commands.check(lock_exists)
async def equip(ctx, *args):
  async with locks[str(ctx.author.id)]:
      u = user.get_user(ctx.author.id)
      commands = formatter.separate_commands(args)
      if len(commands) == 2:
        characterName = formatter.split_information(commands[0])[0]
        weaponName = formatter.split_information(commands[1])[0]
        worked, reason = u.equip_weapon(characterName, weaponName)
        if not worked:
          if reason == "c":
            await error.embed_get_character_suggestions(ctx, u, characterName)
          elif reason == "i":
            await error.embed_weap_is_not_compatible(ctx)
          else:
            await error.embed_get_weapon_suggestions(ctx, u, weaponName)
        else:
          await ctx.send("Weapon has been equipped.")
          database_mongo.save_user(u)


@bot.command(name="givemora", aliases=["givem", "gm"])
@commands.check(not_DM)
@commands.check(user_exists)
@commands.check(lock_exists)
@commands.check(is_minimum_WL)
async def givem(ctx, mention, amnt):
  async with locks[str(ctx.author.id)]:
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
@commands.check(not_DM)
@commands.check(user_exists)
@commands.check(lock_exists)
@commands.check(is_minimum_WL)
async def givep(ctx, mention, amnt):
  async with locks[str(ctx.author.id)]:
      giver = user.get_user(ctx.author.id)
      taker_ID = formatter.get_id_from_mention(str(mention))
      if user.does_exist(taker_ID) and str(taker_ID) != giver._id:
        if amnt.isdigit():
          member = await ctx.guild.fetch_member(taker_ID)
          taker = user.get_user(taker_ID)
          primo = int(amnt)
          await user.embed_donate_primo(ctx, giver, taker, primo, member)
          database_mongo.save_user(giver)
          database_mongo.save_user(taker)
      else:
        await error.embed_user_does_not_exist(ctx)


@bot.command(name="condense", aliases=["con"])
@commands.check(not_DM)
@commands.check(user_exists)
@commands.check(lock_exists)
async def condense(ctx, arg=None, amount=None):
  async with locks[str(ctx.author.id)]:
      u = user.get_user(ctx.author.id)
      amnt = 1
      if arg != None:
        if arg.isdigit():
          amnt = int(arg)
        elif arg.lower().startswith("use"):
          if amount != None:
            if amount.isdigit():
              amnt = int(amount)
          await user.embed_use_condensed(ctx, u, amnt)
          database_mongo.save_user(u)
          return
      await user.embed_condensed(ctx, u, amnt)
      database_mongo.save_user(u)


@bot.command(name="adventure", aliases=["adv", "a"])
@commands.check(not_DM)
@commands.check(user_exists)
@commands.check(lock_exists)
async def _adventure(ctx, *args):
  async with locks[str(ctx.author.id)]:
    u = user.get_user(ctx.author.id)
    commands = formatter.separate_commands(args)
    charList = []
    if len(args) >= 1 and len(args) <= 2 and (args[0].lower().startswith("team") or args[0].lower().startswith("party") or (args[0].lower().startswith("t") and len(args[0]) <= 2) or (args[0].lower().startswith("p") and len(args[0]) <= 2)):
      if len(args) == 2 and args[1].isdigit():
        if int(args[1]) <= 4 and int(args[1]) > 0:
          for i in u.teams[args[1]].keys():
            charList.append(u.teams[args[1]][i])
      else:
        num = args[0][::-1][0]
        if num.isdigit():
          if int(num) <= 4 and int(num) > 0:
            for i in u.teams[num].keys():
              charList.append(u.teams[num][i])
    else:
      for i in range(len(commands)):
        charList.append(formatter.split_information(commands[i])[0].lower())
    await adventure.embed_adventure(ctx, u, charList)
    database_mongo.save_user(u)
    

@bot.command(name="trivia", aliases=["triv","t"])
@commands.check(not_DM)
@commands.check(user_exists)
@commands.check(lock_exists)
async def trivia(ctx, TID, *answer):
  async with locks[str(ctx.author.id)]:
      u = user.get_user(ctx.author.id)  
      answerString = formatter.separate_commands(answer)[0]
      await commission.answer_trivia(ctx, u, TID.upper(), answerString)
      database_mongo.save_user(u)


@bot.command(name="teams", aliases=["team", "party"])
@commands.check(not_DM)
@commands.check(user_exists)
@commands.check(lock_exists)
async def teams(ctx, arg1=None, *args):
    async with locks[str(ctx.author.id)]:
      u = user.get_user(ctx.author.id)
      if arg1 != None and arg1.isdigit():
          if int(arg1) > 0 or int(arg1) <= 4:
              if len(args) == 0:
                await user.embed_show_team(ctx, u, int(arg1))
              else:
                commands = formatter.separate_commands(args)
                charList = []
                for i in range(len(commands)):
                    charList.append(formatter.split_information(commands[i])[0].lower())
                if len(charList) > 4:
                    await error.embed_too_many_characters(ctx)
                else:
                    await user.embed_set_team(ctx, u, int(arg1), charList)
                    database_mongo.save_user(u)
      else:
          await user.embed_show_all_teams(ctx, u)


@bot.command(name="gamble", aliases=["g"])
@commands.check(not_DM)
@commands.check(user_exists)
@commands.check(lock_exists)
async def gamble(ctx, _type, amount):
  async with locks[str(ctx.author.id)]:
    typeList = ["primo", "p", "m", "mora"]
    if _type.lower() in typeList:
      if amount.isdigit():
        u = user.get_user(ctx.author.id)
        channel = bot.get_channel(int(os.getenv('JACKPOT_CHANNEL')))
        await pull.embed_gamble(ctx, u, int(amount), str(_type)[0].lower(), channel)
        database_mongo.save_user(u)
    

@bot.command(name="shop", aliases=["s"])
@commands.check(not_DM)
@commands.check(user_exists)
@commands.check(lock_exists)
@commands.check(shop_exists)
async def user_shop(ctx, _type=None):
  async with locks[str(ctx.author.id)]:
    u = user.get_user(ctx.author.id)
    if _type == None:
      await shop.embed_show_shop(ctx, u, "all")
    else:
      primo_types = ["primogems", "primo", "p", "primogem"]
      mora_types = ["mora", "m"]
      sd_types = ["stardust", "sd", "stard", "sdust"]
      sg_types = ["starglitter", "sg", "starg", "sglitter", "sglit"]
      if _type in primo_types:
        await shop.embed_show_shop(ctx, u, "p")
      elif _type in mora_types:
        await shop.embed_show_shop(ctx, u, "m")
      elif _type in sd_types:
        await shop.embed_show_shop(ctx, u, "sd")
      elif _type in sg_types:
        await shop.embed_show_shop(ctx, u, "sg")
      else:
        await shop.embed_show_shop(ctx, u, "all")

@bot.command(name="buy")
@commands.check(not_DM)
@commands.check(user_exists)
@commands.check(lock_exists)
@commands.check(shop_exists)
async def buy(ctx, name, amnt=None):
  async with locks[str(ctx.author.id)]:
    u = user.get_user(ctx.author.id)
    if amnt == None:
      await shop.shop_buy(ctx, u, name, 1)
    elif amnt.isdigit():
      await shop.shop_buy(ctx, u, name, int(amnt))

@bot.command(name="vote", aliases=["v"])
@commands.check(not_DM)
@commands.check(user_exists)
@commands.check(lock_exists)
async def vote(ctx, toggle:str=""):
  async with locks[str(ctx.author.id)]:
    u = user.get_user(ctx.author.id)
    if toggle.lower() == "toggle":
      u.vote_toggle = (not u.vote_toggle)
      if u.vote_toggle:
        await ctx.send(f"{ctx.author.mention}, Vote DM enabled.")
      else:
        await ctx.send(f"{ctx.author.mention}, Vote DM disabled.")
    else:
      await user.embed_vote(ctx, u, bot.user)
    database_mongo.save_user(u)

@bot.command(name="jackpot", aliases=["jp"])
@commands.check(not_DM)
@commands.check(user_exists)
async def jackp(ctx):
  await pull.embed_jackpot(ctx)

@bot.command(name="blackj", aliases=["bj", "blackjack"])
@commands.check(not_DM)
@commands.check(user_exists)
@commands.check(lock_exists)
async def blackj(ctx, _type, amount):
  type_list_primo = ["p", "primo", "primogems", "primogem"]
  type_list_mora = ["m", "mora"]
  async with locks[str(ctx.author.id)]:
    u = user.get_user(ctx.author.id)
    if _type.lower() in type_list_primo:
      if amount.isdigit():
        await blackjack.embed_blackjack(ctx, bot, u, int(amount), "p")
    elif _type.lower() in type_list_mora:
      if amount.isdigit():
        await blackjack.embed_blackjack(ctx, bot, u, int(amount), "m")

@bot.command(name="trade", aliases=["exchange", "ex"])
@commands.check(not_DM)
@commands.check(user_exists)
@commands.check(lock_exists)
@commands.check(is_minimum_WL)
async def trade(ctx, _type, mention):
  global locks
  responses = ["What are you doin that for? Those are the same you buffoons.", "Yea? You both think thats funny don't you. Get a life.", "Alright, I'm gettin me mallet! You'd better stop that before something happens."]
  async with locks[str(ctx.author.id)]:
    u = user.get_user(ctx.author.id)
    receiver_id = formatter.get_id_from_mention(mention)
    if user.does_exist(receiver_id) and receiver_id != u._id:
      if str(receiver_id) not in locks.keys():
        locks_copy = locks
        locks_copy[str(receiver_id)] = asyncio.Lock()
        locks = locks_copy
      async with locks[str(receiver_id)]:
        receiver = user.get_user(receiver_id)
        if receiver.world_level < 5:
          await error.embed_world_level_requirement_error(ctx, 5, receiver)
          return
        if _type == "c":
          asyncio.get_event_loop().create_task(user.embed_char_list(ctx, u, 1, bot))
          confirm, char1_name = await formatter.request_character_name(ctx, bot, u)
          if not confirm:
            await ctx.send("Trade Cancelled.")
            return
          asyncio.get_event_loop().create_task(user.embed_char_list(ctx, receiver, 1, bot))
          confirm, char2_name = await formatter.request_character_name(ctx, bot, receiver)
          if not confirm:
            await ctx.send("Trade Cancelled.")
            return
          if formatter.name_formatter(char1_name) == formatter.name_formatter(char2_name):
            await ctx.send(f"{ctx.author.mention}<@{receiver._id}>\n{responses[randint(0, len(responses)-1)]}")
            await ctx.send("Trade Cancelled.")
          else:
            await user.embed_exchange_character(ctx, bot, u, char1_name, receiver, char2_name)
        elif _type == "w":
          asyncio.get_event_loop().create_task(user.embed_weap_list(ctx, u, 1, bot))
          confirm, weap1_name = await formatter.request_weapon_name(ctx, bot, u)
          if not confirm:
            await ctx.send("Trade Cancelled.")
            return
          asyncio.get_event_loop().create_task(user.embed_weap_list(ctx, receiver, 1, bot))
          confirm, weap2_name = await formatter.request_weapon_name(ctx, bot, receiver)
          if not confirm:
            await ctx.send("Trade Cancelled.")
            return
          if formatter.name_formatter(weap1_name) == formatter.name_formatter(weap2_name):
            await ctx.send(f"{ctx.author.mention}<@{receiver._id}>\n{responses[randint(0, len(responses)-1)]}")
            await ctx.send("Trade Cancelled.")
          else:
            await user.embed_exchange_weapon(ctx, bot, u, weap1_name, receiver, weap2_name)

@bot.command(name="leaderboards", aliases=["leaderboard", "lb", "leader"])
@commands.check(user_exists)
async def leader_boards(ctx, arg1=None):
  try:
    await user.embed_leader_boards(ctx)
  except Exception as e:
    print(e)

async def embed_help_summary(ctx, command, aliases, description, usage={}):
  embed = discord.Embed(title = f"Command Summary: `{command}`", description=description, color=discord.Color.light_grey())
  SCtext = ""
  for shortcut in aliases:
    if SCtext == "":
      SCtext += f"`{shortcut}`"
    else:
      SCtext += f", `{shortcut}`"
  usage_text = ""
  for u in usage.keys():
    usage_text += f"{u}\n{usage[u]}\n"
  if SCtext != "":
    embed.add_field(name="Shortcuts", value=SCtext, inline=False)
  if usage_text != "":
    embed.add_field(name="Usage", value=usage_text,inline=False)
  embed.set_footer(text="Optional Parameters are shown in italics.")
  await ctx.send(embed=embed)

@bot.command(name="help", aliases=["h"])
async def help(ctx, arg1=None):
  embed = discord.Embed(title = "Yapa Bot Commands", color=discord.Color.greyple(), description="Use `?help command` to see more details about a particular command.")
  text = "`start`, `server`, `daily`, `weekly`, `vote`"
  embed.add_field(name="**Basic Commands**", value = text)
  text = "`adventure`"
  embed.add_field(name=":sunrise_over_mountains: **Adventure Commands**", value = text)
  text = "`resin`, `condense`"
  embed.add_field(name=":crescent_moon: **Resin Commands**", value = text)
  text = "`wish`, `free`"
  embed.add_field(name=":stars: **Wishing Commands**", value = text)
  text = "`balance`, `shop`, `buy`, `gamble`, `blackjack`, `jackpot`, `givemora`, `giveprimo`"
  embed.add_field(name=":moneybag: **Economic Commands**", value = text)
  text = "`profile`, `leaderboards`"
  embed.add_field(name=":person_bald: **Social Commands**", value = text)
  text = "`listcharacters`, `equip`, `teams`"
  embed.add_field(name=":people_wrestling: **Character Commands**", value = text)
  text = "`listweapons`"
  embed.add_field(name=":crossed_swords: **Weapon Commands**", value = text)
  text = "`commissions`, `trivia`"
  embed.add_field(name=":diamond_shape_with_a_dot_inside: **Commission Commands**", value = text)
  text = "`trade`"
  embed.add_field(name="🤝 **Trading Commands**", value = text)

  if arg1 == None:
    await ctx.message.add_reaction("📧")
    await ctx.send("**?help** will dm you commands. If you have dms disabled, use **?help p**.")
    await ctx.author.send(embed=embed)
  elif arg1.lower() == "a":
    if await user_is_me(ctx):
      embed = discord.Embed(title="Admin Commands", color=discord.Color.dark_red())
      text = f"**`{pre}update` `w, c, u, com, shop, jp, lb` `i, p, m`**\n"
      text += f"**`{pre}stats`**\n"
      text += f"**`{pre}clear` `shop_items`**\n"
      text += f"**`{pre}test` `?`**\n"
      text += f"**`{pre}reset` `level, t, com` `@user or all`**\n"
      text += f"**`{pre}delete` `@user`**\n"
      text += f"**`{pre}rob` `@user`**\n"
      text += f"**`{pre}giftxp` `@user` `amnt`**\n"
      text += f"**`{pre}giftp` `@user` `amnt`**\n"
      text += f"**`{pre}giftm` `@user` `amnt`**\n"
      embed.add_field(name="Admin Commands", value=text)
      await ctx.send(embed=embed)
  elif arg1.lower() == "p":
    await ctx.send(embed=embed)
  elif arg1.lower() == "start":
    await embed_help_summary(ctx, f"{pre}start", bot.get_command("start").aliases, "Allows you to start your Yapa Experience.")
  elif arg1.lower() == "server":
    await embed_help_summary(ctx, f"{pre}server", bot.get_command("server").aliases, "Sends the invite link to the official Yapa-Bot support server.")
  elif arg1.lower() == "daily":
    await embed_help_summary(ctx, f"{pre}daily", bot.get_command("daily").aliases, "Allows you to claim daily rewards.")
  elif arg1.lower() == "weekly":
    await embed_help_summary(ctx, f"{pre}weekly", bot.get_command("weekly").aliases, "Allows you to claim weekly rewards.")
  elif arg1.lower() == "vote":
    await embed_help_summary(ctx, f"{pre}vote", bot.get_command("vote").aliases, "Allows you to vote for the bot on top.gg and earn another daily claim.", 
    {f"`{pre}vote` `toggle`":"Allows you to toggle the vote DM confirmation."})
  elif arg1.lower() == "adventure":
    await embed_help_summary(ctx, f"{pre}adventure", bot.get_command("adventure").aliases, "Allows you to adventure with characters for experience and loot at the cost of 20 resin.",
    {f"`{pre}adventure` `char_name` *`{pre}char_name`* *`{pre}char_name`* *`{pre}char_name`*":"Allows you to go on an adventure with up to 4 of your characters. You must have atleast 1 character to adventure.",
    f"`{pre}adventure` `t#`":"Allows you to go on an adventure with a preassigned party."})
  elif arg1.lower() == "teams":
    await embed_help_summary(ctx, f"{pre}teams", bot.get_command("teams").aliases, "_ _",
    {f"`{pre}teams`":"Allows you to look at all of your teams at once.",
    f"`{pre}teams` `#`":"Allows you to look at who is in a specific team.",
    f"`{pre}teams` `#` `char_name` *`{pre}char_name`* *`{pre}char_name`* *`{pre}char_name`*":"Allows you to put up to 4 characters you own into a team.\nDoing this on an existing team will replace the team that is currently there."})
  elif arg1.lower() == "resin":
    await embed_help_summary(ctx, f"{pre}resin", bot.get_command("resin").aliases, "Allows you to look at your resin related information.")
  elif arg1.lower() == "condense":
    await embed_help_summary(ctx, f"{pre}condense", bot.get_command("condense").aliases, "_ _",
     {f"`{pre}condense` *`#`*":"Allows you to store resin in 40 resin capsules. You can only make up to 10 condensed.",
     f"`{pre}condense` `use` *`#`*":"Allows you use stored resin."})
  elif arg1.lower() == "wish":
    await embed_help_summary(ctx, f"{pre}wish", bot.get_command("wish").aliases, "_ _",
    {f"`{pre}wish` *`10`*":"Allows you to wish for your favorite genshin wishes at the cost of 160 primogems per wish."})
  elif arg1.lower() == "free":
    await embed_help_summary(ctx, f"{pre}free", bot.get_command("free").aliases, "_ _",
    {f"`{pre}free` *`10`*":"Allows you to wish for your favorite genshin wishes for free. These wishes will not be added to your collection."})
  elif arg1.lower() == "balance":
    await embed_help_summary(ctx, f"{pre}balance", bot.get_command("balance").aliases, "Allows you to look at your collected currencies.")
  elif arg1.lower() == "shop":
    await embed_help_summary(ctx, f"{pre}shop", bot.get_command("shop").aliases, "Allows you see your shop.",
    {f"`{pre}shop`":"Allows you to see your entire shop.",
    f"`{pre}shop` `p`":"Allows you to see your Primogems shop.",
    f"`{pre}shop` `m`":"Allows you to see your Mora shop.",
    f"`{pre}shop` `sd`":"Allows you to see your Stardust shop.",
    f"`{pre}shop` `sg`":"Allows you to see your StarGlitter shop.",
    })
  elif arg1.lower() == "buy":
    await embed_help_summary(ctx, f"{pre}buy", bot.get_command("buy").aliases, "_ _",
    {"`{pre}buy` `item_name` `#`":"Allows user to buy from the shop as long as they have enough of the right currency."})
  elif arg1.lower() == "gamble":
    await embed_help_summary(ctx, f"{pre}gamble", bot.get_command("gamble").aliases, "Roll all 6's to get the jackpot.",
    {"`{pre}gamble` `p` `#`":"Allows you to use your primogems to gamble in a game of dices. Must bid at least 160 primogems for a chance to earn the jackpot.",
    "`{pre}gamble` `m` `#`":"Allows you to use your mora to gamble in a game of dices. Must bid at least 10,000 mora for a chance to win the jackpot."})
  elif arg1.lower() == "blackjack":
    await embed_help_summary(ctx, f"{pre}blackjack", bot.get_command("blackjack").aliases, "Play a nice game of blackjack against Yapa. Win to double your money.",
    {"`{pre}blackjack` `p` `#`":"Allows you to bid primogems in a game of blackjack.",
    "`{pre}blackjack` `p` `#`":"Allows you to bid mora in a game of blackjack."})
  elif arg1.lower() == "jackpot":
    await embed_help_summary(ctx, f"{pre}jackpot", bot.get_command("jackpot").aliases, "Allows you to see the current total jackpots.")
  elif arg1.lower() == "givemora":
    await embed_help_summary(ctx, f"{pre}givemora", bot.get_command("givemora").aliases, "A lovely donation of mora. Must be World Level 5 or above to use.",
    {f"`{pre}givemora` `@user` `#`":"Allows you to donate mora to another user."})
  elif arg1.lower() == "giveprimo":
    await embed_help_summary(ctx, f"{pre}giveprimo", bot.get_command("giveprimo").aliases, "A lovely donation of primogems. Must be World Level 5 or above to use.",
    {f"`{pre}giveprimo` `@user` `#`":"Allows you to donate primogems to another user."})
  elif arg1.lower() == "profile":
    await embed_help_summary(ctx, f"{pre}profile", bot.get_command("profile").aliases, "_ _",
    {f"`{pre}profile` *`@user`*":"Allows you to look at your or other user data.",
    f"`{pre}profile` `favorite` `char_name`":"Allows you to set your favorite character. Character must be owned before favoriting.",
    f"`{pre}profile` `description` `desc...`":"Allows you set your profile description.",
    f"`{pre}profile` `nickname` `nick...`":"Allows you set your profile description."})
  elif arg1.lower() == "listcharacters":
    await embed_help_summary(ctx, f"{pre}listcharacters", bot.get_command("listcharacters").aliases, "_ _",
    {"`{pre}listcharacters` *`#`*":"Allows you to look at your personal character collection.",
    "`{pre}listcharacters` `char_name`":"Allows you to look at a specific character in your collection."})
  elif arg1.lower() == "equip":
    await embed_help_summary(ctx, f"{pre}equip", bot.get_command("equip").aliases, "_ _",
    {f"`{pre}equip` `char_name` `{pre}weap_name`":"Allows you to equip a weapon to a chracter. You can only equip things you own. Put none into weap_name to unequip a weapon."})
  elif arg1.lower() == "listweapons":
    await embed_help_summary(ctx, f"{pre}listweapons", bot.get_command("listweapons").aliases, "_ _",
    {"`{pre}listweapons` *`#`*":"Allows you to look at your personal weapon collection.",
    "`{pre}listweapons` `weap_name`":"Allows you to look at a specific weapon in your collection."})
  elif arg1.lower() == "commissions":
    await embed_help_summary(ctx, f"{pre}commissions", bot.get_command("commissions").aliases, "Allows you to look at your commissions and their descriptions.")
  elif arg1.lower() == "trivia":
    await embed_help_summary(ctx, f"{pre}trivia", bot.get_command("trivia").aliases, "_ _",
    {f"`{pre}trivia` `trivia_ID` `answer...`":"Allows you to answer your trivia commissions. Trivia_id can be found in the () before the name of every trivia commission."})
  elif arg1.lower() == "trade":
    await embed_help_summary(ctx, f"{pre}trade", bot.get_command("trade").aliases, "Allows trading with other users. Requires World Level 5 or higher to use.",
    {"`{pre}trade` `c` `@user`":"Allows you to trade characters with another user.",
    "`{pre}trade` `w` `@user`":"Allows you to trade weapons with another user."})
  elif arg1.lower() == "leaderboards":
    await embed_help_summary(ctx, f"{pre}leaderboards", bot.get_command("leaderboards").aliases, "Gets the top 10 players of Yapa-Bot.")
  else:
    await error.embed_command_does_not_exist(ctx)


@tasks.loop(minutes=30)
async def update_stats():
    #"""This function runs every 30 minutes to automatically update your server count."""
    try:
        await bot.dblpy.post_guild_count(shard_count=bot.shard_count)
    except Exception as e:
        print('Failed to post server count\n{}: {}'.format(type(e).__name__, e))

@bot.event
async def on_dbl_vote(data):
  #"""An event that is called whenever someone votes for the bot on top.gg."""
  if not user.does_exist(int(data["user"])):
    return
  global locks
  if str(data["user"]) not in locks.keys():
    locks_copy = locks
    locks_copy[str(data["user"])] = asyncio.Lock()
    locks = locks_copy
  async with locks[str(data["user"])]:
    toggle = True
    embed = discord.Embed(title="Voting successful!")
    text = ""
    if user.does_exist(int(data["user"])):
      u = user.get_user(int(data["user"]))
      u.primogems += 800
      u.condensed += 3
      u.mora += 10000
      toggle = u.vote_toggle
      u.update_vote()
      database_mongo.save_user(u)
      text = "<@{}> Thank you for voting for the Yapa Bot."
      embed.add_field(name="Rewards", value="**800** Primogems\n**10,000** Mora\n**3** Condensed Resin\n**12hr 1.5x** Experience Boost")
    else:
      text = "<@{}> Thank you for voting for the Yapa Bot.\nSince you have not started yet, you will not gain any rewards."
      embed.add_field(name="Rewards Would Have Been", value="**800** Primogems\n**10,000** Mora\n**3** Condensed Resin\n**12hr 1.5x*** Experience Boost")
    f = discord.File("Images/Other/Gift.png", "Gift.png")
    embed.set_thumbnail(url="attachment://Gift.png")
    embed.set_footer(text="Use ?vote toggle to disable DM confirmation.")
    if not user.does_exist(int(data["user"])) or toggle:
      fetched_user = await bot.fetch_user(int(data["user"]))
      await fetched_user.send(text.format(data["user"]), embed=embed, file=f)

@bot.event
async def on_dbl_test(data):
    #"""An event that is called whenever someone tests the webhook system for your bot on top.gg."""
    print(f"Received a test upvote:\n{data}")

if __name__ == "__main__":
  threading.Thread(target=update_counter).start()
  update_commissions_check()
  update_stats.start()
  bot.run(os.getenv('TOKEN'))