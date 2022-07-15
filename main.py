from unicodedata import name
import nextcord
from nextcord import Interaction,SlashOption
from nextcord.ext import commands
import json
import logging
from database import db_commands
from polygon import polygonAPI
import verifications as verify
import sys
from keepalive import keep_alive

title="\N{mushroom} Funguy Family Airdrop-Bot \N{mushroom}"
success='✅ Success!'

###########
# Credentials for discord Bot
###########
f = open('credentials/funguy_family.json')
credentialData = json.load(f)

logger = logging.getLogger('nextcord')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

#Server_ID of the guild where the commands will be deployed
ServerID = credentialData['serverID']
intents = nextcord.Intents.default()
#intents.members = True
client = commands.Bot(command_prefix='/', intents=intents)

#############
# Connect to db
#############
db = db_commands.DB()

###############
# Check if the bot is ready to be used
###############
@client.event
async def on_ready():
  logger.info('The Bot is now READY to be used !!!')


class Join(nextcord.ui.View):
  '''
  Airdrop Join Buttion.
  '''
  @nextcord.ui.button(label = 'Join Current/Active Airdrop', style=nextcord.ButtonStyle.green)
  async def join(self, button : nextcord.ui.Button, interaction: nextcord.Interaction):     
    
    user = interaction.user
    user_id = int(user.id)
    avatar_url = str(user.avatar)

    signin_result = await db.insert_airdrop_signin(user_id)
    signin_json = json.loads(signin_result[0][0])

    if signin_json[0]['STATUS'] == 1:
      logger.info("User {} joined the current airdrop".format(user))
      embed = nextcord.Embed(title=title,description="Sign In Verification",color=nextcord.Color.green()) 
      embed.add_field(name="Wallet Verification",value=success,inline=False)
         
    else :
      embed = nextcord.Embed(title=title,description="Sign In Verification",color=nextcord.Color.red()) 
      embed.set_thumbnail(url=avatar_url)
      embed.add_field(name="Result",value="failed with error :  ***{}***".format(signin_json[0]['ErrorMsg']),inline=False)

    button.disabled = True  
    embed.set_thumbnail(url=avatar_url)
    await interaction.response.edit_message(embed=embed,view=self)


@client.slash_command(name="funguy_help", description="Launches Funguy Application Help page", guild_ids=[ServerID])
async def funguy_help(interaction: Interaction):
  roles = interaction.user.roles
  if not await role_check(interaction,roles):
      return
    
    
  
  user = interaction.user
  user_id,avatar_url,discord_name,discord_tag = await get_user_details(user)
  
  embed = nextcord.Embed(title=title, description="Hello **{}**".format(discord_name), color=nextcord.Color.blue())
  embed.add_field(name="/funguy_status",value="> Gives your funguy information.",inline=False)
  embed.add_field(name="/funguy_flex",value="> Flex your funguy information.",inline=False)
  embed.add_field(name="/funguy_top_10",value="> Gives information about the top 10 funguy members.",inline=False)
  embed.add_field(name="/funguy_add",value="""> _Add your data for the Tuschay Coin ($TSHY) Airdrop_
                                              > /funguy_add 0x123120e08556037329d2b34ce553e1f255ccc7e9 25 1990-01-25
                                              
                                              > **Options:**
                                              > **wallet address** - _What is your Polygon (MATIC) wallet address?(wallet with your Funguy Family collection NFTs) *_
                                              > **Number of Funguys Owned** -  _How many items (NFT's) do you own from the Funguy Family collection? *_
                                              > **DateOfOldestFunguyOwned** -  _Date of the oldest Funguy Family NFT in your wallet? (In format YYYY-MM-DD) *_
                                              """,
                                              inline=False)
  embed.add_field(name="/funguy_update",value="""> _Update your current data if any exist_
                                            > /funguy_update 0x123120e08556037329d2b34ce553e1f255ccc7e9 25 1990-01-25
                                            > **Options:**
                                            > **wallet address** - _What is your Polygon (MATIC) wallet address?(wallet with your Funguy Family collection NFTs) *_
                                            > **Number of Funguys Owned** -  _How many items (NFT's) do you own from the Funguy Family collection? *_
                                            > **DateOfOldestFunguyOwned** -  _Date of the oldest Funguy Family NFT in your wallet? (In format YYYY-MM-DD) *_
                                            """,
                                            inline=False)

  embed.set_author(name='| Funguy - Help', icon_url=avatar_url) 
  embed.set_thumbnail(url=avatar_url) 
  await interaction.response.send_message(embed=embed,ephemeral=True)


@client.slash_command(name="funguy_status",description="Retrieve your current data",guild_ids=[ServerID])
async def funguy_status(interaction: Interaction):
  roles = interaction.user.roles
  if not await role_check(interaction,roles):
      return

  user = interaction.user
  user_id,avatar_url,discord_name,discord_tag = await get_user_details(user)
  
  logger.info('User {}#{} executed  -  /funguy_status command'.format(discord_name, discord_tag))

  status_result = await db.view_funguy_user(user_id)
  status_json = json.loads(status_result[0][0])

  view = nextcord.ui.View()

  if status_json[0]['STATUS'] == 0:
    embed = nextcord.Embed(title=title,description="Hello **{}** . I was unable to find any existing data for your user.".format(discord_name),color=nextcord.Color.red())
    embed.add_field(name="Reason",value='{}'.format(status_json[0]['ErrorMsg']),inline=False)
    embed.add_field(name="Tips",value="**/funguy_help**\nExecute command /funguy_help for more info",inline=False)
    embed.add_field(name="/funguy_add",value="Example : /funguy_add 0x123120e08556037329d2b34ce553e1f255ccc7e9 25 1990-01-25",inline=False)

  else: 
    embed = nextcord.Embed(title=title,description="Hello **{}** . Below is your data I have found in our database.".format(discord_name),color=nextcord.Color.green())
    embed.add_field(name="Wallet",value="\N{bank} {}".format(status_json[0]['WalletAddress']),inline=False)
    embed.add_field(name="Number of Funguys Owned",value="\N{cyclone} {}".format(status_json[0]['NumberOfFunguysOwned']),inline=False)
    embed.add_field(name="Number of Funguys Baby Owned",value="\N{cyclone} {}".format(status_json[0]['NumberOfFunguysBabyOwned']),inline=False)
    embed.add_field(name="Date of oldest Funguy",value="\N{calendar} {}".format(status_json[0]['DateOfOldestFunguyOwned']),inline=False)
    embed.add_field(name="Tip",value='Execute : /funguy_update so I can update your existing data',inline=False)

    if status_json[0]['DidUserSignIn'] == 0 :
      view = Join() 
    else:
      embed.add_field(name="Already Signed",value="Your data is submitted to the current Airdrop: {}".format(status_json[0]['AirDropName']))
      
  
  
  embed.set_author(name='| Funguy - Status', icon_url=avatar_url)    
  embed.set_thumbnail(url=avatar_url)
  await interaction.response.send_message(embed=embed,ephemeral=True,view=view)

    

@client.slash_command(name="funguy_add", description="Example : /funguy_add 0x123120e08556037329d2b34ce553e1f255ccc7e9 25 1990-01-25", guild_ids=[ServerID])
async def funguy_add(interaction: Interaction,
                        wallet_address : str = SlashOption(description="Polygon (MATIC) wallet address"),
                        number_of_funguys_owned : str = SlashOption(description="How many items (NFT's) do you own from the Funguy Family collection?"),
                        number_of_funguys_baby_owned : str = SlashOption(description="How many items (NFT's) do you own from the Funguy Family Baby collection?"),
                        date_of_oldest_funguy_owned : str = SlashOption(description="Date of the oldest Funguy Family NFT in your wallet. (In format YYYY-MM-DD)") 
                    ):

  roles = interaction.user.roles
  if not await role_check(interaction,roles):
      return
  
  user = interaction.user
  user_id,avatar_url,discord_name,discord_tag = await get_user_details(user)

  logger.info('User{}#{} executed  -  /funguy_add command'.format(discord_name, discord_tag))

  embed,isfailed,fnumber,bnumber,date_oldest = await verify.data_validation(wallet_address,number_of_funguys_owned,number_of_funguys_baby_owned,date_of_oldest_funguy_owned)

  if(isfailed==True):
    logger.error("Invalid Data Entered : {} | {} | {} | {}".format(wallet_address,number_of_funguys_owned,number_of_funguys_baby_owned,date_oldest))
    embed.set_author(name='| Funguy - Add Entry Data', icon_url=avatar_url)    
    embed.set_thumbnail(url=avatar_url)
    await interaction.response.send_message(embed=embed,ephemeral=True)

  else:
    logger.info("Valid Data Entered : {} | {} | {} | {}".format(wallet_address,fnumber,bnumber,date_oldest))
    insert_result = await db.insert_funguy_user(user_id,discord_name,int(discord_tag),wallet_address,fnumber,bnumber,date_oldest)
    insert_json = json.loads(insert_result[0][0])

    if insert_json[0]['STATUS'] == 1:
      embed = nextcord.Embed(title=title,description="Input data verification",color=nextcord.Color.green())
      embed.add_field(name="Result",value=success,inline=False)
      embed.add_field(name="Tip",value='Execute : /funguy_status to check your current data',inline=False)
      
    else:
      embed = nextcord.Embed(title=title,description="**Entry Save Failed** ❌",color=nextcord.Color.red())
      embed.add_field(name="Reason",value='{}'.format(insert_json[0]['ErrorMsg']),inline=False)
      embed.add_field(name="Tip",value='Execute : /funguy_update so I can update your existing data',inline=False)
      embed.add_field(name="Tip",value='Execute : /funguy_status to check your current data',inline=False)
  
    embed.set_author(name='| Funguy - Add Entry Data', icon_url=avatar_url)    
    embed.set_thumbnail(url=avatar_url)
    await interaction.response.send_message(embed=embed,ephemeral=True)


@client.slash_command(name="funguy_update", description="Example : /funguy_update 0x123120e08556037329d2b34ce553e1f255ccc7e9 25 1990-01-25", guild_ids=[ServerID])
async def funguy_update(interaction: Interaction,
                        wallet_address : str = SlashOption(description="Polygon (MATIC) wallet address"),
                        number_of_funguys_owned : str = SlashOption(description="How many items (NFT's) do you own from the Funguy Family collection?"),
                        number_of_funguys_baby_owned : str = SlashOption(description="How many items (NFT's) do you own from the Funguy Family Baby collection?"),
                        date_of_oldest_funguy_owned : str = SlashOption(description="Date of the oldest Funguy Family NFT in your wallet. (In format YYYY-MM-DD)")
                        ):
  roles = interaction.user.roles
  if not await role_check(interaction,roles):
      return

  user = interaction.user

  user_id,avatar_url,discord_name,discord_tag = await get_user_details(user)
  logger.info('User {}#{} executed  -  /funguy_update command'.format(discord_name,discord_tag))

  embed,isfailed,fnumber,bnumber,date_oldest = await verify.data_validation(wallet_address,number_of_funguys_owned,number_of_funguys_baby_owned,date_of_oldest_funguy_owned)

  if(isfailed==True):
    logger.error("Invalid Data Entered : {} | {} | {} | {}".format(wallet_address,number_of_funguys_owned,number_of_funguys_baby_owned,date_oldest))
    embed.set_author(name='| Funguy - Add Entry Data', icon_url=avatar_url)    
    embed.set_thumbnail(url=avatar_url)
    await interaction.response.send_message(embed=embed,ephemeral=True)

  else:
    logger.info("Valid Data Entered : {} | {} | {} | {}".format(wallet_address,fnumber,bnumber,date_oldest))
    update_result = await db.update_funguy_user(user_id,discord_name,int(discord_tag),wallet_address,fnumber,bnumber,None,date_oldest)
    update_json = json.loads(update_result[0][0])

    if update_json[0]['STATUS'] == 1:
      embed = nextcord.Embed(title=title,description="Update data verification",color=nextcord.Color.green())
      embed.add_field(name="Result",value=success,inline=False)
      embed.add_field(name="Tip",value='Execute : /funguy_status to check your updated data',inline=False)

    else:
      embed = nextcord.Embed(title=title,description="Update data verification",color=nextcord.Color.red())      
      embed.add_field(name="Result",value="failed with error :  ***{}***".format(update_json[0]['ErrorMsg']),inline=False)
    
    embed.set_author(name='| Funguy - Update Entry Data', icon_url=avatar_url)  
    embed.set_thumbnail(url=avatar_url)
    await interaction.response.send_message(embed=embed,ephemeral=True)


@client.slash_command(name="calculate_rewards", description="Example : /calculate_rewards January 2022 - Tuschay Coin ($TSHY) Airdrop", guild_ids=[ServerID],default_member_permissions=0)
async def calculate_rewards(interaction: Interaction,
                            airdrop_name : str = SlashOption(description="Month Year - Tuschay Coin ($TSHY) Airdrop"),
                            ):

  roles = interaction.user.roles
  if not await role_check(interaction,roles):
      return
  
  user = interaction.user

  user_id,avatar_url,discord_name,discord_tag = await get_user_details(user)

  logger.info('User {}#{} executed  -  /calculate_rewards command'.format(discord_name,discord_tag))

  if await verify.check_if_admin(user_id):
    calculation_result = await db.calculate_TSHY_coins(airdrop_name,user_id)
    calculation_json = json.loads(calculation_result[0][0])

    if calculation_json[0]['STATUS'] == 1:
      embed = nextcord.Embed(title=title,description="Airdrop Reward Calculation",color=nextcord.Color.green())
      embed.add_field(name="Result",value="Reward Calculation Successfully executed for : \n ***{}***".format(airdrop_name),inline=False)
      
    else:
      embed = nextcord.Embed(title=title,description="Airdrop Reward Calculation",color=nextcord.Color.red())
      embed.add_field(name="Result",value="Reward Calculation failed with error :  ***{}***".format(calculation_json[0]['ErrorMsg']),inline=False)
      
    embed.set_thumbnail(url=avatar_url)
    embed.set_author(name='| Funguy - Calculate Rewards', icon_url=avatar_url)    
    await interaction.response.send_message(embed=embed,ephemeral=True)  

  else:
    embed = nextcord.Embed(title=title,description="❌ **NOT AN ADMIN** ❌",color=nextcord.Color.red())
    embed.add_field(name="Tip",value='Don\'t be sneaky',inline=False)
    await interaction.response.send_message(embed=embed,ephemeral=True)


@client.slash_command(name="funguy_top_ten", description="View top ten funguy users.", guild_ids=[ServerID])
async def funguy_top_ten(interaction: Interaction):
  roles = interaction.user.roles
  if not await role_check(interaction,roles):
      return
    
    
  
  user = interaction.user
  user_id,avatar_url,discord_name,discord_tag = await get_user_details(user)

  embed = nextcord.Embed(title=title,description="Hello **{}**. Below is a current ranking of the Top 10 Funguy Holders. Be sure to use /funguy_update to add any Funguys you own to the bot!".format(discord_name),color=nextcord.Color.green())
  status_result = await db.view_top_ten_funguy_user()
  status_json = json.loads(status_result[0][0])
  json_size = len(status_json)

  embed.add_field(name="1st place",value=":first_place: {} - funguy owned: {}".format(status_json[0]['DiscordUserName'], status_json[0]['NumberOfFunguysOwned']),inline=False)
  embed.add_field(name="2nd place",value=":second_place: {} - funguy owned: {}".format(status_json[1]['DiscordUserName'], status_json[1]['NumberOfFunguysOwned']),inline=False)
  embed.add_field(name="3rd place",value=":third_place: {} - funguy owned: {}".format(status_json[2]['DiscordUserName'], status_json[2]['NumberOfFunguysOwned']),inline=False)

  for i in range(3, json_size):  
    embed.add_field(name="{}th place".format(i+1),value=":medal: {} - funguy owned: {}".format(status_json[i]['DiscordUserName'], status_json[i]['NumberOfFunguysOwned']),inline=False)

  embed.set_author(name='| Funguy - Top 10', icon_url=avatar_url) 
  embed.set_thumbnail(url=avatar_url) 

  await interaction.response.send_message(embed=embed,ephemeral=True)

@client.slash_command(name="funguy_flex",description="Flex your funguys",guild_ids=[ServerID])
async def funguy_flex(interaction: Interaction):
  roles = interaction.user.roles
  if not await role_check(interaction,roles):
      return

  user = interaction.user
  user_id,avatar_url,discord_name,discord_tag = await get_user_details(user)
  
  logger.info('User {}#{} executed  -  /funguy_flex command'.format(discord_name, discord_tag))

  status_result = await db.view_funguy_user(user_id)
  status_json = json.loads(status_result[0][0])

  view = nextcord.ui.View()


  if status_json[0]['STATUS'] == 0:
    embed = nextcord.Embed(title=title,description="Hello **{}** . I was unable to find any existing data for your user.".format(discord_name),color=nextcord.Color.red())
    embed.add_field(name="Reason",value='{}'.format(status_json[0]['ErrorMsg']),inline=False)
    embed.add_field(name="Tips",value="**/funguy_help**\nExecute command /funguy_help for more info",inline=False)
    embed.add_field(name="/funguy_add",value="Example : /funguy_add 0x123120e08556037329d2b34ce553e1f255ccc7e9 25 1990-01-25",inline=False)

  else: 
    polygon = polygonAPI.MakeApiCall(
      "https://api.polygonscan.com/api",
      "account",
      "tokenbalance",
      "0xD8f9a909649BA317175A4f2F5416958Af64a0BFC",
      status_json[0]['WalletAddress']
    )
    embed = nextcord.Embed(title=title,description="**{}** is showing off their wallet balance! Type in /funguy_flex to show yours!".format(discord_name),color=nextcord.Color.green())
    embed.add_field(name="Number of Funguys Owned",value="\N{cyclone} {}".format(status_json[0]['NumberOfFunguysOwned']),inline=False)
    embed.add_field(name="Number of Funguys Baby Owned",value="\N{cyclone} {}".format(status_json[0]['NumberOfFunguysBabyOwned']),inline=False) 
    embed.add_field(name="Number of Tshy Coin Owned",value=":moneybag: {}".format(polygon.tuschay_coin),inline=False) 
    
  embed.set_author(name='| Funguy - Flex ', icon_url=avatar_url)    
  embed.set_thumbnail(url=avatar_url)
  await interaction.response.send_message(embed=embed,ephemeral=False,view=view)



async def get_user_details(user):

  user_id = int(user.id)
  avatar_url = str(user.avatar) if user.avatar else "https://cdn.discordapp.com/embed/avatars/0.png"
  discord_name = str(user).rstrip().split('#')[0].rstrip()
  discord_tag = str(user).rstrip().split('#')[1].rstrip()

  return user_id,avatar_url,discord_name,discord_tag

async def role_check(interaction,roles):

  role_names = [role.name for role in roles]

  if not any(item in role_names for item in credentialData['funguy_roles']):
    embed = nextcord.Embed(title=title,description="Hello **_Spore_** Sadly not a Funguy Family member",color=nextcord.Color.red())
    embed.add_field(name="Eligible Funguy Family Roles",value="**Funguy Folk** | **_Funguy Forager_** | **_Funguy Farmer_** | **_Funguy Champignon_** | **_Funguy Philanthropist_**")
    embed.add_field(name="Tip",value='If you want to join the Funguy Family check out the [**official-links**](https://discord.com/channels/883888852278853684/888185899224018945) channel ',inline=False)
    await interaction.response.send_message(embed=embed,ephemeral=True)
    return False
  else:
    return True
  

keep_alive()
client.run(credentialData['discord_token'])







