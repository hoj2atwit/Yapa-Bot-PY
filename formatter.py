import math
import discord
import prefix

def getAvatar(avamember : discord.Member=None):
  return avamember.avatar_url

def nameUnformatter(name):
  map_dict = {' ':'-', '\'':'-'}
  uFormName = ''.join(i if i not in map_dict else map_dict[i] for i in name)
  return uFormName

def nameFormatter(name):
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

def textFormatter(name):
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

def rewardListOrganizer(ar):
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

def organizeByRarity(d):
  orgAr = []
  changedItems = 0
  for i in range(6):
    for x in d.keys():
      if d[x]["rarity"] == i:
        orgAr.append(d[x])
        changedItems += 1
    if changedItems == len(d.keys()):
      break    
  return orgAr[::-1]

def getXPToNextLevel(level):
    return int(math.floor(((30 + 10**(2**(level-1))) * (2**(math.floor(level/10))))/2))

def getIDFromMention(text):
  id = ""
  for c in text:
    if c.isdigit():
      id += c
  return id

def removeExtraSpaces(command):
  for i in range(2):
    while command.startswith(" ") and len(command) > 0:
      command = command[1:]
    command = command[::-1]
  return command

def splitInformation(command):
  info = []
  text = ""
  for c in command:
    if c != prefix.commandPrefix:
      text += c
    else:
      info.append(removeExtraSpaces(text))
      text = ""
  if text != "":
    info.append(removeExtraSpaces(text))
  return info
