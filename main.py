import discord
import os
import user
import pull
import asyncio
import error
import prefix
import formatter
from keep_alive import keep_alive

fiveStarWishGifSingle = "Images/Gifs/SingleFiveStar.gif"
fourStarWishGifSingle = "Images/Gifs/SingleThreeStar.gif"
threeStarWishGifSingle = "Images/Gifs/SingleThreeStar.gif"
fiveStarWishGifTen = "Images/Gifs/TenFiveStar.gif"
fourStarWishGifTen = "Images/Gifs/TenFourStar.gif"


pre = prefix.commandPrefix
client = discord.Client()

@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
  if message.author == client.user:
    return
  
  #Commands for OWNER OF BOT ONLY
  if str(message.author.id) == os.getenv('OWNER_ID'):
    if message.content.lower().startswith(pre):
      command = message.content[len(pre):]

      #Clear All User Data
      if command.lower().startswith("clear"):
        user.clearUserData()
        await message.channel.send("All User Data Cleared")
        return

      #Delete User
      elif command.lower().startswith("delete"):
        if len(command) > 7:
          command = command[7:]
          id = formatter.getIDFromMention(command)
          if user.doesExist(id):
            user.deleteUser(id)
            await message.channel.send(f"<@{id}>\'s User data deleted")
            return
          else:
            e = error.embedUserDoesNotExist()
            await message.channel.send(embed=e)
            return

      #Give Primo for Free
      elif command.lower().startswith("giftp"):
        u = user.getUser(str(message.author.id))
        member = await message.channel.guild.fetch_member(message.author.id)
        amnt  = 16000
        if len(command) > 6:
            command = command[6:]
            if command[0].isdigit():
              amntS = ""
              for c in command:
                if c.isdigit():
                  amntS += c
                else:
                  break
              amnt = int(amntS)
              if len(command) > len(amntS)+1:
                command = command[len(amntS)+1:]
            if len(command) > 1:
              id = formatter.getIDFromMention(command)
              if user.doesExist(id):
                member = await message.channel.guild.fetch_member(int(id))
                u = user.getUser(id)
              else:
                e = error.embedUserDoesNotExist()
                await message.channel.send(embed=e)
                return
        e, f = user.embedGivePrimo(u, amnt)
        await message.channel.send(member.mention, embed=e, file=f)

      #Give Mora for Free
      elif command.lower().startswith("giftm"):
        u = user.getUser(str(message.author.id))
        member = await message.channel.guild.fetch_member(message.author.id)
        amnt = 1000000

        if len(command) > 6:
            command = command[6:]
            if command[0].isdigit():
              amntS = ""
              for c in command:
                if c.isdigit():
                  amntS += c
                else:
                  break
              amnt = int(amntS)
              if len(command) > len(amntS)+1:
                command = command[len(amntS)+1:]
            if len(command) > 1:
              id = formatter.getIDFromMention(command)
              if user.doesExist(id):
                member = await message.channel.guild.fetch_member(int(id))
                u = user.getUser(id)
              else:
                e = error.embedUserDoesNotExist()
                await message.channel.send(embed=e)
                return
        e, f = user.embedGiveMora(u, amnt)
        await message.channel.send(member.mention, embed=e, file=f)

  if message.content.lower().startswith(pre):
    command = message.content[len(pre):]
    if user.doesExist(str(message.author.id)):
      u = user.getUser(str(message.author.id))
      if command.lower().startswith("free 10") or command.lower() == "f 10":
        embed, f, rarity = pull.embedFreeTenPull(u.name)
        e = discord.Embed()
        if rarity == 5:
          file = discord.File(fiveStarWishGifTen, "TenFiveStar.gif")
          e.set_image(url="attachment://TenFiveStar.gif")
        else:
          file = discord.File(fourStarWishGifTen, "TenFourStar.gif")
          e.set_image(url="attachment://TenFourStar.gif")
        msg = await message.channel.send(embed=e, file=file)
        await asyncio.sleep(7)
        await msg.delete()
        await message.channel.send(message.author.mention, embed=embed, file=f)

      #Free single pull
      elif command.lower().startswith("free") or command.lower() == "f":

        embed, f, rarity = pull.embedFreeSinglePull(u.name)
        e = discord.Embed()
        if rarity == 5:
          file = discord.File(fiveStarWishGifSingle, "SingleFiveStar.gif")
          e.set_image(url="attachment://SingleFiveStar.gif")
        elif rarity == 4:
          file = discord.File(fourStarWishGifSingle, "SingleThreeStar.gif")
          e.set_image(url="attachment://SingleThreeStar.gif")
        else:
          file = discord.File(threeStarWishGifSingle, "SingleThreeStar.gif")
          e.set_image(url="attachment://SingleThreeStar.gif")
        msg = await message.channel.send(embed=e, file=file)
        await asyncio.sleep(7)
        await msg.delete()
        await message.channel.send(message.author.mention, embed=embed, file=f)

      #Primo 10 wish
      elif command.lower().startswith("wish 10") or command.lower() == "w 10":
        if u.primogems < 1600:
          e = error.embedNotEnoughPrimo()
          await message.channel.send(message.author.mention, embed=e)
          return
        embed, f, rarity = pull.embedTenPull(u)
        e = discord.Embed()
        if rarity == 5:
          file = discord.File(fiveStarWishGifTen, "TenFiveStar.gif")
          e.set_image(url="attachment://TenFiveStar.gif")
        else:
          file = discord.File(fourStarWishGifTen, "TenFourStar.gif")
          e.set_image(url="attachment://TenFourStar.gif")
        msg = await message.channel.send(embed=e, file=file)
        await asyncio.sleep(7)
        await msg.delete()
        await message.channel.send(message.author.mention, embed=embed, file=f)

      #Primo single pull
      elif command.lower().startswith("wish") or command.lower() == "w":
        if u.primogems < 160:
          e = error.embedNotEnoughPrimo()
          await message.channel.send(message.author.mention, embed=e)
          return
        embed, f, rarity = pull.embedSinglePull(u)
        e = discord.Embed()
        if rarity == 5:
          file = discord.File(fiveStarWishGifSingle, "SingleFiveStar.gif")
          e.set_image(url="attachment://SingleFiveStar.gif")
        elif rarity == 4:
          file = discord.File(fourStarWishGifSingle, "SingleThreeStar.gif")
          e.set_image(url="attachment://SingleThreeStar.gif")
        else:
          file = discord.File(threeStarWishGifSingle, "SingleThreeStar.gif")
          e.set_image(url="attachment://SingleThreeStar.gif")
        msg = await message.channel.send(embed=e, file=file)
        await asyncio.sleep(7)
        await msg.delete()
        await message.channel.send(message.author.mention, embed=embed, file=f)

      #Show profile
      elif command.lower().startswith("profile") or command.lower().startswith("p"):
        url = message.author.avatar_url
        other = False
        if command.lower().startswith("profile"):
          if len(command) > 8:
            command = command[8:]
            other = True
        else:
          if len(command) > 2:
            command = command[2:]
            other = True
        
        if other:
          id = formatter.getIDFromMention(command)
          if user.doesExist(id):
            member = await message.channel.guild.fetch_member(int(id))
            url = formatter.getAvatar(member)
            u = user.getUser(id)
          else:
            e = error.embedUserDoesNotExist()
            await message.channel.send(embed=e)
            return
        e = user.embedProfile(u)
        e.set_thumbnail(url=url)
        e.set_footer(text=f"{message.author.mention}")
        await message.channel.send(embed=e)

      #Show balance
      elif command.lower().startswith("balance") or command.lower() == "bal" or command.lower() == "b":
        e, f = user.embedBal(u)
        e.set_footer(text=f"{message.author.mention}")
        await message.channel.send(embed=e, file=f)

      #Show resin
      elif command.lower().startswith("resin") or command.lower() == "r":
        e, f = user.embedResin(u)
        e.set_footer(text=f"{message.author.mention}")
        await message.channel.send(embed=e, file=f)
      
      #Show Character List
      elif command.lower().startswith("listc"):
        pg = 1
        if len(command) > 6:
          command = command[6:]
          if command.isdigit():
            pg = int(command)
          else:
            #show specific character info
            if u.doesCharExist(command):
              e, f = user.embedShowCharInfo(u, u.characters[formatter.nameUnformatter(command)])
              await message.channel.send(embed=e, file=f)
              return
            else:
              await message.channel.send(embed=error.embedCharIsNotOwned())
              return
        e = user.embedCharList(u, pg)
        await message.channel.send(embed=e)
      
      #Show Weapon List
      elif command.lower().startswith("listw"):
        pg = 1
        if len(command) > 6:
          command = command[6:]
          if command.isdigit():
            pg = int(command)
          else:
            #show specific weapon info
            if u.doesWeapExist(command):
              e, f = user.embedShowWeapInfo(u, u.weapons[formatter.nameUnformatter(command)])
              await message.channel.send(embed=e, file=f)
              return
            else:
              await message.channel.send(embed=error.embedWeapIsNotOwned())
              return
        e = user.embedWeapList(u, pg)
        await message.channel.send(embed=e)

      #Lists all commands
      elif command.lower().startswith("help"):
        embed = discord.Embed(title = "Yapa Bot Commands", color=discord.Color.dark_red())
        text = f"**[{pre}start]** Allows you to start your Yappa Experience.\n"
        text += f"**[{pre}wish] | [10]** Allows you to pull for your favorite genshin wishes at the cost of 160 primogems per wish.\n"
        text += f"**[{pre}free] | [10]** Allows you to pull for your favorite genshin wishes for free. These wishes will not be added to your collection.\n"
        text += f"**[{pre}profile] | [@user]** Allows you to look at your personal user data.\n"
        text += f"**[{pre}balance]** Allows you to look at your collected currencies.\n"
        text += f"**[{pre}resin]** Allows you to look at your current resin.\n"
        text += f"**[{pre}listc] | [pg#, character]** Allows you to look at your personal character collection.\n"
        text += f"**[{pre}listw] | [pg#, weapon]** Allows you to look at your personal weapon collection.\n"
        embed.add_field(name="Basic Commands", value = text, inline=False)
        await message.channel.send(embed=embed)

    else:

      #Makes user data for new user
      if command.lower().startswith("start"):
        user.createUser(str(message.author.name), str(message.author.id))
        embed = discord.Embed(title = "Starting Adventure", color = discord.Color.green())
        embed.add_field(name = "_ _", value=f"{message.author.mention}\'s adventure has now begun!\nDo **[{pre}help]** to get the list of available commands.")
        embed.set_thumbnail(url=message.author.avatar_url)
        await message.channel.send(message.author.mention, embed=embed)

        
      else:
        await message.channel.send(f"{message.author.mention}, Use **[{pre}start]** to begin your adventure")

keep_alive()
client.run(os.getenv('TOKEN'))