import database_mongo
#:white_flower: 5 star
#:dizzy: 4 star
#:star2: 3 star
#:star1: 2 star
#:sparkles: 1 star
#:moneybag: Mora
fiveStarPrefix = ":white_flower: "
fourStarPrefix = ":dizzy: "
threeStarPrefix = ":star2: "
twoStarPrefix = ":star1: "
oneStarPrefix = ":sparkles: "

commandPrefix = "?"

def get_prefix(ctx):
  ser_pref = database_mongo.get_prefix(ctx.message.guild.id)
  if bool(ser_pref):
    return ser_pref["prefix"]
  return commandPrefix