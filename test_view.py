"""Testing view  funciton"""
from unittest import TestCase
from app import app
from models import db, Airdrop, User
from flask import session, Flask, g

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///airdrops_test_db'
app.config['SQLALCHEMY_ECHO'] = False
app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['DONT-SHOW-DEBUG-TOOLBAR']
app.config['WTF_CSRF_ENABLED'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.debug = True

db.drop_all()
db.create_all()

class AirdropsViewsTestCase(TestCase):
    """Test for Airdrops view function"""
    def setUp(self):
        """Add ongoing, upcoming and ended projects"""
        
        # delete existing data from tables
        Airdrop.query.delete()
        User.query.delete()
        
        #Create new airdrops 
        bitcoin = Airdrop(project_name='Bitcoin', description='Decentralized Currency', status='ONGOING', coin_name='BTC', coin_slug='BTCUSD', coin_symbol='B', start_date='09-02-2022', end_date='09-03-2022', total_prize=1000000, winner_count=1000, project_link='Satoshi Nakamoto')
        ethereum = Airdrop(project_name='Etherium', description='World Computer', status='UPCOMING', coin_name='ETH', coin_slug='ETHUSD', coin_symbol='E', start_date='09-03-2022', end_date='09-04-2022', total_prize=1000000, winner_count=1000, project_link='Vitalik Butterin')
        polymath = Airdrop(project_name='Polymath', description='Tokinization of real world assets', status='ENDED', coin_name='POLY', coin_slug='POLYUSD', coin_symbol='P', start_date='09-03-2021', end_date='09-04-2021', total_prize=1000000, winner_count=1000, project_link='Charles Wakoski')
        #Add and commit to database
        db.session.add(bitcoin)
        db.session.add(ethereum)
        db.session.add(polymath)
        db.session.commit()
    
    def test_homepage(self):
        """Test homepage view function"""
        with app.test_client() as client:
            resp = client.get('/')
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Ongoing Airdrops', html)
            self.assertIn(' <p class="view_all"><a href="/airdrops/ongoing"> View All </a></p>', html)
            
            self.assertIn('Upcoming Airdrops', html)
            self.assertIn('<p class="view_all"><a href="/airdrops/upcoming"> View All </a></p>', html)
            
            self.assertIn('Ended Airdrops', html)
            self.assertIn('<p class="view_all"><a href="/airdrops/ended"> View All </a></p>', html)
        
    def test_ongoing_Airdrops(self):
        """Test Ongoing Airdrops view function"""
        with app.test_client() as client:
            resp = client.get('/airdrops/ongoing')
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 class="table-header"> Ongoing Airdrops</h1>', html)
    
    def test_upcoming_Airdrops(self):
        """Test Upcoiming Airdrops"""
        with app.test_client() as client:
            resp = client.get('/airdrops/upcoming')
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 class="table-header"> Upcoming Airdrops </h1>', html)
            
    def test_ended_Airdrop(self):
        """Test Ended Airdrop"""
        with app.test_client() as client:
            resp = client.get('/airdrops/ended')
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 class="table-header"> Ended Airdrops </h1>', html)
                    
    def test_airdropProject(self):
        """Test individual airdrop project"""
        with app.test_client() as client:
            resp = client.get('/airdrops/project/1')
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<div  class="col-12 d-flex justify-content-center mt-4 project-details"> Project Details </div>', html)
            
    def test_signUp_newUser_form(self):
        """Test SignUp new user GET form"""
        with app.test_client() as client:
            resp = client.get('/signup')
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 class="signup-header"> Create New Account </h1>', html)
            
    def test_signUp_createNewUser(self):
        """Test signUp new User. POST"""
        with app.test_client() as client:
            resp = client.post('/signup', follow_redirects=True, data={'username': 'testuser', 'email':'test1@gmail.com', 'password':'testpassword1!'})            
            html = resp.get_data(as_text=True)
            
            # query user from db
            user = User.query.all()
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Account Created', html)
            # Test if user in sessions
            self.assertEqual(session["CURR_USER_KEY"] , user[0].id)
            
    def test_logOut(self):
        """test logout viwe function"""
        with app.test_client() as client:
            resp = client.post('/logout',  follow_redirects=True)
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('No User found', html)
        
    def test_login(self):
        """Test Login route"""
        with app.test_client() as client:
            #  sign up new user
            user1 = User.register(username='testUser', 
                                    password='testpassword1', email='test@gmail.com')
            #add user to database
            db.session.add(user1)
            db.session.commit()
            
            # query user
            u1 = User.query.filter(User.username == 'testUser').first()
            
            # login user
            resp = client.post('/login', follow_redirects=True,
                                data={'username':'testUser', 'password':'testpassword1'})
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'Welcome Back {u1.username}!',html)
            
    def test_favorite_List(self):
        """Test Favorite List"""
        with app.test_client() as client:
            #create user
            user1 = User.register(username='testUser', 
                                    password='testpassword1', email='test@gmail.com')
            #add user to database
            db.session.add(user1)
            db.session.commit()
            
            #sign in user to access user favorites
            resp = client.post('/login', follow_redirects=True,
                                data={'username':'testUser', 'password':'testpassword1'})
            
            #user favorite route
            resp = client.get('/bitdrops/favorites/list')
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Favorite Projects',html)
            
    def test_search(self):
        """Test search feature"""
        with app.test_client() as client:
            resp = client.get('/search?search=Vow')
            html = resp.get_data(as_text=True)
                
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Search Results',html)
        
        
        
        
        
        
        
        
        
        
            
            
            
            

