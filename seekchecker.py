#install these with 'pip install -r requirements.txt'
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import threading
from datetime import datetime, timedelta

pd.set_option('mode.chained_assignment', None)

def checkJobs(driver):
    for job in range(0, len(df_seek['Link'])):
        if pd.isnull(df_seek['Date Removed'][job]):
            print(df_seek['Link'][job])
            driver.get(df_seek['Link'][job])
            try:
                print(driver.find_element(By.CSS_SELECTOR, '#app > div > div:nth-child(8) > div > div > div > div > div:nth-child(1) > h2').text)
                df_seek['Date Removed'][job] = datetime.today().date()
            except:
                print("Still Active")

print("Loading seekjobs.xlsx...")
df_seek = pd.ExcelFile('seekjobs.xlsx').parse('Sheet1')

#Deactivate fields older than 30 days
print("Removing Jobs older than 30 days")
threshold_date = datetime.today().date() - timedelta(days=30)
threshold_date = pd.to_datetime(threshold_date)
for job in range(0, len(df_seek['Link'])):
    if pd.isnull(df_seek['Date Removed'][job]):
        print(df_seek['Link'][job])
        if (df_seek['date'][job] <= threshold_date):
            df_seek['Date Removed'][job] = datetime.today().date()

if 'Date Removed' not in df_seek.columns:
    df_seek['Date Removed'] = ""

driverSeek = webdriver.Chrome()
seek_thread = threading.Thread(target=checkJobs, args=(driverSeek,))
seek_thread.start()    
seek_thread.join()

print("Finished. Saving seekjobs.xlsx...")
df_seek.to_excel("seekjobs.xlsx", index=False)