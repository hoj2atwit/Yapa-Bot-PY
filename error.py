import discord

def embedNotEnoughPrimo():
  embed = discord.Embed(color=discord.Color.red())
  embed.add_field(name = "Low Balance", value = "Not Enough Primogems")
  return embed
def embedNotEnoughMora():
  embed = discord.Embed(color=discord.Color.red())
  embed.add_field(name = "Low Balance", value = "Not Enough Mora")
  return embed
def embedNotEnoughStarGlitter():
  embed = discord.Embed(color=discord.Color.red())
  embed.add_field(name = "Low Balance", value = "Not Enough Star Glitter")
  return embed
def embedNotEnoughStarDust():
  embed = discord.Embed(color=discord.Color.red())
  embed.add_field(name = "Low Balance", value = "Not Enough Star Dust")
  return embed
def embedCharIsNotOwned():
  embed = discord.Embed(color=discord.Color.red())
  embed.add_field(name = "Character not found", value = "You do not own this character or this character does not exist.")
  return embed
def embedCharDoesNotExist():
  embed = discord.Embed(color=discord.Color.red())
  embed.add_field(name = "Character not found", value = "This character does not exist.")
  return embed
def embedWeapIsNotOwned():
  embed = discord.Embed(color=discord.Color.red())
  embed.add_field(name = "Weapon not found", value = "You do not own this weapon or this weapon does not exist.")
  return embed
def embedWeapDoesNotExist():
  embed = discord.Embed(color=discord.Color.red())
  embed.add_field(name = "Character not found", value = "This weapon does not exist.")
  return embed
def embedArtIsNotOwned():
  embed = discord.Embed(color=discord.Color.red())
  embed.add_field(name = "Artifact not found", value = "You do not own this artifact or this artifact does not exist.")
  return embed
def embedArtDoesNotExist():
  embed = discord.Embed(color=discord.Color.red())
  embed.add_field(name = "Artifact not found", value = "This artifact does not exist.")
  return embed
def embedUserDoesNotExist():
  embed = discord.Embed(color=discord.Color.red())
  embed.add_field(name = "User not found", value = "This User does not exist or has not begun their adventure.")
  return embed