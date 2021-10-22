import discord
import os
import requests
import json
from replit import db
from threading import Timer
from keep_alive import keep_alive

# instantiate a discord client
client = discord.Client()

def check(pre):
  try: 
    return all(isinstance(int(x), int) for x in pre)
  except: 
    return False

def getPrices(asset):
  url = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd'
  response = requests.get(url)
  data = response.json()

  # insert asset and prices into db
  for i in range(len(data)):
    ids = data[i]['id']
    currentPrices = int(data[i]['current_price'])
    db["ids"] = currentPrices
 
  if "ids" in db.keys():
    return db[asset]
  else:
    return None

def isSupported(asset):
  if asset in db.keys():
    return True
  else:
    return False

@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))
  channel = discord.utils.get(client.get_all_channels(), name='general')
  await client.get_channel(channel.id).send('Price Bot is now online!')

# function called whenever there is a message in the chat 
@client.event
async def on_message(message):
  if message.author == client.user:
    return

  msg = message.content

  # print price
  if msg.startswith('$price'):
    ids = msg.split('$price ',1)[1].lower()
    price = int(getPrices(ids))
    await message.channel.send('USD {0}'.format(price))

  # print list of supported assets
  if msg.startswith('$list'):
    assetList = [key for key in db.keys()]
    await message.channel.send(assetList)

  # check if asset is supported
  # example: $support bitcoin 
  if msg.startswith('$support'):
    asset = msg.split('$support ', 1)[1].lower()
    check = isSupported(asset)
    await message.channel.send(check)

keep_alive()
client.run(os.getenv('TOKEN'))
