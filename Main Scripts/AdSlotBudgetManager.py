
import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime
import pandas as pd
load_dotenv()

try:
    DB_NAME = os.getenv('DB_NAME')
    DB_USER = os.getenv('DB_USER')
    DB_PASS = os.getenv('DB_PASS')
    DB_HOST = os.getenv('DB_HOST')
    DB_PORT = os.getenv('DB_PORT')

except Exception as e:
    print("Error while accessing the environment variables ")
    raise e

try:
    conn = psycopg2.connect(database = DB_NAME,user = DB_USER,password=DB_PASS,host=DB_HOST,port = DB_PORT)
    cursor = conn.cursor()

except (Exception,psycopg2.DatabaseError) as error:
    print(error)

sql_query = """SELECT * FROM online_ads.ads
                Where status = 'Active';
                """

try:
    cursor.execute(sql_query)
    data_orm = cursor.fetchall()
    print(data_orm[1])

    df = pd.read_sql(sql_query,conn)
    print(df.head(1))

except Exception as e:
    print(e)

