from models import User, Airdrop, db, Reminder
from app import app

#create tables
db.drop_all()
db.create_all()


