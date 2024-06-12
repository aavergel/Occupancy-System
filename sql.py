import mysql.connector
from mysql.connector import Error


def create_connection(hostname, user, password, database):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=hostname,
            user=user,
            password=password,
            database=database
        )
        print('Connection to Mysql DB successful')
    except Error as e:
        print(f'The error \'{e}\' has occured')
    return connection


def execute_query(conn, query):
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        conn.commit()
        print('Query executed successfully')
    except Error as e:
        print(f'The error\'{e}\' has oxxurred')


def execute_read_query(conn, query):
    cursor = conn.cursor(dictionary=True)
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f'The error \'{e}\' has occured')




