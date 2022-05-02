from flask import (Flask, render_template, make_response,
                   request, session, redirect, url_for, flash,
                   url_for, session, send_from_directory, Response)

from werkzeug.utils import secure_filename
import imghdr
import sys, os, random
import cs304dbi as dbi
import bcrypt
import queries
import random, re

app = Flask(__name__)

app.secret_key = ''.join([ random.choice(('ABCDEFGHIJKLMNOPQRSTUVXYZ' +
                                          'abcdefghijklmnopqrstuvxyz' +
                                          '0123456789'))
                           for i in range(20) ])


@app.route('/')
def index():
    '''
    Landing page. Gives background on the app and gives the user the option to 
    login or signup.
    '''
    if 'email' in session:
        return redirect(url_for('home'))
    else:
        return render_template("index.html")

@app.route('/signup/', methods=['GET', 'POST'])
def signup():
    '''
    Gives the user the signup form under the get request. 
    Collect the user's credentials and inserts the user into the database if 
    the credentials are appropriate (user must use Wellesley College email) 
    under the post request. 
    '''
    if(request.method == 'GET'):
        return render_template("signup.html")
    else:
        conn = dbi.connect()
        email = request.form.get('email')
        name = request.form.get('name')
        institution = request.form.get('institution')
        password = request.form.get('password')
        password2 = request.form.get('password2')
        user_type = request.form.get('type')

        email_pattern = re.compile('@wellesley.edu$')
        if(len(email_pattern.findall(email)) == 0):
            flash('Please use your Wellesley College email.')
            return redirect(url_for('signup'))
        
        if(password != password2):
            flash('Passwords do not match')
            return redirect(url_for('signup'))

        # if user is already in database, redirect back to login page
        if (queries.user_exists(conn, email)):
            flash('An account with this email already exists. Please login.')
            return redirect(url_for('login'))
        else:
            # create a new user with the form data.
            hashed_password = bcrypt.hashpw(password.encode('utf-8'),
                                            bcrypt.gensalt())
            stored_password = hashed_password.decode('utf-8')
            # add the new user to the database
            queries.insert_member(conn, email, stored_password, name, institution, user_type)
            session['email'] = email
        return redirect(url_for('file_upload', src=url_for('pic',email=email), email=email))

@app.route('/login/', methods=['GET', 'POST'])
def login():
    '''
    Gives the user the login form under the get request.
    With post request, it collects the user's credentials and verifies they 
    exist in the database and that their password is correct before redirecting
    them to welcome page otherwise, if credentials are incorrect, it stays on 
    the same page. It also updates the session appropriately.
    '''
    if(request.method == 'GET'):
        return render_template("login.html")

    else:
        conn = dbi.connect()
        email = request.form.get('email')
        password = request.form.get('password')        
        member = queries.login(conn, email)

        if(member is None):
            flash('Login credentials are incorrect. Please try again or sign up.')
            return redirect(url_for('login'))

        stored_password = member['password']
        hashed_password = bcrypt.hashpw(password.encode('utf-8'),
                                stored_password.encode('utf-8'))

        hashed_str = hashed_password.decode('utf-8')
                            
        if(hashed_str == stored_password):
            flash('Successfully logged in.')
            #redirect them to the page for logged in people
            session['email'] = email
            session['logged_in'] = True
            session['visits'] = 1
            return redirect(url_for('home'))
        else:
            flash('Login unsuccessful. Please try again or sign up.')
            return redirect(url_for('login'))

@app.route('/home/')
def home():
    if 'email' in session:
        return render_template('welcomePage.html')
    else:
        return redirect(url_for('index'))

@app.route('/favorite/', methods=['POST'])
def favorite():
    '''Adds or removes application from list of favorites when button is clicked.'''
    conn = dbi.connect()
    if (session.get('uid')): #if it exists
        uid = session['uid']
        # Get data from form: 
        data = request.form
        link = data['link']
        print('Link:' + link)
        # Update database
        if isFavorite(conn,uid,link) != True:
            addFavorite(conn,uid, link)
        # response dictionary
            resp_dic = {'link': link}
            print("respLink:" + resp_dic['link'])
            return jsonify(resp_dic)
    else:
        flash('You must be logged in to add to your favorites.')
        return redirect(url_for('index'))


@app.route('/logout/', methods=['GET'])
def logout():
    '''
    Logs out the current user and updates the session accordingly.
    '''
    if 'email' in session:
        email = session['email']
        session.pop('email')
        session.pop('logged_in')
        flash('You are logged out')
        return redirect(url_for('index'))
    else:
        flash('You are not logged in. Please login or join')
        return redirect(url_for('login'))

@app.route('/upload/', methods=['GET', 'POST'])
def upload():
    '''
    Gives the user an upload form to enter the required details of an opportunity
    under the get request.
    Under the post request, it collects all the form inputs and inserts the 
    opportunity into the database and redirects to the display page which
    should be updated to include the newly added opportunity.
    '''
    conn = dbi.connect()
    if(request.method == 'GET'):
        return render_template("upload.html")
    else:
        conn = dbi.connect()
        session_value = request.cookies.get('session')
        if('email' in session):
            email = session['email']
        else:
            flash('Please login again.')
            return redirect(url_for('login'))

        # code to gather experience info to add to the database
        field = request.form.get('field')
        title = request.form.get('title')
        institution = request.form.get('institution')
        startDate = request.form.get('start')
        location = request.form.get('location')
        experienceType = request.form.get('experienceType')
        experienceLevel = request.form.get('experienceLevel')
        description = request.form.get('description')
        appLink = request.form.get('link')
        sponsorship = request.form.get('sponsorship')

        queries.insert_opportunity(conn, email, field, title, institution, 
                                    startDate, location, experienceType, 
                                    experienceLevel, description, appLink, 
                                    sponsorship)
        return redirect(url_for('display'))

@app.route('/display/')
def display():
    '''
    Diplays all the available opportunities in the database.
    '''
    if('email' in session):
        conn = dbi.connect()
        opportunities = queries.get_opportunities(conn)
        fields = queries.get_fields(conn)
        institutions = queries.get_institutions_opportunity(conn)
        return render_template('display.html', opportunities=opportunities,
                                fields=fields, institutions=institutions)
    else:
        flash('Please login.')
        return render_template('login.html')


# '''rate an opportunity'''
@app.route('/rating/', methods = ["POST"])
def rating():
    if('email' in session):
        conn = dbi.connect()
        email = session['email']
        userRating = request.form.get("stars")
        pid = request.form.get("pid")
        print(pid, "pid", email, "email", userRating, "userRating")
        queries.insert_and_update_rating(conn,email,pid,userRating)
        avgRating = queries.average_rating(conn,pid)
        queries.update_pid_average(conn,avgRating,pid)
        flash("user{} is rating opportunity {} as {} stars".format(session["email"],pid,userRating))
        return redirect(url_for('display'))

    else:
        flash('Please login.')
        return render_template('login.html')

# '''rate an opportunity'''
@app.route('/search/', methods = ["GET"])
def search():
    if('email' in session):
        conn = dbi.connect()
        if request.args['kind'] == 'title':
            title = request.args['search']
            jobs = queries.look_oppor_title(conn, title)
            return render_template('display.html', opportunities=jobs)

        elif request.args['kind'] == 'field':  
            field = request.args['search']
            jobs = queries.look_oppor_field(conn, field)
            print(jobs)
            return render_template('display.html', opportunities=jobs)

        elif request.args['kind'] == 'institution':  
            institution = request.args['search']
            jobs = queries.look_oppor_institution(conn, institution)
            return render_template('display.html', opportunities=jobs)

    else:
        flash('Please login.')
        return render_template('login.html')

# Farida's code 
# page with all members of the app
@app.route('/community/', methods=['GET'])
def community():
    if('email' in session):
        conn = dbi.connect()
        members = queries.get_all_members(conn)
        professions = queries.get_professions(conn)
        affiliations = queries.get_affiliations(conn)
        institutions = queries.get_institutions_member(conn)
        return render_template("community.html", members=members, 
                                professions=professions, 
                                affiliations=affiliations,
                                institutions=institutions)
    else:
        flash('Please login.')
        return render_template('login.html')    


# Farida's code 
# page with all members of the app
@app.route('/display_member/<email>', methods=['GET'])
def display_member(email):
    if('email' in session):
        conn = dbi.connect()
        # email = request.form.get('memberEmail')
        # print("jhfsldkjfhasdfhsadklfhsadhfsdkhflasdfhjksdfhsadhf ", email)
        member = queries.get_one_member(conn,email)
        return render_template("memberPage.html", email = email, member = member)
    else:
        flash('Please login again.')
        return redirect(url_for('login'))        

@app.route('/pic/<email>')
def pic(email):
    conn = dbi.connect()
    curs = dbi.dict_cursor(conn)
    numrows = curs.execute(
        '''select filename from profilePic where email = %s''',
        [email])
    if numrows == 0:
        return send_from_directory(app.config['UPLOADS'], 'ww.jpg')
    row = curs.fetchone()
    return send_from_directory(app.config['UPLOADS'],row['filename'])

# This gets us better error messages for certain common request errors
app.config['TRAP_BAD_REQUEST_ERRORS'] = True

# new for file upload
app.config['UPLOADS'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 1*1024*1024 # 1 MB

# uploads image 
@app.route('/file_upload/', methods=["GET", "POST"])
def file_upload():
    if 'email' in session:
        email = session['email']
        if request.method == 'GET':
            return render_template('uploadPhoto.html',src=url_for('pic',email=email),email=email)
            # ,src= os.path.join(app.config['UPLOADS'],'ftahirywellesley.edu.jpg'),email='')

        if request.form["submit"] == "Upload Later":
            flash('You can update your picture on your profile page')
            return redirect(url_for('home'))

        if request.method == 'POST':
            print("does it visit here")
            try:
                f = request.files['pic']
                user_filename = f.filename
                ext = user_filename.split('.')[-1]
                user = email.split('@')[0]
                filename = secure_filename('{}.{}'.format(user,ext))
                pathname = os.path.join(app.config['UPLOADS'],filename)
                f.save(pathname)
                conn = dbi.connect()
                curs = dbi.dict_cursor(conn)
                curs.execute(
                    '''insert into profilePic(email,filename) values (%s,%s)
                    on duplicate key update filename = %s''',
                    [email, filename, filename])
                conn.commit()
                flash('Image Upload Successful')
                return redirect(url_for('home'))
                
            except Exception as err:
                flash('Upload failed {why}'.format(why=err))
                session.pop('email')
                return redirect(url_for('signup'))
    else:
        flash('signup unsuccessful')
        return redirect(url_for('signup'))

if __name__ == '__main__':
    dbi.cache_cnf()
    dbi.use('rs2_db') #centralex_db

    import os
    port = os.getuid()
    app.debug = True
    app.run('0.0.0.0',port)