import discord
import formatter
import error
import database_mongo
import random
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
        total += 11
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

  if total != 21:
    return False, total
  else:
    return True, total

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
      text = f"You won {formatter.number_format(amount*2)}x Primogems"
    else:
      u.mora += amount*2
      text = f"You won {formatter.number_format(amount*2)}x Mora"
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
      text = f"You lost {formatter.number_format(amount)}x Primogems"
      database_mongo.add_to_jackpot_primo(amount)
    else:
      text = f"You lost {formatter.number_format(amount)}x Mora"
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

def make_deck():
  deck = []
  for i in range(4):
    suit = ""
    if i == 0:
      suit = "♦️"
    elif i == 1:
      suit = "♣️"
    elif i == 2:
      suit = "♥️"
    else:
      suit = "♠️"
    for x in range(13):
      num = ""
      if x == 0:
        num = "A"
      elif x == 10:
        num = "J"
      elif x == 11:
        num = "Q"
      elif x == 12:
        num = "K"
      else:
        num = f"{x+1}"
      
      deck.append(f"{num}{suit}")
  return deck

def shuffle(deck):
  for i in range(len(deck)-1, 0, -1):
      
    # Pick a random index from 0 to i 
    j = random.randint(0, i + 1) 
    
    # Swap arr[i] with the element at random index 
    deck[i], deck[j] = deck[j], deck[i] 
    
async def embed_blackjack(ctx, bot, u, amount, _type):
  if _type == "p":
    if u.primogems < amount:
      await error.embed_not_enough_primo(ctx)
      return
  else:
    if u.mora < amount:
      await error.embed_not_enough_mora(ctx)
      return
  deck = make_deck()
  shuffle(deck)
  shuffle(deck)
  shuffle(deck)
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
            player_hand.append(deck.pop())
            bot_go = bot_decision(bot_hand, deck)
            await game.edit(embed=embed_create_blackjack(u, bot_hand, player_hand))
            await game.remove_reaction(reaction, user)
        elif str(reaction.emoji) == "🤚":
          win, total = check_21(player_hand)
          bot_go = True
          while bot_go:
            bot_go = bot_decision(bot_hand, deck)
          bot_win, bot_total = check_21(bot_hand)

          if bot_win and win:
            await game.edit(embed=await embed_create_blackjack_final(ctx, u, bot_hand, player_hand, "b", amount, _type))
          elif win:
            await game.edit(embed=await embed_create_blackjack_final(ctx, u, bot_hand, player_hand, "u", amount, _type))
          elif bot_win:
            await game.edit(embed=await embed_create_blackjack_final(ctx, u, bot_hand, player_hand, "y", amount, _type))
          else:
            if total > 21 or bot_total > 21:
              if total > 21 and bot_total > 21:
                await game.edit(embed=await embed_create_blackjack_final(ctx, u, bot_hand, player_hand, "b", amount, _type))
              elif total > 21 and bot_total <= 21:
                await game.edit(embed=await embed_create_blackjack_final(ctx, u, bot_hand, player_hand, "y", amount, _type))
              elif bot_total > 21 and total <= 21:
                await game.edit(embed=await embed_create_blackjack_final(ctx, u, bot_hand, player_hand, "u", amount, _type))
            else:
              if total > bot_total:
                await game.edit(embed=await embed_create_blackjack_final(ctx, u, bot_hand, player_hand, "u", amount, _type))
              elif bot_total > total:
                await game.edit(embed=await embed_create_blackjack_final(ctx, u, bot_hand, player_hand, "y", amount, _type))

          await game.clear_reactions()
          break
        else:
          await game.remove_reaction(reaction, user)
    except asyncio.TimeoutError:
        await ctx.send(f"{ctx.author.mention}, You took too long, Now the game is cancelled.")
        await game.clear_reactions()
        break