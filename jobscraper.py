#install these with 'pip install -r requirements.txt'
from selenium import webdriver
import pandas as pd
import threading

#these files are created in this same folder. config.py and credentials.py
from config import *        # will have your search variables.
from seek import *
from salary import *

def init_driver():
    driver = webdriver.Chrome()
    return driver

if __name__ == "__main__":
    driverSeek = init_driver()
    seek_thread = threading.Thread(target=seek_job_search, args=(driverSeek,))
    seek_thread.start()
    seek_thread.join() 
    
    try:
        df_seek = pd.ExcelFile('seekjobs.xlsx').parse('Sheet1')
        df_seek['Salary Calculation'] = df_seek['Salary'].apply(lambda x: calculate_result(x) if x is not None else None)
        df_seek.to_excel('jobs.xlsx', index=False)
    except:
        print("Error loading data")