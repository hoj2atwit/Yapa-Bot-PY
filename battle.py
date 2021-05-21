import discord
import asyncio

async def battle(ctx, bot, chars, enemies):
  battle_screen = await ctx.send()
  rock_emoji = "🪨"
  paper_emoji = "◻️"
  scissor_emoji = "✂️"
  await battle_screen.add_reaction(rock_emoji)
  await battle_screen.add_reaction(paper_emoji)
  await battle_screen.add_reaction(scissor_emoji)
  def check(reaction, user):
        return str(reaction.emoji) in [rock_emoji, paper_emoji, scissor_emoji] and reaction.message == battle_screen and (user.id == ctx.author.id)
  while True:
        try:
            reaction, user = await bot.wait_for("reaction_add", timeout=30, check=check)

            if str(reaction.emoji) == rock_emoji:
              await battle_screen.remove_reaction(reaction, user)
            elif str(reaction.emoji) == paper_emoji:
              await battle_screen.remove_reaction(reaction, user)
            elif str(reaction.emoji) == scissor_emoji:
              await battle_screen.remove_reaction(reaction, user)
            else:
              await battle_screen.remove_reaction(reaction, user)
        except asyncio.TimeoutError:
            break