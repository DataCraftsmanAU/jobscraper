#install these with 'pip install -r requirements.txt'
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import random
import time
import re
import openpyxl
from datetime import datetime
from urllib.parse import urlparse

from config import *

def seek_job_search(driver):
    """Runs seek.com.au specific webscraping and then parses the salary text to attempt to normalise it for PA."""
    
    # seek.com.au specific search variables
    minimumSalary = '150000'
    maximumSalary = ''
    worktypes = ['full-time','contract-temp']
    
    try:
        df = pd.ExcelFile('seekjobs.xlsx').parse('Sheet1')
    except:
        print("No Historical Data")
        df = pd.DataFrame()

    def listjobs(worktype, search):
        job_listings = driver.find_elements(By.CSS_SELECTOR, 'article')
        for listing in job_listings:
            try:
                date = datetime.today().date()
            except:
                date = ""
            try:
                jobTitle = listing.find_element(By.CSS_SELECTOR, 'h3 a').text
                print(jobTitle)
            except:
                jobTitle = ""
            try:
                company = listing.find_element(By.CSS_SELECTOR, 'span a').text
                print(company)
            except:
                company = ""
            try:
                location = listing.find_element(By.CSS_SELECTOR, 'div.snwpn00.l1r1185b.l1r118hf.l1r1186n > div:nth-child(1) > span > span:nth-child(1) > span').text
                print(location)
            except:
                location = ""
            try:
                salary = listing.find_element(By.CSS_SELECTOR, 'div:nth-child(2) > span > span').text
                print(salary)
            except:
                salary = ""
            try:
                url = listing.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
                parsed_url = urlparse(url)
                link = parsed_url.scheme + "://" + parsed_url.netloc + parsed_url.path
            except:
                link = ""
                
            job_data.append({'date': date, 'Work Type': worktype, 'Search Term': search, 'Job Title': jobTitle, 'Company Name': company, 'Location': location, 'Salary': salary, 'Link': link})
    
    job_data = []
    for search in range(len(SEARCHES)):
        for worktype in worktypes:
            driver.get(f'https://www.seek.com.au/{SEARCHES[search]}-jobs/{worktype}?salaryrange={minimumSalary}-{maximumSalary}&salarytype=annual')
            delay = random.uniform(0.5, 1.0)
            time.sleep(delay)
            lastpage = False
            while lastpage == False:
                try:
                    listjobs(worktype, SEARCHES[search])
                    next = driver.find_element(By.CSS_SELECTOR,'nav > ul > li._1wkzzau0.a1msqia6.a1msqi9v.a1msqiw > a')
                    next.click()
                    delay = random.uniform(0.5, 1.0)
                    time.sleep(delay)
                except:
                    lastpage = True
                                    
    print("Saving seekjobs.xlsx...")
    newdata = pd.DataFrame(job_data)
    df_seek = pd.concat([df,newdata], ignore_index=True)
    df_seek = df_seek.drop_duplicates(subset=['Link'])
    df_seek.to_excel("seekjobs.xlsx", index=False)