import psycopg2
#install these with 'pip install -r requirements.txt'
import pandas as pd

#these files are created in this same folder. config.py and credentials.py
from credentials import *   # stores your postgres server details
from salary import *

print("Loading seekjobs.xlsx")
#Load Excel files
df_combined = pd.ExcelFile('seekjobs.xlsx').parse('Sheet1')

df_combined['Salary Calculation'] = df_combined['Salary'].apply(lambda x: calculate_result(x) if x is not None else None)

print("Cleaning and Formatting Data")
#Type Casting
df_combined['Salary Calculation'] = df_combined['Salary Calculation'].fillna(0).astype('int64')
df_combined['date'] = df_combined['date'].apply(lambda x: x.strftime('%Y-%m-%d') if pd.notnull(x) else None)
df_combined['Date Removed'] = df_combined['Date Removed'].apply(lambda x: x.strftime('%Y-%m-%d') if pd.notnull(x) else None)

# Convert the dataframe to a list of tuples
data = df_combined.to_records(index=False).tolist()

# Establish a connection to the PostgreSQL database
print("Connecting to Database")
conn = psycopg2.connect(database=DBTYPE, user=DBUSER, password=DBPASSWORD, host=DBHOST, port=DBPORT)
# Create a new cursor object
cur = conn.cursor()

print("Inserting Data")
# Execute the INSERT statement
cur.executemany("""INSERT INTO jobscraper.jobs ("date", "Work Type", "Search Term", "Job Title", "Company Name", "Location", "Salary", "Link", "Salary Calculation", "Date Removed") 
                VALUES (%s::date,%s,%s,%s,%s,%s,%s,%s,%s::bigint,%s::date) 
                ON CONFLICT ("Link") 
                DO UPDATE SET "date" = EXCLUDED."date", "Work Type" = EXCLUDED."Work Type", "Search Term" = EXCLUDED."Search Term", "Job Title" = EXCLUDED."Job Title", "Company Name" = EXCLUDED."Company Name", "Location" = EXCLUDED."Location", "Salary" = EXCLUDED."Salary", "Link" = EXCLUDED."Link", "Salary Calculation" = EXCLUDED."Salary Calculation", "Date Removed" = EXCLUDED."Date Removed" """, data)
# Commit the changes
conn.commit()

# Close the cursor and the connection
cur.close()
conn.close()
print("Database Updated!")