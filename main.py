import discord
from discord.ext import tasks
import os
import requests
import json
from replit import db
from threading import Timer
from keep_alive import keep_alive
from analysis import BotModules
import pandas as pd

# instantiate a discord client
client = discord.Client()

# import bot modules
bm = BotModules()

# get environment variables
REFRESH_INTV = 3600*24
WAIT_TIME = 0.1
TOKEN = os.getenv("TOKEN")

# initiate base path
BASEPATH = "./data"

# initialize global variables
init = 1
all_prices = None
caps_comparison = None

def check(pre):
  try: 
    return all(isinstance(int(x), int) for x in pre)
  except: 
    return False

@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))
  channel = discord.utils.get(client.get_all_channels(), name='general')
  _routine.start()
  await client.get_channel(channel.id).send('Price Bot is now online!')
  # _get_all_prices.start()
  # _get_small_caps.start()

# function called whenever there is a message in the chat 
@client.event
async def on_message(message):
  if message.author == client.user:
    return

  msg = message.content

  # print price
  if msg.startswith('$price'):
    ids = msg.split('$price ',1)[1].lower()
    price = bm.get_prices(ids)
    await message.channel.send('USD {:,}'.format(price))

  # print list of supported assets
  if msg.startswith('$list'):
    assetList = all_prices['id']
    await message.channel.send(assetList)

  # check if asset is supported
  # example: $support bitcoin 
  if msg.startswith('$support'):
    asset = msg.split('$support ', 1)[1].lower()
    check = bm.is_supported(asset)
    await message.channel.send(check)

  if msg.startswith('$getnewsmallcaps'):
    ls = caps_comparison['small_caps']
    if len(ls["id"]) == 0:
      await message.channel.send("No new small caps")
    else:
      await message.channel.send(ls['id'])

  if msg.startswith('$getsmallcaps'):
    small_caps = pd.read_csv(os.path.join(BASEPATH, "small_caps.csv"))
    await message.channel.send(small_caps['id'])


@tasks.loop(seconds=float(REFRESH_INTV))
async def _routine():
  global all_prices, caps_comparison
  all_prices, caps_comparison = bm.routine()
  print("Routine completed")
  

if __name__ == "__main__":
  keep_alive()
  client.run(TOKEN)
