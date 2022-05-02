import os 
import cs304dbi as dbi

def insert_member(conn, user_email, user_password, user_name,institution, user_type):
    '''
    Inserts a new member into the database. 
    '''
    curs = dbi.dict_cursor(conn)
    sql = ''' INSERT INTO  member (email, password, name, institution, type)
            values (%s, %s, %s, %s, %s)
        '''
    curs.execute(sql, [user_email, user_password, user_name, institution, user_type])
    conn.commit()

def user_exists(conn, email):
    '''
    Verifies if a user already exists in the database.
    '''
    curs = dbi.dict_cursor(conn)
    sql = '''SELECT email
                    FROM member
                    WHERE email = %s'''
    curs.execute(sql, [email])
    if(curs.fetchone() is None):
        return False
    return True

def login(conn, email):
    '''
    Collects the password from the database allowing the user to login.
    '''
    curs = dbi.dict_cursor(conn)
    sql = '''SELECT email, password, name, type
                    FROM member
                    WHERE email = %s'''
    curs.execute(sql, [email])
    return curs.fetchone()

def insert_opportunity(conn, email, field, title, institution, startDate, location, 
                    experienceType, experienceLevel, description, appLink, 
                    sponsorship):
    '''
    Adds opportunity posting into database.
    '''
    curs = dbi.dict_cursor(conn)
    sql = ''' INSERT INTO  opportunity (email, field, title, institution, 
            startDate, `location`, experienceType, experienceLevel, 
            `description`, appLink, sponsorship)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) '''
    curs.execute(sql, [email, field, title, institution, startDate, location, 
                        experienceType, experienceLevel, description, appLink, 
                        sponsorship])
    conn.commit()

def insert_and_update_rating(conn,email,pid,userRating):
    '''inserts and updates '''
    curs = dbi.dict_cursor(conn)
    curs.execute('''INSERT INTO rating(email,pid,rating) VALUES (%s,%s,%s)
                            ON DUPLICATE KEY UPDATE rating = %s''', 
                            [email, pid, userRating, userRating])
    conn.commit()

def average_rating(conn,pid):
    '''compute average rating for opportunities'''
    curs = dbi.dict_cursor(conn)
    curs.execute('''SELECT avg(rating)
                FROM rating
                WHERE pid = %s''', [pid])
    dic = curs.fetchone()
    if dic['avg(rating)'] == None:
        return "None"
    avgRating = float(dic['avg(rating)'])
    return avgRating

# update overall rating of an opportunity 
def update_pid_average(conn,avgRating,pid):
    curs = dbi.dict_cursor(conn)
    curs.execute('''update opportunity set averageRating = %s
                            where pid = %s''', 
                            [avgRating, pid])
    conn.commit()

def get_opportunities(conn):
    '''
    Gets and returns all opportunities in the database.
    '''
    curs = dbi.dict_cursor(conn)
    sql = 'SELECT * FROM opportunity'
    curs.execute(sql)
    return curs.fetchall()

def get_fields(conn):
    '''
    Gets and returns all fields in the database.
    '''
    curs = dbi.dict_cursor(conn)
    sql = 'SELECT distinct field from opportunity'
    curs.execute(sql)
    return curs.fetchall()

def get_institutions_opportunity(conn):
    curs = dbi.dict_cursor(conn)
    sql = 'SELECT distinct institution from opportunity'
    curs.execute(sql)
    return curs.fetchall()

def get_professions(conn):
    curs = dbi.dict_cursor(conn)
    sql = 'SELECT distinct profession from member'
    curs.execute(sql)
    return curs.fetchall()

def get_institutions_member(conn):
    curs = dbi.dict_cursor(conn)
    sql = 'SELECT distinct institution from member'
    curs.execute(sql)
    return curs.fetchall()

def get_affiliations(conn):
    curs = dbi.dict_cursor(conn)
    sql = 'SELECT distinct `type` from member'
    curs.execute(sql)
    return curs.fetchall()

def look_oppor_title(conn, title):
    curs = dbi.dict_cursor(conn)
    sql = "select * from opportunity where title like %s"
    curs = dbi.dict_cursor(conn)
    title = '%' + title + '%'
    curs.execute(sql, [title]) 
    return curs.fetchall()

def look_oppor_field(conn, field):
    curs = dbi.dict_cursor(conn)
    sql = "select * from opportunity where field like %s"
    curs = dbi.dict_cursor(conn)
    field = '%' + field + '%'
    curs.execute(sql, [field]) 
    return curs.fetchall()

def look_oppor_institution(conn, institution):
    curs = dbi.dict_cursor(conn)
    sql = "select * from opportunity where institution like %s"
    curs = dbi.dict_cursor(conn)
    institution = '%' + institution + '%'
    curs.execute(sql, [institution]) 
    return curs.fetchall()

def get_all_members(conn):
    curs = dbi.dict_cursor(conn)
    sql = "select * from member"
    curs.execute(sql) 
    return curs.fetchall()

def get_one_member(conn,email):
    curs = dbi.dict_cursor(conn)
    sql = "select * from member where email = %s"
    curs = dbi.dict_cursor(conn)
    curs.execute(sql, [email]) 
    return curs.fetchone()

def isFavorite(conn, uid, link):
    '''Checks whether an opportunity has been favorited'''
    curs = dbi.cursor(conn)
    sql = '''select * from favorites where uid = %s and link = %s'''
    curs.execute(sql, [uid, link])
    result = curs.fetchone()
    return result != None

def addFavorite(conn, uid, link):
    '''Adds opportunity to users' list of favorites, or removes if needed'''
    curs = dbi.cursor(conn)
    curs.execute('''insert into favorites(uid, link)
                values (%s, %s);''', [uid, link])
    conn.commit()

def removeFavorite(uid, link):
    '''Removes application from users' list of favorites'''
    conn = dbi.connect()
    curs = dbi.cursor(conn)
    sql = '''delete from favorites where uid = %s and link = %s'''
    curs.execute(sql, [uid, link])
    conn.commit()

if __name__ == '__main__':
    dbi.cache_cnf()
    dbi.use('centralex_db')
    conn = dbi.connect()
    print(get_institutions_member(conn))
