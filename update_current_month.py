from database import db_commands
import json

##############
# Connect to DB
##############
db = db_commands.DB()
async def update_db():
    await db.update_airdrop_currentMonth(2)

update_db

