import pymysql


def db_query(db, sql, params):
    # Connect to MySQL
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='seoakey1009!',
        charset='utf8',
        db=db
    )
    try:
        # create Dictionary Cursor
        with conn.cursor() as cursor:
            sql_query = sql
            # excute SQL
            cursor.execute(sql_query, params)
        # commit data
        conn.commit()
    finally:
        conn.close()


def create_db():
    # CREATE school DB
    sql = 'CREATE DATABASE school'
    db_query(db=None, sql=sql, params=None)


def create_table():
    # CREATE student table
    sql = '''
        CREATE TABLE student (
            id int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
            email varchar(255) NOT NULL,
            password varchar(255) NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    '''
    db_query(db='school', sql=sql, params=None)


def insert_student(email, password):
    sql = 'INSERT INTO student (email, password) VALUES (%s, %s)'
    params = (email, password)
    db_query(db='school', sql=sql, params=params)


def select_student(email):
    conn = pymysql.connect(
        host='0.0.0.0',
        user='root',
        password='seoakey1009!',
        charset='utf8',
        db='school'
    )
    sql = 'SELECT * FROM student WHERE email = %s'
    params = (email,)

    try:
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            result = cursor.fetchone()
            print(result)
        conn.commit()
    finally:
        conn.close()


def update_email(new, old):
    sql = 'UPDATE student SET email = %s WHERE email = %s'
    params = (new, old)
    db_query(db='school', sql=sql, params=params)


def delete_student(email):
    sql = 'DELETE FROM student WHERE email = %s'
    params = (email,)
    db_query(db='school', sql=sql, params=params)
