#install these with 'pip install -r requirements.txt'
from selenium import webdriver
import pandas as pd
import threading
from datetime import datetime

#these files are created in this same folder. config.py and credentials.py
from credentials import *   # will have your LINKEDIN_ACCOUNT and LINKEDIN_PASSWORD variables stored as strings.
from config import *        # will have your search variables.
from seek import *
from linkedin import *
pd.set_option('mode.chained_assignment', None)

def checkJobs(driver):
    for job in range(0, len(df_seek['Link'])):
        if (df_seek['Active'][job] != 0):
            print(df_seek['Link'][job])
            driver.get(df_seek['Link'][job])
            try:
                print(driver.find_element(By.CSS_SELECTOR, '#app > div > div:nth-child(8) > div > div > div > div > div:nth-child(1) > h2').text)
                df_seek['Active'][job] = False
                df_seek['Date Removed'][job] = datetime.today().date()
            except:
                print("Still Active")

df_seek = pd.ExcelFile('seekjobs.xlsx').parse('Sheet1')
df_seek = df_seek.sort_values(by=['date'])

if 'Active' not in df_seek.columns:
    df_seek['Active'] = True
    
if 'Date Removed' not in df_seek.columns:
    df_seek['Date Removed'] = ""

driverSeek = webdriver.Chrome()
seek_thread = threading.Thread(target=checkJobs, args=(driverSeek,))
seek_thread.start()    
seek_thread.join()

print("Saving seekjobs.xlsx...")
df_seek.to_excel("seekjobs.xlsx", index=False)