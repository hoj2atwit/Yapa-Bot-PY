import discord
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
from datetime import datetime, timedelta

tz = pytz.timezone("America/New_York")
pre = prefix.commandPrefix
load_dotenv()



bot = commands.Bot(f"{pre}", case_insensitive=True)
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

def not_DM(ctx):
    return ctx.author.guild != None

def user_already_exists(ctx):
  return not user.does_exist(ctx.author.id)

def user_is_me(ctx):
  return str(ctx.author.id) == os.getenv('OWNER_ID')

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
            await updater.update_all_characters_DB(ctx)
            await ctx.send(f"{ctx.author.mention}, New character data downloaded.")
          elif arg2.lower() == "i":
            await ctx.send(f"{ctx.author.mention}, Searching for new character images.")
            await updater.get_all_character_images_API(ctx)
            await ctx.send(f"{ctx.author.mention}, New character images have been downloaded.")
            
        elif arg1.lower() == "w":
          if arg2 == None:
            await ctx.send(f"{ctx.author.mention}, Searching for new weapon data.")
            await updater.update_weapons_DB(ctx)
            await ctx.send(f"{ctx.author.mention}, New weapon data downloaded.")
          elif arg2.lower() == "i":
            await ctx.send(f"{ctx.author.mention}, Searching for new weapon images.")
            await updater.get_all_weap_images_API(ctx)
            await ctx.send(f"{ctx.author.mention}, Weapon images have been downloaded.")
            
        elif arg1.lower() == "u":
          await ctx.send(f"{ctx.author.mention}, Updating All Users.")
          user.update_users()
          await ctx.send(f"{ctx.author.mention}, All users have been updated.")
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

@bot.command(name="test")
@commands.check(not_DM)
@commands.check(user_is_me)
@commands.check(lock_exists)
async def test(ctx):
    async with locks[str(ctx.author.id)]:
      confirm = await formatter.confirmation(ctx, bot)
      if confirm:
          await ctx.send("Confirmed!")
      else:
          await ctx.send("Denied!")

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

@bot.command(name="listCharacter", aliases=["listc", "lc", "listchar"])
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

@bot.command(name="listWeapon", aliases=["listw", "lw"])
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
        await pull.embed_gamble(ctx, u, int(amount), str(_type)[0].lower())
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
async def vote(ctx):
  async with locks[str(ctx.author.id)]:
    u = user.get_user(ctx.author.id)
    await user.embed_vote(ctx, u)
    database_mongo.save_user(u)

@bot.command(name="help", aliases=["h"])
@commands.check(not_DM)
async def help(ctx,arg1=None):
  embedList = []
  embed = discord.Embed(title = "Yapa Bot Commands 1", color=discord.Color.dark_red())
  text = f"**[{pre}start]** Allows you to start your Yappa Experience.\n"
  text += f"**[{pre}daily]** Allows you to claim daily rewards.\n"
  text += f"**[{pre}weekly]** Allows you to claim weekly rewards.\n"
  text += f"**[{pre}adventure] | [char_name] | [{pre}cn {pre}cn {pre}cn]** Allows you to go on an adventure with up to 4 of your characters at the cost of 20 resin. You must have atleast 1 character to adventure.\n"
  text += f"**[{pre}resin]** Allows you to look at your current resin.\n"
  text += f"**[{pre}condense] | [amnt#]** Allows you to store resin in 40 resin capsules. You can only store up to 10 condensed.\n"
  text += f"**[{pre}condense use] | [amnt#]** Allows you use stored resin.\n"
  text += f"**[{pre}listw] | [pg# or weap_name]** Allows you to look at your personal weapon collection.\n_ _\n_ _"
  embed.add_field(name="Basic Commands", value = text, inline=False)


  text = f"**[{pre}wish] | [10]** Allows you to pull for your favorite genshin wishes at the cost of 160 primogems per wish.\n"
  text += f"**[{pre}free] | [10]** Allows you to pull for your favorite genshin wishes for free. These wishes will not be added to your collection.\n_ _\n_ _"
  embed.add_field(name="Wishing Commands", value = text, inline=False)


  text = f"**[{pre}balance]** Allows you to look at your collected currencies.\n"
  text += f"**[{pre}givem] | [amnt#] | [@user]** Allows you to donate mora to another user.\n"
  text += f"**[{pre}givep] | [amnt#] | [@user]** Allows you to donate primogems to another user.\n_ _\n_ _"
  embed.add_field(name="Economic Commands", value = text, inline=False)


  text = f"**[{pre}listc] | [pg# or char_name]** Allows you to look at your personal character collection.\n"
  text += f"**[{pre}teams]** Allows you to look at all of your teams.\n"
  text += f"**[{pre}teams] | [team #]** Allows you to look at who is in a specific team.\n"
  text += f"**[{pre}teams] | [team #] | [char_name ?char_name ?char_name ?char_name]** Allows you to put up to 4 characters you own into their own party.\n"
  text += f"**[{pre}equip] | [char_name] | [{pre}weap_name, {pre}none]** Allows you to equip a weapon to a chracter. You can only equip things you own.\n_ _\n_ _"
  embed.add_field(name="Character Commands", value = text, inline=False)


  text = f"**[{pre}profile] | [@user]** Allows you to look at your or other user data.\n"
  text += f"**[{pre}profile] | [favorite] | [char_name]** Allows you to set your favorite character. Character must be owned before favoriting.\n"
  text += f"**[{pre}profile] | [description] | [desc...]** Allows you set your profile description.\n"
  text += f"**[{pre}profile] | [nickname] | [nick...]** Allows you set your profile description."
  embed.add_field(name="Profile Commands", value = text, inline=False)


  embed.set_footer(text=f"Page 1/2")
  embedList.append(embed)


  embed = discord.Embed(title = "Yapa Bot Commands 2", color=discord.Color.dark_red())
  text = f"**[{pre}commission]** Allows you to look at your commissions and their descriptions.\n"
  text += f"**[{pre}trivia] | [triviaID] | [answer]** Allows you to answer your trivia commissions. Trivia id can be found in the () before every trivia commission."
  embed.add_field(name="Commission Commands", value = text, inline=False)

  text = f"**[{pre}gamble] | [primo or mora] | [amount]** Allows you to use your mora or primogems to gamble, having a chance to win x2 or even x10 of waht you put it.\n"
  embed.add_field(name="Gambling Commands", value = text, inline=False)

  text = f"**[{pre}shop] | [p, m, sg, sd]** Allows user to see their shop.\n"
  text += f"**[{pre}buy] | [item_name] | [amount]** Allows user to buy from the shop as long as they have enough of the right currency.\n"
  embed.add_field(name="Shop Commands", value = text, inline=False)

  embed.set_footer(text=f"Page 2/2")
  embedList.append(embed)

  if arg1 == "p":
    await formatter.pages(ctx, bot, embedList)
  else:
      await ctx.message.add_reaction("📧")
      for e in embedList:
        await ctx.author.send(embed=e)

@tasks.loop(minutes=30)
async def update_stats():
    #"""This function runs every 30 minutes to automatically update your server count."""
    try:
        await bot.dblpy.post_guild_count()
        print(f'Posted server count ({bot.dblpy.guild_count})')
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
    u = user.get_user(int(data["user"]))
    u.primogems += 800
    u.condensed += 3
    u.mora += 10000
    u.update_vote()
    database_mongo.save_user(u)

@bot.event
async def on_dbl_test(data):
    #"""An event that is called whenever someone tests the webhook system for your bot on top.gg."""
    print(f"Received a test upvote:\n{data}")

if __name__ == "__main__":
  threading.Thread(target=update_counter).start()
  update_commissions_check()
  update_stats.start()
  bot.run(os.getenv('TOKEN'))