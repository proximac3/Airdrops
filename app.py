import os
from flask import Flask, render_template, request, flash, redirect, session, g, flash, request, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
import requests
from forms import SignupForm, LoginForm, UpdateEmployeeForm
from datetime import datetime, date
import threading
from send_email import send_notification_email
from keys import cmc_api_key

from models import db, connect_db, User, Airdrop, Favorite, Reminder
import pdb
 
CURR_USER_KEY = "curr_user"
app = Flask(__name__)
 
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgres:///airdrops_db'))
 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "parasite")
toolbar = DebugToolbarExtension(app)
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
 
connect_db(app)

#custom 404 error page
@app.errorhandler(404)
def not_foun(e):
    return render_template('404_error.html'), 404

@app.before_request
def add_user_to_g():
    """If user is logged in, add user to global object"""
    try:
        if session['CURR_USER_KEY']:
            g.user = User.query.get(session['CURR_USER_KEY'])
            session['user_favorites'] = Favorite.user_favorites(g.user.fav)
        else:
            g.user = None
    except:
        ...

# Homepage Route
@app.route('/')
def home():
    #query airdrop from DB
    ongoing = Airdrop.query.filter(Airdrop.status == 'ONGOING').limit(5)
    upcoming = Airdrop.query.filter(Airdrop.status == 'UPCOMING').limit(5)
    ended = Airdrop.query.filter(Airdrop.status == 'ENDED').limit(5)
    
    # if 'CURR_USER_KEY' in session:
    #     print(session['CURR_USER_KEY'])
    #     print(g.user)
    # else:
    #     print('User not in session')
    
    return render_template('home.html', ongoing=ongoing, upcoming=upcoming, ended=ended)

# Ongoing Airdrops route
@app.route('/airdrops/ongoing')
def ongoing_airdrops():
    #query ONGOING airdrops from database
    liveDrops = Airdrop.query.filter(Airdrop.status == 'ONGOING').all()
    return render_template('live_airdrops.html', liveDrops=liveDrops)

# upcoming airdrops route
@app.route('/airdrops/upcoming')
def upcoming_airdrops():
    #query UPCOMING airdrops
    upcoming_Drops = Airdrop.query.filter(Airdrop.status == 'UPCOMING').all()
    return render_template('upcoming_airdrops.html', upcoming_Drops=upcoming_Drops)

# ended airdrop route
@app.route('/airdrops/ended')
def ended_airdrops():
    #query ENDED airdrops 
    ended_drops = Airdrop.query.filter(Airdrop.status == "ENDED").all()
    return render_template('ended_airdrops.html', ended_drops=ended_drops)

# individual airdrop project info
@app.route('/airdrops/project/<int:project_id>')
def airdrop_project(project_id):
    #query project
    project = Airdrop.query.get(project_id)
    
    #calculate time difference
    time_left = Airdrop.time_difference(project.end_date)
    return render_template('airdrop_project.html', project=project, time=time_left)

# Sign up new User
@app.route('/signup', methods=['POST', 'GET'])
def signup():
    #create sign up form
    form = SignupForm()
    
    # Validate form
    if form.validate_on_submit():
        try:
            #register username
            user = User.register(username=form.username.data, password=form.password.data, email=form.email.data)
            
            #add user to database
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            # Notify user if username or password already taken
            db.session.rollback()
            flash('Username or Email already Taken', 'error')
            return render_template('signup.html', form=form)
        
        #add user to session
        session["CURR_USER_KEY"] = user.id
        # session['user_favorites'] = Favorite.user_favorites(g.user.fav)
        
        flash('Account Created', 'success')
        return redirect('/')
    else:
        #if form not valid, render sign up form
        return render_template('signup.html', form=form)

# Logout Route
@app.route('/logout', methods=['POST'])
def logout():
    """if user's logged in, log user out."""
    if 'CURR_USER_KEY' in session:
        session.pop('CURR_USER_KEY')
        session.pop('user_favorites')
        g.user = None
        
        flash("Loged Out Successfully", 'success')
        
        return redirect('/')  
    else:
        flash("No User found", 'error')
        return redirect('/')

# Login route
@app.route('/login', methods=['POST', 'GET'])
def logion():
    """Login and authenticate User"""
    form = LoginForm()
    
    # validate form
    if form.validate_on_submit():
         # login user 
        user = User.login(form.username.data, form.password.data)
         
        # if user Exist, put user into session
        if user:
            session["CURR_USER_KEY"] = user.id
            g.user = user
            session['user_favorites'] = Favorite.user_favorites(g.user.fav)
            flash(f'Welcome Back {user.username}!', 'success')
            return redirect('/')
        else:
            # redirect back to form with errror message
            flash('Username or Email incorrect', 'error')
            return redirect('/login')
    return render_template('login.html', form=form)


# user profile
@app.route('/bitdrops/profile/<int:id>')
def user_profile(id):
    # query user
    # user = User.query.filter(User.id == id).first()
    return render_template('profile.html')

# edit user Profile
@app.route('/bitdrops/edit/profile/<int:id>', methods=['POST', 'GET'])
def edit_user_profile(id):
    # query user
    user = User.query.filter(User.id == id).first()
    #create form
    form = UpdateEmployeeForm(obj=user)
    
    if form.validate_on_submit():
        user.username = form.username.data
        db.session.commit()
        user.email = form.email.data
        db.session.commit()
        
        return redirect('/')
    else:
        return render_template('edit_profile.html', form=form) 
    
    
#  ADD projects to favorites
@app.route('/bitdrops/favorites/add', methods=['POST'])
def add_favorites():
    # get project id 
    pid = request.json['id']
    project_name = request.json['projectName']
    
    try:
        project = Favorite(project_name=project_name, user_id=g.user.id, project_id=pid)
        db.session.add(project)
        db.session.commit()
        return (jsonify(message='Project ID Received'), 200)
    except:
        db.session.rollback()
        return (jsonify(message='ERROR Adding project to Favorites'), 200)
    
    return render_template('favorites.html')

#  remove projects to favorites
@app.route('/bitdrops/favorites/remove', methods=['POST'])
def remove_favorites():
    # get project id 
    pid = request.json['id']
    project_name = request.json['projectName']
    
    try:
        project = Favorite.query.filter(Favorite.project_id == pid, 
                                        Favorite.user_id == g.user.id).delete()
        db.session.commit()
        return (jsonify(message='Project removed from favorites'), 200)
    except:
        db.session.rollback()
        return (jsonify(message='ERROR removing project from Favorites'), 200)
    
    return render_template('favorites.html')
    


# view user favorites
@app.route('/bitdrops/favorites/list')
def view_favorites():
    #query user favorites
    user_favorites = User.query.get_or_404(g.user.id)

    return render_template('favorites.html', favorites=user_favorites.fav)


# display searched Projects on page
@app.route('/search', methods=['GET'])
def search():
    # get search word
    search1 = request.args['search']
    
    #query search word
    results = Airdrop.query.filter(Airdrop.project_name.contains(search1)).all()
    
    projects = []
    # if project in db contains searched word, query project
    if len(results) > 0:
        for element in results: 
            proj = Airdrop.query.filter(Airdrop.project_name == f'{element}').first()
            # add project to prjects list
            projects.append(proj)
        return render_template('search.html', projects=projects)
    else:
        
        return render_template('bad_search.html')

# favorite reminder route 
@app.route('/bitdrops/reminder', methods=['POST'])
def reminder():
    """Set reminder for project"""
    
    # get project data
    p_id = request.json['id']
    project_name = request.json['projectName']
    value = request.json['value']
    
    print(value)
    # query project 
    project = Airdrop.query.filter(Airdrop.id == p_id).first()
    
    # add reminder to database
    if value == 'starts':
        """Set reminder for when project starts"""
        try:
            reminder = Reminder(project_name=project_name, project_id=p_id, user_id=g.user.id, reminder_date=project.start_date, reminder=value)
            db.session.add(reminder)
            db.session.commit()
        except:
            db.session.rollback()
            return (jsonify(message='Project reminder already set for When project begins'), 201)
        
        return (jsonify(message='Project reminder Set'), 200)
    elif value == 'ends':
        """Set reminder for when project ends"""
        try:
            reminder = Reminder(project_name=project_name, project_id=p_id, user_id=g.user.id, reminder_date=project.end_date, reminder=value)
            db.session.add(reminder)
            db.session.commit()
        except:
            db.session.rollback()
            return (jsonify(message='Project reminder already set for when project ends'), 201)
        
        return (jsonify(message='Project reminder Set'), 200)
        
## About us view
@app.route('/bitdrops/aboutus')
def about_us():
    return render_template('aboutus.html')

#how to participate
@app.route('/bitdrops/participate')
def participate():
    return render_template('participate.html')

###################Application functions Below##############################
# If new airdrop is not in db then add to DB
def get_new_airdrops():
    threading.Timer(86400.0, get_new_airdrops).start()
    
    data_status = ['ONGOING', 'UPCOMING', 'ENDED']
    # Query all airdrops in database
    airdrops_in_db = Airdrop.get_all_airdrops()
    
    for element in data_status:
        #coinmarketcap API url and parameter
        url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/airdrops'
        parameters = {
            'status':f'{element}'
        }
        headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': f'{cmc_api_key}',
        }
        
        #response
        resp = requests.get(url, headers=headers, params=parameters)
        #result
        results = resp.json()
        
        # loop through airdrops from each category(ongoing, upcoming and ended)
        for element in results['data']:
            if element['project_name'] in airdrops_in_db:
                # if airdrop already in db, ignore
                ...
            else:
                # create new airdrop and commit
                newDrop = Airdrop.add_airdrop(element['project_name'], element['description'], element['status'], element['coin']['name'], element['coin']['slug'], element['coin']['symbol'], element['start_date'], element['end_date'], element['total_prize'], element['winner_count'], element['link'])
            
                if newDrop:
                    db.session.add(newDrop)
                    db.session.commit()
# get_new_airdrops()
    
# Send email reminders to users
def send_reminder():
    threading.Timer(86400.0,  send_reminder).start()
    reminder = Reminder.query.all()
    
    for element in reminder:
        if Airdrop.time_difference(element.reminder_date) <= 1:
            send_notification_email('ram.bharwani@yahoo.com', element.project_name, element.reminder)
        else:
            ...
# send_reminder()


#update project status
def update_airdrop():
    threading.Timer(90000.0, update_airdrop).start()
    
    # query Ongoing Airdrops
    ongoing = Airdrop.query.filter(Airdrop.status == 'ONGOING').all()
    
    # loop through ongoing airdrops and update status
    for element in ongoing:
        if Airdrop.time_difference(element.end_date) <= 0:
            element.status = "ENDED"
            db.session.commit()
            
    #  query upcoming airdrops
    upcoming = Airdrop.query.filter(Airdrop.status == 'UPCOMING').all()
    
    # loop through upcoming airdrops and update status
    for elem in upcoming:
        if Airdrop.time_difference(elem.start_date) <= 0:
            elem.status = "ONGOING"
            db.session.commit()    
# update_airdrop()
