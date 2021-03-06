import random
import error
import discord
import formatter_custom
import commission

#allows adventuring
async def embed_adventure(ctx, u, characterList):
  if u.resin < 20:
    await error.embed_not_enough_resin(ctx)
    return

  characters = []
  for c in characterList:
    if u.does_character_exist(c):
      characters.append(u.get_character(c))
    else:
      await error.embed_get_character_suggestions(ctx, u, c)
      return
  if formatter_custom.has_identicals(characterList):
        await error.embed_dublicate_characters(ctx)
        return
  if len(characters) > 0 and len(characters) <= 4:
    moraReward = int(random.randint(500, 5000)*(int(u.world_level)+1))
    primoReward = int(random.randint(20+(5*u.world_level) ,60+(10*u.world_level)))
    can, timeLeft = u.can_vote()
    charXPReward = int(random.randint(3,6)*(1.5**u.world_level)*(1.5**(not can)))
    userXPReward = int(random.randint(8,20)*(1.5**u.world_level)*(1.5**(not can)))
    e = discord.Embed(title=f"{u.nickname}\'s Adventuring Rewards", color=discord.Color.green())
    u.mora += moraReward
    e.add_field(name="Drops", value=f"{formatter_custom.number_format(moraReward)}x Mora", inline=False)
    text = ""
    for c in characters:
      await c.add_xp(charXPReward, ctx)
      text += f"{c.name} gained **{formatter_custom.number_format(charXPReward)} exp**\n"
      u.save_character(c)
    await u.add_experience(userXPReward, ctx)
    text += f"{u.nickname} gained **{formatter_custom.number_format(userXPReward)} ARxp**\n"
    e.add_field(name="Experience", value=text, inline=False)
    u.primogems += primoReward
    e.add_field(name="Primogems", value=f"{formatter_custom.number_format(primoReward)}x Primogems", inline=False)
    u.resin -= 20
    await commission.check_target_complete(ctx, u, "adventure", 1)
    f = discord.File("Images/Other/Drops.png", "Drops.png")
    e.set_thumbnail(url="attachment://Drops.png")
    if can:
      e.set_footer(text=f"You have {formatter_custom.number_format(u.resin)} Resin left.")
    else:
      e.set_footer(text=f"???? Boost Active | You have {formatter_custom.number_format(u.resin)} Resin left.")
    await ctx.send(embed=e, file=f)
  elif len(characters) == 0:
    await error.embed_no_characters(ctx)
  else:
    await error.embed_too_many_characters(ctx)

#generateAllCommissions()
