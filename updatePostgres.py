import psycopg2
#install these with 'pip install -r requirements.txt'
import pandas as pd

#these files are created in this same folder. config.py and credentials.py
from credentials import *   # will have your LINKEDIN_ACCOUNT and LINKEDIN_PASSWORD variables stored as strings.
from config import *        # will have your search variables.
from seek import *
from linkedin import *
from salary import *

#Load Excel files
df_linkedin = pd.ExcelFile('linkedinjobs.xlsx').parse('Sheet1')
df_seek = pd.ExcelFile('seekjobs.xlsx').parse('Sheet1')

#Set Source
df_linkedin['Source'] = "LinkedIn"
df_seek['Source'] = "Seek"
df_seek['Salary Calculation'] = df_seek['Salary'].apply(lambda x: calculate_result(x) if x is not None else None)

#Combine seek and linkedin
df_combined = pd.concat([df_seek, df_linkedin], ignore_index=True)

#Type Casting
df_combined['Salary Calculation'] = df_combined['Salary Calculation'].fillna(0).astype('int64')
df_combined['date'] = df_combined['date'].apply(lambda x: x.strftime('%Y-%m-%d') if pd.notnull(x) else None)
df_combined['Date Removed'] = df_combined['Date Removed'].apply(lambda x: x.strftime('%Y-%m-%d') if pd.notnull(x) else None)
df_combined['Active'] = df_combined['Active'].astype(bool)

df_combined['Source'] = df_combined['Source'].apply(lambda x: "LinkedIn" if x == "LinkedIn" else "Seek")

# Convert the dataframe to a list of tuples
data = df_combined.to_records(index=False).tolist()

# Establish a connection to the PostgreSQL database
conn = psycopg2.connect(database=DBTYPE, user=DBUSER, password=DBPASSWORD, host=DBHOST, port=DBPORT)
# Create a new cursor object
cur = conn.cursor()
# Execute the INSERT statement
cur.executemany("""INSERT INTO jobscraper.jobs ("date", "Work Type", "Search Term", "Job Title", "Company Name", "Location", "Salary", "Link", "Salary Calculation", "Active", "Date Removed", "Source") 
                VALUES (%s::date,%s,%s,%s,%s,%s,%s,%s,%s::bigint,%s::int::bool,%s::date,%s) 
                ON CONFLICT ("Link") 
                DO UPDATE SET "date" = EXCLUDED."date", "Work Type" = EXCLUDED."Work Type", "Search Term" = EXCLUDED."Search Term", "Job Title" = EXCLUDED."Job Title", "Company Name" = EXCLUDED."Company Name", "Location" = EXCLUDED."Location", "Salary" = EXCLUDED."Salary", "Link" = EXCLUDED."Link", "Salary Calculation" = EXCLUDED."Salary Calculation", "Active" = EXCLUDED."Active", "Date Removed" = EXCLUDED."Date Removed", "Source" = EXCLUDED."Source" """, data)
# Commit the changes
conn.commit()

# Close the cursor and the connection
cur.close()
conn.close()