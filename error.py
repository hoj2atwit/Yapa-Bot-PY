from user import User
import discord
import formatter

async def embed_not_enough_primo(ctx):
  embed = discord.Embed(color=discord.Color.red())
  embed.add_field(name = "Low Balance", value = "Not Enough Primogems")
  await ctx.send(ctx.author.mention, embed=embed)

async def embed_not_enough_mora(ctx):
  embed = discord.Embed(color=discord.Color.red())
  embed.add_field(name = "Low Balance", value = "Not Enough Mora")
  await ctx.send(ctx.author.mention, embed=embed)

async def embed_not_enough_star_glitter(ctx):
  embed = discord.Embed(color=discord.Color.red())
  embed.add_field(name = "Low Balance", value = "Not Enough Star Glitter")
  await ctx.send(ctx.author.mention, embed=embed)

async def embed_not_enough_star_dust(ctx):
  embed = discord.Embed(color=discord.Color.red())
  embed.add_field(name = "Low Balance", value = "Not Enough Star Dust")
  await ctx.send(ctx.author.mention, embed=embed)

async def embed_char_is_not_owned(ctx, name):
  embed = discord.Embed(color=discord.Color.red())
  embed.add_field(name = "Character not found", value = f"A character with the name **[{name}]** could not be found in your collection.")
  await ctx.send(ctx.author.mention, embed=embed)

async def embed_char_does_not_exist(ctx):
  embed = discord.Embed(color=discord.Color.red())
  embed.add_field(name = "Character not found", value = "This character does not exist.")
  await ctx.send(ctx.author.mention, embed=embed)

async def embed_weap_is_not_owned(ctx, name):
  embed = discord.Embed(color=discord.Color.red())
  embed.add_field(name = "Weapon not found", value = f"A weapon with the name **[{name}]** could not be found in your collection.")
  await ctx.send(ctx.author.mention, embed=embed)

async def embed_weap_is_not_compatible(ctx):
  embed = discord.Embed(color=discord.Color.red())
  embed.add_field(name = "Incompatible", value = "That weapon is incompatible.")
  await ctx.send(ctx.author.mention, embed=embed)

async def embed_weap_does_not_exist(ctx):
  embed = discord.Embed(color=discord.Color.red())
  embed.add_field(name = "Character not found", value = "This weapon does not exist.")
  await ctx.send(ctx.author.mention, embed=embed)

async def embed_art_is_not_owned(ctx):
  embed = discord.Embed(color=discord.Color.red())
  embed.add_field(name = "Artifact not found", value = "You do not own this artifact or this artifact does not exist.")
  await ctx.send(ctx.author.mention, embed=embed)

async def embed_art_does_not_exist(ctx):
  embed = discord.Embed(color=discord.Color.red())
  embed.add_field(name = "Artifact not found", value = "This artifact does not exist.")
  await ctx.send(ctx.author.mention, embed=embed)

async def embed_user_does_not_exist(ctx):
  embed = discord.Embed(color=discord.Color.red())
  embed.add_field(name = "User not found", value = "This User does not exist or has not begun their adventure.")
  await ctx.send(ctx.author.mention, embed=embed)

async def embed_failed_robbery(ctx):
  embed = discord.Embed(color=discord.Color.red())
  embed.add_field(name = "Mora not found", value = "This User does not have enough mora to steal.")
  await ctx.send(ctx.author.mention, embed=embed)

async def embed_failed_donation_mora(ctx):
  embed = discord.Embed(color=discord.Color.red())
  embed.add_field(name = "Mora not found", value = "This User does not have enough mora to give away.")
  await ctx.send(ctx.author.mention, embed=embed)

async def embed_failed_donation_mora_tax(ctx):
  embed = discord.Embed(color=discord.Color.red())
  embed.add_field(name = "Donation Error", value = "You did not give the minimum amount of mora to cover transfer tax. (1000 Mora)")
  await ctx.send(ctx.author.mention, embed=embed)

async def embed_failed_donation_primo(ctx):
  embed = discord.Embed(color=discord.Color.red())
  embed.add_field(name = "Primo not found", value = "This User does not have enough primogems to give away.")
  await ctx.send(ctx.author.mention, embed=embed)

async def embed_failed_donation_primo_tax(ctx):
  embed = discord.Embed(color=discord.Color.red())
  embed.add_field(name = "Donation Error", value = "You did not give the minimum amount of primogems to cover transfer tax. (100 Primo)")
  await ctx.send(ctx.author.mention, embed=embed)

async def embed_long_description(ctx, length):
  embed = discord.Embed(color=discord.Color.red())
  embed.add_field(name = "Too Long", value = f"Your Description was too long.\nInputed Length: **{formatter.number_format(length)}**\nExpected Length: **400**")
  await ctx.send(ctx.author.mention, embed=embed)

async def embed_too_early(ctx, waitTime):
  embed = discord.Embed(color=discord.Color.red())
  embed.add_field(name = "Too Early", value = f"You cannot use that command for **{waitTime}**.")
  await ctx.send(ctx.author.mention, embed=embed)

async def embed_not_enough_resin(ctx):
  embed = discord.Embed(color=discord.Color.red())
  embed.add_field(name = "Resin Not Found", value = "You do not have sufficient Resin.")
  await ctx.send(ctx.author.mention, embed=embed)

async def embed_not_enough_condensed(ctx):
  embed = discord.Embed(color=discord.Color.red())
  embed.add_field(name = "Resin Not Found", value = "You do not have sufficient Condensed Resin.")
  await ctx.send(ctx.author.mention, embed=embed)

async def embed_too_many_characters(ctx):
  embed = discord.Embed(color=discord.Color.red())
  embed.add_field(name = "Character Error", value = "You have given too many characters.")
  await ctx.send(ctx.author.mention, embed=embed)

async def embed_no_characters(ctx):
  embed = discord.Embed(color=discord.Color.red())
  embed.add_field(name = "Character Error", value = "You have given no characters.")
  await ctx.send(ctx.author.mention, embed=embed)

async def embed_wrong_answer(ctx):
  embed = discord.Embed(color=discord.Color.red())
  embed.add_field(name = "Answer Error", value = "Your answer is incorrect.")
  await ctx.send(ctx.author.mention, embed=embed)

async def embed_too_much_condensed(ctx):
  embed = discord.Embed(color=discord.Color.red())
  embed.add_field(name = "Maximum Hit", value = "You already have 10 or more condensed resin.")
  await ctx.send(ctx.author.mention, embed=embed)

async def embed_get_character_suggestions(ctx, u, attempt):
  name_list_string = formatter.get_suggestions(u.characters, attempt)
  if name_list_string != "":
    embed = discord.Embed()
    embed.add_field(name="Suggestions", value=f"Did you mean: {name_list_string}?")
    await ctx.send(f"<@{u._id}>", embed=embed)
  else:
    await embed_char_is_not_owned(ctx, attempt)

async def embed_get_weapon_suggestions(ctx, u, attempt):
  name_list_string = formatter.get_suggestions(u.weapons, attempt)
  if name_list_string != "":
    embed = discord.Embed()
    embed.add_field(name="Suggestions", value=f"Did you mean: {name_list_string}?")
    await ctx.send(f"<@{u._id}>", embed=embed)
  else:
    await embed_weap_is_not_owned(ctx, attempt)

async def embed_world_level_requirement_error(ctx, requirement, u=None):
  embed = discord.Embed(color=discord.Color.red())
  if u == None:
    embed.add_field(name = "World Level Error", value = f"You do not meet the required world level.\n**World Level {requirement} is required.**")
  else:
    embed.add_field(name = "World Level Error", value = f"{u.nickname} does not meet the required world level.\n**World Level {requirement} is required.**")
  await ctx.send(ctx.author.mention, embed=embed)

async def embed_dublicate_characters(ctx):
  embed = discord.Embed()
  embed.add_field(name="Character Error", value="You cannot input the same character multiple times.")
  await ctx.send(ctx.author.mention, embed=embed)

async def embed_unknown_item(ctx, name):
  embed = discord.Embed()
  embed.add_field(name="Item Error", value=f"Item could not be found \"{name}\".")
  await ctx.send(ctx.author.mention, embed=embed)

async def embed_not_enough_items_to_purchase(ctx, item_name):
  embed = discord.Embed()
  embed.add_field(name="Shop Error", value=f"There is not enough {item_name} in stock.")
  await ctx.send(ctx.author.mention, embed=embed)

async def embed_out_of_stock(ctx):
  embed = discord.Embed()
  embed.add_field(name="Shop Error", value="That item is out of stock.")
  await ctx.send(ctx.author.mention, embed=embed)

async def embed_command_does_not_exist(ctx):
  embed = discord.Embed()
  embed.add_field(name="Command Error", value="Command does not exist.")
  await ctx.send(ctx.author.mention, embed=embed)