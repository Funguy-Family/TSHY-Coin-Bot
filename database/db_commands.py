from sqlite3 import DatabaseError
import pyodbc 
import json
from datetime import date

class DB():
  def __init__(
    self
  ):
    """
      Database connections
    """
    f = open('credentials/db.json')
    db_data = json.load(f)

    self.conn = pyodbc.connect('Driver={' + db_data['driver'] + '};'
                          'Server=' + db_data['server_name'] + ';'
                          'Database='+ db_data['database_name'] + ';'
                          'UID='+ db_data['username'] + ';'
                          'PWD='+ db_data['password'] + ';'
                          'Trusted_Connection=no;')
    self.noCount = """ SET NOCOUNT ON; """                    
    if self.conn: 
      print('The Bot is Connected to the  DB')
    else:
      print('Error connecting to DB')

  async def view_funguy_user(
    self,
    discord_user_id: int
  ):
    """
      '[
        { 
          "DiscordUserID" : "2"
        }
      ]'
    """
    input_data_dict = {
      'DiscordUserID': discord_user_id
    }
    
    input_data_json = json.dumps(input_data_dict)

    try:
      sql = """\
      EXEC [dbo].[ViewFunguyUserProc] @Data=?
      """
      params = (input_data_json)
      self.cursor = self.conn.cursor()
      self.cursor.execute(self.noCount + sql, params)
      output_json_data = self.cursor.fetchall()
      return output_json_data
    except Exception as e:
      output_data_dict = {
        'STATUS': 0,
        'ErrorMsg': e
      }
      
      output_json_data = json.dumps(output_data_dict)    
      return output_json_data

  async def insert_funguy_user(
    self,
    discord_user_id: int,
    discord_user_name: str,
    discord_user_tag: int,
    wallet_address: str, 
    number_of_funguys_owned: int, 
    number_of_funguysbaby_owned : int, 
    date_of_oldest_funguy_owned: date
  ):

    """
    '[
      { 
        "DiscordUserID" : "2",
        "DiscordUserName": "John",
        "DiscordUserTag": "0001",
        "WalletAddress": "awrfafaw",
        "NumberOfFunguysOwned": 2,
        "NumberOfFunguysBabyOwned": 1,
        "DateOfOldestFunguyOwned": "2021-12-21"
      }
    ]'
    """

    input_data_dict = {
        "DiscordUserID" : discord_user_id,
        "DiscordUserName": discord_user_name,
        "DiscordUserTag": discord_user_tag,
        "WalletAddress": wallet_address,
        "NumberOfFunguysOwned": number_of_funguys_owned,
        "NumberOfFunguysBabyOwned": number_of_funguysbaby_owned,
        "DateOfOldestFunguyOwned": date_of_oldest_funguy_owned
    }
    
    input_data_json = json.dumps(input_data_dict,default=str)

    try:

      assert (type(number_of_funguys_owned) == int), "Number of Funguys owned must be a number"
      assert (type(date_of_oldest_funguy_owned) == date), "Date of Oldest Funguy owned must be a date (YYYY-MM-DD)"

      sql = """\
      EXEC [dbo].[InsertFunguyUserProc] @Data=?
      """
      params = (input_data_json)
      self.cursor = self.conn.cursor()
      self.cursor.execute(self.noCount + sql, params)    
      output_json_data = self.cursor.fetchall()      
      self.cursor.commit()
      self.cursor.close()
      del self.cursor
      return output_json_data
    except Exception as e:
      output_data_dict = {
        'STATUS': 0,
        'ErrorMsg': e
      }
      
      output_json_data = json.dumps(output_data_dict)    
      return output_json_data

  async def update_funguy_user(
    self,
    discord_user_id: int,
    discord_user_name: str,
    discord_user_tag: int,
    wallet_address: str,
    number_of_funguys_owned: int,
    number_of_funguysbaby_owned : int, 
    is_it_addition: bool,
    date_of_oldest_funguy_owned: date
  ):

    """
    '[
      { 
        "DiscordUserID" : "2",
        "DiscordUserName": "John",
        "DiscordUserTag": "0001",
        "WalletAddress": "awrfafaw",
        "NumberOfFunguysOwned": "2",
        "IsItAddition": "1",
        "DateOfOldestFunguyOwned": "2021-12-21"
      }
    ]' 
    """

    input_data_dict = {
            "DiscordUserID" : discord_user_id,
            "DiscordUserName": discord_user_name,
            "DiscordUserTag": discord_user_tag,
            "WalletAddress": wallet_address,
            "NumberOfFunguysOwned": number_of_funguys_owned,
            "NumberOfFunguysBabyOwned": number_of_funguysbaby_owned,
            "IsItAddition": is_it_addition,
            "DateOfOldestFunguyOwned": date_of_oldest_funguy_owned
        }
          
    input_data_json = json.dumps(input_data_dict,default=str)

    try:
      if(is_it_addition is not None and number_of_funguys_owned is None):
        raise Exception('Looks like you are trying to change your number of funguys owned, please add a number as well.')
      if(number_of_funguys_owned is not None):
        assert (type(number_of_funguys_owned) == int), "Number of Funguys owned must be a number"
      if(date_of_oldest_funguy_owned is not None):
        assert (type(date_of_oldest_funguy_owned) == date), "Date of Oldest Funguy owned must be a date (YYYY-MM-DD)"

      sql = """\
      EXEC [dbo].[UpdateFunguyUserProc] @Data=?
      """
      params = (input_data_json)
      self.cursor = self.conn.cursor()
      self.cursor.execute(self.noCount + sql, params)    
      output_json_data = self.cursor.fetchall()
      self.cursor.commit()
      self.cursor.close()
      del self.cursor
      return output_json_data
    except Exception as e:
      output_data_dict = {
        'STATUS': 0,
        'ErrorMsg': e
      }
      
      output_json_data = json.dumps(output_data_dict)    
      return output_json_data
      
  async def insert_airdrop_signin(
    self,
    discord_user_id: int
  ):

    """
      '[
        { 
          "DiscordUserID" : "2"
        }
      ]'
    """

    input_data_dict = {
            "DiscordUserID" : discord_user_id
        }
        
    input_data_json = json.dumps(input_data_dict)
    try:
      sql = """\
      EXEC [dbo].[InsertAirdropSignInTblProc] @Data=?
      """
      params = (input_data_json)
      self.cursor = self.conn.cursor()
      self.cursor.execute(self.noCount + sql, params)    
      output_json_data = self.cursor.fetchall()      
      self.cursor.commit()
      self.cursor.close()
      del self.cursor
      return output_json_data
    except Exception as e:
      output_data_dict = {
        'STATUS': 0,
        'ErrorMsg': e
      }
      output_json_data = json.dumps(output_data_dict)    
      return output_json_data

  async def update_airdrop_currentMonth(
    self,
    discord_user_id: int
  ):
    """
      '[
        { 
          "DiscordUserID" : "2"
        }
      ]'
    """
    input_data_dict = {
        "DiscordUserID" : discord_user_id
    }
        
    input_data_json = json.dumps(input_data_dict)

    try:
      sql = """\
      EXEC [dbo].[UpdateAirDropMasterTblIsCurrentProc]
      """
      params = (input_data_json)      
      self.cursor = self.conn.cursor()
      self.cursor.execute(self.noCount + sql)    
      output_json_data = self.cursor.fetchall()      
      self.cursor.commit()
      self.cursor.close()
      del self.cursor      
      return output_json_data
    except Exception as e:
      output_data_dict = {
        'STATUS': 0,
        'ErrorMsg': e
      }
      output_json_data = json.dumps(output_data_dict)    
      return output_json_data

  async def calculate_TSHY_coins(
    self,
    airdrop_name:str,
    discord_user_id: int
  ):
    """
      '[
        { 
          "AirdropName" : "January 2022 - Tuschay Coin ($TSHY) Airdrop",
          "DiscordUserID": "3"
        }
      ]'
    """
    input_data_dict = {
        "AirdropName" : airdrop_name,
        "DiscordUserID": discord_user_id
    }
          
    input_data_json = json.dumps(input_data_dict)
    try:
      assert(type(airdrop_name) == str), "Airdrop Name must not be a string name"

      sql = """\
      EXEC [dbo].[CalculateTSHYCoinProc] @Data=?
      """
      params = (input_data_json)
      self.cursor = self.conn.cursor()
      self.cursor.execute(self.noCount + sql,params)    
      output_json_data = self.cursor.fetchall()
      self.cursor.commit()
      self.cursor.close()
      del self.cursor      
      return output_json_data
    except Exception as e:
      output_data_dict = {
        'STATUS': 0,
        'ErrorMsg': e
      }
      output_json_data = json.dumps(output_data_dict)    
      return output_json_data

if __name__ == '__main__':
    db = DB()

