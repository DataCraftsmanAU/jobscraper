
#install these with 'pip install -r requirements.txt'
from selenium import webdriver
import pandas as pd
import threading

#these files are created in this same folder. config.py and credentials.py
from credentials import *   # will have your LINKEDIN_ACCOUNT and LINKEDIN_PASSWORD variables stored as strings.
from config import *        # will have your search variables.
from seek import *
from linkedin import *
from salary import *

def init_driver():
    driver = webdriver.Chrome()
    return driver

if __name__ == "__main__":
    
    if WEBSITES['seek']:
        driverSeek = init_driver()
    if WEBSITES['linkedin']:
        driverLinkedin = init_driver()
    if WEBSITES['seek']:
        seek_thread = threading.Thread(target=seek_job_search, args=(driverSeek,))
    if WEBSITES['linkedin']:    
        linkedin_thread = threading.Thread(target=linkedin_job_search, args=(driverLinkedin,))
    if WEBSITES['seek']:    
        seek_thread.start()
    if WEBSITES['linkedin']:    
        linkedin_thread.start()
    if WEBSITES['seek']:    
        seek_thread.join()
    if WEBSITES['linkedin']:    
        linkedin_thread.join()   
    
    try:
        df_linkedin = pd.ExcelFile('linkedinjobs.xlsx').parse('Sheet1')
        df_seek = pd.ExcelFile('seekjobs.xlsx').parse('Sheet1')
        
        df_linkedin['Source'] = "LinkedIn"
        df_seek['Source'] = "Seek"
        df_seek['Salary Calculation'] = df_seek['Salary'].apply(lambda x: calculate_result(x) if x is not None else None)
        
        df_combined = pd.concat([df_seek, df_linkedin], ignore_index=True)
        
        df_combined.to_excel('jobs.xlsx', index=False)
    except:
        print("Error loading data")