
import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime
import pandas as pd
load_dotenv()

print(f"--- Script started at {datetime.now()}---")

def redistribute_budget(row):
    """
    Calculates and returns the new current_slot_budget for a given ad campaign row.
    """
    start_date = f"{row['date_range_start']} {row['time_range_start']}"
    end_date = f"{row['date_range_end']} {row['time_range_end']}"
    
    start_date = datetime.strptime(start_date,'%Y-%m-%d %H:%M:%S')
    end_date = datetime.strptime(end_date,'%Y-%m-%d %H:%M:%S')

    current_date = datetime.now().replace(microsecond=0)
    print(current_date)
    if start_date < current_date:
        if current_date < end_date:
            remaining_time = end_date-current_date
            num_of_slots = int(remaining_time.total_seconds()/600)
            
            if num_of_slots>0:
                return round(row['budget']/num_of_slots,2)
            

    return row['current_slot_budget']
    


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

sql_query = """SELECT campaign_id,budget,
                      date_range_start,date_range_end,
                      time_range_start,time_range_end,
                      current_slot_budget
                FROM online_ads.ads
                Where status = 'Active';
            """

try:
    # cursor.execute(sql_query)
    # data_orm = cursor.fetchall()
    # print(data_orm[1])
    # print(len(data_orm))

    df = pd.read_sql(sql_query,conn)
    print(df.shape)



    print(df.columns)
    print(datetime.now().replace(microsecond=0))

    df['new_slot_budget']= df.apply(lambda x: redistribute_budget(x),axis=1)

    print(df.head(5))


    df_to_update = df[df['current_slot_budget'] != df['new_slot_budget']]
    print(df_to_update)

    if not df_to_update.empty:
        update_query = "UPDATE online_ads.ads SET current_slot_budget=%s WHERE campaign_id=%s;"
        for index,row in df_to_update.iterrows():
            cursor.execute(update_query,(row['new_slot_budget'],row['campaign_id']))
    
        conn.commit()

        print("Database updated Successfully!")
    else:
        print("No campaigns needed a budget update.")

except Exception as e:
    print(e)
    conn.rollback()

finally:
    conn.close()