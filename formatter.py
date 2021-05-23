import math
import discord
import prefix
import datetime
import asyncio

def get_avatar(avamember):
  return avamember.avatar_url

def name_formatter(name):
  map_dict = {' ':'-', '\'':'-'}
  uFormName = ''.join(i if i not in map_dict else map_dict[i] for i in name)
  return uFormName.lower()

def name_unformatter(name):
    currentPart = ""
    formattedName = ""
    #Iterates through name given
    for x in range(len(name)):
      #Checks if spacer Character has been run into
      if(name[x] == "-"):
        #Adds 's to formatted name text if the only character in current part is S
        if(currentPart == "S"):
          formattedName += "\'s"
          currentPart = ""
        else:
        #Adds currentPart to formattedName and adds space as long as it is not the first word found
          if(formattedName != ""):
            formattedName += " ";      
          formattedName += currentPart;
          currentPart = "";
      else:
        #Adds next character to current part
        currentPart += name[x]
        #Capitalizes first letter in new part
        if(len(currentPart) == 1):
          currentPart = currentPart.upper();
          #Adds part to name if at the end of the name.
        if(x == len(name)-1):
          if(len(currentPart) != x+1):
            formattedName += " "
          formattedName += currentPart
    return formattedName;

def text_formatter(name):
    currentPart = ""
    formattedName = ""
    #Iterates through name given
    for x in range(len(name)):
      #Checks if spacer Character has been run into
      if(name[x] == "-"):
        #Adds 's to formatted name text if the only character in current part is S
        if(currentPart == "s"):
          formattedName += "\'s"
          currentPart = ""
        else:
        #Adds currentPart to formattedName and adds space as long as it is not the first word found
          if(formattedName != ""):
            formattedName += " ";      
          formattedName += currentPart;
          currentPart = "";
      else:
        #Adds next character to current part
        currentPart += name[x]
        #Capitalizes first letter in new part
        if(len(currentPart) == 1):
          currentPart = currentPart;
          #Adds part to name if at the end of the name.
        if(x == len(name)-1):
          formattedName += " " + currentPart
    return formattedName;

def reward_list_organizer(ar):
  orgAr = []
  changedItems = 0
  for i in range(6):
    for x in ar:
      if x.rarity == i:
        orgAr.append(x)
        changedItems += 1
    if changedItems == len(ar):
      break    
  return orgAr[::-1]

def organize_by_rarity(d):
  sortedKeys = sorted(d)[::-1]
  orgAr = []
  changedItems = 0
  for i in range(6):
    for x in sortedKeys:
      if d[x]["rarity"] == i:
        orgAr.append(d[x])
        changedItems += 1
    if changedItems == len(d.keys()):
      break    
  return orgAr[::-1]

def get_xp_to_next_level(level):
    return int((30 + (100*(level-1)*(int(level/5)+1)) + (20**int(level/10)))/2)

def get_id_from_mention(text):
  _id = ""
  for c in text:
    if c.isdigit():
      _id += c
  if _id == "":
      return 0
  return int(_id)

def remove_extra_spaces(command):
  for i in range(2):
    while command.startswith(" ") and len(command) > 0:
      command = command[1:]
    command = command[::-1]
  return command

def split_information(command):
  info = []
  text = ""
  for c in command:
    if c != prefix.commandPrefix:
      text += c
    else:
      if text != "":
        info.append(remove_extra_spaces(text))
        text = ""
  if text != "":
    info.append(remove_extra_spaces(text))
  return info

def get_DateTime(timeString):
  t = []
  text = ""
  for c in timeString:
    if c.isdigit():
      text += c
    else:
      t.append(text)
      text = ""
  if t != "":
    t.append(text)
  
  return datetime.datetime(int(t[0]), int(t[1]), int(t[2]), int(t[3]), int(t[4]), int(t[5]))

def separate_commands(commandsPointer):
  commands = []
  text = ""
  for x in commandsPointer:
    if x.startswith(prefix.commandPrefix):
      if text != "":
        commands.append(remove_extra_spaces(text))
        text = x
      else:
        text = x
    else:
      if text == "":
        text += x
      else:
        text += f" {x}"
  if text != "":
    commands.append(text)
  return commands

def get_commission_ID(command):
  _id = command[:1].upper()
  for c in command[1:]:
    if c == " ":
      break
    elif c.isdigit():
      _id += c
  return _id

def number_format(num):
  numString = str(num)[::-1]
  finalString = ""
  for i in range(len(numString)):
    if (i) % 3 == 0 and i != 0:
      finalString += ","
    finalString += numString[i]
  return finalString[::-1]
    

def has_identicals(lst):
    for i in range(len(lst)):
        for x in range(len(lst) - (i+1)):
            if str(lst[i].lower()) == str(lst[x+1+i]).lower():
                return True
    return False


def get_suggestions(_dict, attempt):
  name_list = []
  for l in range(len(attempt)-1):
    for name in _dict.keys():
      if name.find(attempt[:len(attempt)-l]) != -1:
        name_list.append(_dict[name]["name"])
    if len(name_list) > 0:
      break
  if len(name_list) == 0:
    attempt_backward = attempt[::-1]
    for x in range(len(attempt)-1):
      for name in _dict.keys():
        if name[::-1].find(attempt_backward[:len(attempt_backward)-x]) != -1:
          name_list.append(_dict[name]["name"])
      if len(name_list) > 0:
        break
  if len(name_list) == 0:
    for name in _dict.keys():
      if name.startswith(attempt[:1]):
        name_list.append(_dict[name]["name"])

  name_list_string = ""
  for i in range(len(name_list)):
    if name_list_string == "":
      name_list_string += f"**[{name_list[i]}]**"
    elif i == len(name_list)-1:
      name_list_string += f" or **[{name_list[i]}]**"
    else:
      name_list_string += f", **[{name_list[i]}]**"
  return name_list_string

async def pages(ctx, bot, embedList):
  pages = await ctx.send(embed=embedList[0])
  cur_index = 0
  await pages.add_reaction("◀️")
  await pages.add_reaction("▶️")
  def check(reaction, user):
        return str(reaction.emoji) in ["◀️", "▶️"] and reaction.message == pages and (not user.bot)
  while True:
        try:
            reaction, user = await bot.wait_for("reaction_add", timeout=30, check=check)

            if str(reaction.emoji) == "▶️":
                cur_index += 1
                if cur_index >= len(embedList):
                    cur_index = 0
                await pages.edit(embed=embedList[cur_index])
                await pages.remove_reaction(reaction, user)

            elif str(reaction.emoji) == "◀️":
                cur_index -= 1
                if cur_index < 0:
                    cur_index = len(embedList)-1
                await pages.edit(embed=embedList[cur_index])
                await pages.remove_reaction(reaction, user)

            else:
                await pages.remove_reaction(reaction, user)
        except asyncio.TimeoutError:
            break

async def confirmation(ctx, bot):
  await ctx.send(f"{ctx.author.mention}, Are you sure you want to do this?(y/n)")
  def check(response):
        confirmation = ["yes","no","y","n"]
        return response.author == ctx.author and str(response.content.lower()) in confirmation
  while True:
        try:
            response = await bot.wait_for(event = 'message', timeout=30, check=check)

            if str(response.content.lower()) == "yes" or str(response.content.lower()) == "y":
                return True

            elif str(response.content.lower()) == "no" or str(response.content.lower()) == "n":
                return False
        except asyncio.TimeoutError:
            await ctx.send("Response timeout.")
            return False

def strike(text):
    result = ''
    for c in text:
        result = result + '\u0336' + c
    return result

class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'