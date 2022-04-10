"""Models for User and airdrops."""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from flask_bcrypt import Bcrypt
from datetime import datetime, date

db = SQLAlchemy()

bcrypt = Bcrypt()
 
def connect_db(app):
    """Connect to database"""
    
    db.app = app
    db.init_app(app)
    
class User(db.Model):
    """User Model"""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    
    fav = db.relationship('Favorite', backref='users',cascade = "all,delete")
    
    # register new user
    @classmethod
    def register(cls, username, password, email):
        """Register new user with hashed password& return user"""
        
        # Hash Password 
        hashed = bcrypt.generate_password_hash(password)
        # turn hased key into utf-8 String
        hashed_utf8 = hashed.decode('utf8')
        
        return cls(username=username, email=email, password=hashed_utf8)
    
    #authenticate user
    @classmethod
    def login(cls, username, pwd):
        """Validate user exist and password is correct.
            Return User if valid, else return false
        """
        user = User.query.filter_by(username=username).first()
        
        if user and bcrypt.check_password_hash(user.password, pwd):
            # Return User Instance
            return user
        else:
            return False
    
    
class Airdrop(db.Model):
    """Airdrops Model"""
    __tablename__ = 'airdrops'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String, nullable=False)
    coin_name = db.Column(db.String, default='TBA')
    coin_slug = db.Column(db.String, default='TBA')
    coin_symbol = db.Column(db.String, default='TBA')
    start_date = db.Column(db.Date, default='TBA')
    end_date = db.Column(db.Date, default='TBA')
    total_prize = db.Column(db.BigInteger, default=0)
    winner_count = db.Column(db.BigInteger, default=0)
    project_link = db.Column(db.String, default='TBA')
    
    
    def __repr__(self):    
        return f'{self.project_name}'
    
    #create Airdrop
    @classmethod
    def add_airdrop(self, project,desc,stat, coin, slug, symbol,start,end, prize, count, link):
        try:
            newAirdrop = Airdrop(project_name=project, description=desc, status=stat, coin_name=coin, coin_slug=slug, coin_symbol=symbol, start_date=start, end_date=end,total_prize=prize, winner_count=count, project_link=link)
            
            #add to Database
            db.session.add(newAirdrop)
            
            return newAirdrop
        except:
            db.session.rollback()
            return False
    
    @classmethod
    def time_difference(self, end_date):
        """claculate time difference of project start date and end date"""
        start_date = date.today()
        end = end_date
        difference = end - start_date
        return difference.days
    
    @classmethod
    def get_all_airdrops(self):
        """Query and return all airdrops"""
        results = []
        airdrops = Airdrop.query.all()
        
        for element in airdrops:
            results.append(element.project_name)
        
        return  results
    
    
class Favorite(db.Model):
    """User favorites"""
    __tablename__ = 'favorites'
    
    # id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_name = db.Column(db.String, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('airdrops.id'), primary_key=True)
    
    project = db.relationship('Airdrop', backref='favorites')
    
    def __repr__(self):    
        return f'{self.project_name}'
        
    @classmethod
    def user_favorites(self, favorites):
        """List of userfavorites"""
        user_favs = [element.project_name for element in favorites]
        
        return user_favs
    
class Reminder(db.Model):
    """Reminder for users"""
    __tablename__ = 'reminder'
    
    project_name = db.Column(db.String)
    project_id = db.Column(db.Integer, db.ForeignKey('airdrops.id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    reminder_date = db.Column(db.Date, default='TBA')
    reminder = db.Column(db.String, primary_key=True)
    
    user = db.relationship('User', backref='reminder')