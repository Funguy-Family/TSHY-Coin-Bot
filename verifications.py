import nextcord
from datetime import date
from datetime import datetime
import json
from web3 import Web3

today = date.today()
releasedate=datetime.strptime("2021-09-01", '%Y-%m-%d')
title="\N{mushroom} Funguy Family Airdrop-Bot \N{mushroom}"
success='✅ Success!'

f = open('credentials/funguy_family.json')
credentialData = json.load(f)



async def data_validation(wallet_address,number_of_funguys,number_of_funguys_baby_owned,date):
  
  embed = nextcord.Embed(title=title,description="Input data verification") 
  isfailed=False

  ankr_url = 'https://rpc.ankr.com/polygon'
  web3 = Web3(Web3.HTTPProvider(ankr_url))
  #TODO : Maybe find a solution to check for owners of Funguy Contract Address 0x2953399124F0cBB46d2CbACD8A89cF0599974963
  # f = web3.filter({'address': "0x2953399124F0cBB46d2CbACD8A89cF0599974963"})
  # print(f)

  if web3.isAddress(wallet_address):
    embed.add_field(name="Wallet Verification",value=success,inline=False)
  else : 
    embed.add_field(name="Wallet Verification",value="❌ Failed! :  **{}** is not a valid address".format(wallet_address),inline=False)
    isfailed=True 


  if (number_of_funguys):
    try:
      fnumber=number_of_funguys
      fnumber = int(number_of_funguys)
      assert fnumber < 2500, 'Incorrect Amount of Funguys'
      embed.add_field(name="Number of Funguys owned",value=success,inline=False)
    except Exception:
      embed.add_field(name="Number of Funguys owned",value='❌ Failed! :  **{}** is not a valid number'.format(number_of_funguys),inline=False)
      isfailed=True

    if (number_of_funguys_baby_owned):
      try:
        bnumber=number_of_funguys_baby_owned
        bnumber = int(number_of_funguys_baby_owned)
        assert bnumber < 2500, 'Incorrect Amount of Funguys'
        embed.add_field(name="Number of Funguys Baby owned",value=success,inline=False)
      except Exception:
        embed.add_field(name="Number of Funguys Baby owned",value='❌ Failed! :  **{}** is not a valid number'.format(number_of_funguys_baby_owned),inline=False)
        isfailed=True

  if (date):
    try:
        date_oldest=date
        assert  releasedate <= datetime.strptime(date, '%Y-%m-%d')

        date_oldest = datetime.strptime(date, '%Y-%m-%d').date()
        embed.add_field(name="Date",value=success,inline=False)
    except Exception:
        embed.add_field(name="Date",value='❌ Failed! : **{}** is not a valid date.\n\n - **YYYY-MM-DD** is the valid format\n\n - Oldest date accepted is **2021-09-01**'.format(date),inline=False)
        isfailed=True

  return embed,isfailed,fnumber,bnumber,date_oldest

async def check_if_admin(user_id):
    return True if user_id in credentialData['admin'] else False
