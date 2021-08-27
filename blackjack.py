import discord
import formatter_custom
import error
import database_mongo
import card
import asyncio
import commission

def check_21(hand):
  total = 0
  aces = 0
  for c in hand:
    val = c[:len(c)-2]
    if val.isdigit():
      total += int(val)
    else:
      if val == "J" or val == "Q" or val == "K":
        total += 10
      else:
        aces += 1
  for i in range(aces):
    if total + 11 > 21:
      total += 1
    else:
      if aces - (i+1) > 0 and total + 11 == 21:
        total += 1
      else:
        total += 11

  if total == 21:
    return True, total
  else:
    return False, total

def embed_create_blackjack(u, bot_hand, player_hand):
  embed = discord.Embed(title=f"{u.nickname}'s BlackJack Game")
  text = ""
  for c in bot_hand:
    if text == "":
      text += f"{c}"
    else:
      text += f", ⬜"
  embed.add_field(name="Yapa's Hand", value = text, inline=False)
  text = ""
  for c in player_hand:
    if text == "":
      text += f"{c}"
    else:
      text += f", {c}"
  check, total = check_21(player_hand)
  embed.add_field(name=f"{u.nickname}'s Hand -> {total}", value = text, inline=False)
  return embed

async def embed_create_blackjack_final(ctx, u, bot_hand, player_hand, winner, amount, _type):
  if _type == "p":
    u.primogems -= amount
  else:
    u.mora -= amount
  if winner == "u":
    embed = discord.Embed(title=f"{u.nickname}'s BlackJack Game", color=discord.Color.green())
    text = ""
    if _type == "p":
      u.primogems += amount*2
      text = f"You won {formatter_custom.number_format(amount*2)}x Primogems"
    else:
      u.mora += amount*2
      text = f"You won {formatter_custom.number_format(amount*2)}x Mora"
    embed.add_field(name="You Won!", value=text)
  elif winner == "b":
    embed = discord.Embed(title=f"{u.nickname}'s BlackJack Game")
    embed.add_field(name="It was a tie.", value="You got your money back.")
    if _type == "p":
      u.primogems += amount
    else:
      u.mora += amount
  else:
    embed = discord.Embed(title=f"{u.nickname}'s BlackJack Game", color=discord.Color.red())
    if _type == "p":
      text = f"You lost {formatter_custom.number_format(amount)}x Primogems"
      database_mongo.add_to_jackpot_primo(amount)
    else:
      text = f"You lost {formatter_custom.number_format(amount)}x Mora"
      database_mongo.add_to_jackpot_mora(amount)
    embed.add_field(name="You lost.", value=text)
  await commission.check_target_complete(ctx, u, "gamble", 1)
  database_mongo.save_user(u)
  text = ""
  for c in bot_hand:
    if text == "":
      text += f"{c}"
    else:
      text += f", {c}"
  check, total = check_21(bot_hand)
  embed.add_field(name=f"Yapa's Final Hand -> {total}", value = text, inline=False)
  text = ""
  for c in player_hand:
    if text == "":
      text += f"{c}"
    else:
      text += f", {c}"
  check, total = check_21(player_hand)
  embed.add_field(name=f"{u.nickname}'s Final Hand -> {total}", value = text, inline=False)
  return embed  

def bot_decision(hand, deck):
  check, total = check_21(hand)
  if total < 17 and not check and len(hand) < 5:
    hand.append(deck.pop())
    return True
  else:
    return False

def check_winner(user_win, bot_win, user_total, bot_total):
  if bot_win and user_win:
    return "b"
  elif user_win:
    return "u"
  elif bot_win:
    return "y"
  else:
    if user_total >= 21 or bot_total >= 21:
      if user_total > 21 and bot_total > 21:
        return "b"
      elif user_total > 21 and bot_total <= 21:
        return "y"
      elif bot_total > 21 and user_total <= 21:
        return "u"
    else:
      if user_total > bot_total:
        return "u"
      elif bot_total > user_total:
        return "y"
      else:
        return "b"

async def embed_blackjack(ctx, bot, u, amount, _type):
  if _type == "p":
    if u.primogems < amount:
      await error.embed_not_enough_primo(ctx)
      return
  else:
    if u.mora < amount:
      await error.embed_not_enough_mora(ctx)
      return
  deck = card.make_deck()
  card.shuffle(deck)
  card.shuffle(deck)
  card.shuffle(deck)
  bot_hand = []
  player_hand = []

  bot_hand.append(deck.pop())
  bot_hand.append(deck.pop())
  player_hand.append(deck.pop())
  player_hand.append(deck.pop())

  game = await ctx.send(embed=embed_create_blackjack(u, bot_hand, player_hand))

  rea_hit = await game.add_reaction("💥")
  rea_stay = await game.add_reaction("🤚")

  def check(reaction, user):
        return str(reaction.emoji) in ["💥", "🤚"] and reaction.message == game and user == ctx.author

  while True:
    try:
        reaction, user = await bot.wait_for("reaction_add", timeout=30, check=check)
        if str(reaction.emoji) == "💥":
          player_hand.append(deck.pop())
          win, total = check_21(player_hand)
          if win or (total < 21 and len(player_hand) == 5):
            bot_go = True
            while bot_go:
              bot_go = bot_decision(bot_hand, deck)
            bot_win, bot_total = check_21(bot_hand)
            
            if bot_win or (bot_total < 21 and len(bot_hand) == 5):
              await game.edit(embed=await embed_create_blackjack_final(ctx, u, bot_hand, player_hand, "b", amount, _type))
            else:
              await game.edit(embed=await embed_create_blackjack_final(ctx, u, bot_hand, player_hand, "u", amount, _type))

            await game.clear_reactions()
            break
          elif total > 21:
            await game.edit(embed=await embed_create_blackjack_final(ctx, u, bot_hand, player_hand, "y", amount, _type))
            await game.clear_reactions()
            break
          else:
            bot_go = bot_decision(bot_hand, deck)
            await game.edit(embed=embed_create_blackjack(u, bot_hand, player_hand))
            await game.remove_reaction(reaction, user)
        elif str(reaction.emoji) == "🤚":
          win, total = check_21(player_hand)
          bot_go = True
          while bot_go:
            bot_go = bot_decision(bot_hand, deck)
          bot_win, bot_total = check_21(bot_hand)
          
          await game.edit(embed=await embed_create_blackjack_final(ctx, u, bot_hand, player_hand, check_winner(win, bot_win, total, bot_total), amount, _type))
          
          await game.clear_reactions()
          break
        else:
          await game.remove_reaction(reaction, user)
    except asyncio.TimeoutError:
        await ctx.send(f"{ctx.author.mention}, You took too long, Now the game is cancelled.")
        tax_amount = 0
        if _type == "p":
          if amount < 160:
            tax_amount = amount//2
          else:
            tax_amount = amount//5
          u.primogems -= tax_amount
          database_mongo.add_to_jackpot_primo(tax_amount)
          await ctx.send(f"{ctx.author.mention}, {formatter_custom.number_format(tax_amount)} Primogems has been taxed to prevent abuse.")
        else:
          if amount < 10000:
            tax_amount = amount//2
          else:
            tax_amount = amount//5
          u.mora -= tax_amount
          database_mongo.add_to_jackpot_mora(tax_amount)
          await ctx.send(f"{ctx.author.mention}, {formatter_custom.number_format(tax_amount)} Mora has been taxed to prevent abuse.")
        database_mongo.save_user(u)
        await game.clear_reactions()
        break