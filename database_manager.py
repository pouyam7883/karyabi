import mysql.connector
import config

def get_db_connection():
    '''this function return connection to database'''

    try:
        connection = mysql.connector.connect(
            host=config.MYSQL_HOST,
            user=config.MYSQL_USER,
            password=config.MYSQL_PASS,
            database=config.MYSQL_DATABASE
        )
        return connection
    except mysql.connector.Error as e:
        print(f"[-] Error connecting to database: {e}")
        return None