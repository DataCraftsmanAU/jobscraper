from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import time
import re
import openpyxl
from datetime import datetime
from urllib.parse import urlparse

from credentials import *
from config import *

def linkedin_job_search(driver):
    """Runs linkedin.com specific web scraping."""
    
    # linkedin.com specific search variables
    worktypes = ['F','C']

    #quick = '&f_AL=true'
    quick = ''
    
    try:
        df = pd.ExcelFile('linkedinjobs.xlsx').parse('Sheet1')
    except:
        print("No Historical Data")
        df = pd.DataFrame()

    def listjobs(worktype, search):
        for listing in (range(1,25)):
            body = driver.find_element(By.CSS_SELECTOR, f'.scaffold-layout__list-container > li:nth-child({listing})')
            driver.execute_script("arguments[0].scrollIntoView();", body)
            listingText = driver.find_element(By.CSS_SELECTOR, f'.scaffold-layout__list-container > li:nth-child({listing})').text.split('\n')
            try:
                date = datetime.today().date()
            except:
                date = ""
            try:
                jobTitle = listingText[0]
            except:
                jobTitle = ""
            try:
                company = listingText[1]
            except:
                company = ""
            try:
                location = listingText[2]
            except:
                location = ""
            try:
                url = driver.find_element(By.CSS_SELECTOR, f'.scaffold-layout__list-container > li:nth-child({listing})')
                url = url.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
                parsed_url = urlparse(url)
                link = parsed_url.scheme + "://" + parsed_url.netloc + parsed_url.path
            except:
                link = ""
                
            job_data.append({'date': date, 'Work Type': worktype, 'Search Term': search, 'Job Title': jobTitle, 'Company Name': company, 'Location': location, 'Salary': 0, 'Link': link, 'Details': ""})
    
    job_data = []        
    # Navigate to the LinkedIn login page
    driver.get('https://www.linkedin.com/login')

    # Wait for the page to load
    time.sleep(2)

    # Fill in the login form
    print("Logging In")
    username = driver.find_element(By.ID,'username')
    username.send_keys(LINKEDIN_ACCOUNT)
    password = driver.find_element(By.ID,'password')
    password.send_keys(LINKEDIN_PASSWORD)
    password.submit()

    print("Loading Jobs")
    driver.get('https://www.linkedin.com/jobs/collections/recommended')
    time.sleep(2)

    for search in range(len(SEARCHES)):
        for worktype in worktypes:
            print(f'https://www.linkedin.com/jobs/search/?currentJobId=3710578757{quick}&f_JT={worktype}&geoId=101452733&keywords=%22{SEARCHES[search]}%22&location=Australia&refresh=true&sortBy=DD')
            driver.get(f'https://www.linkedin.com/jobs/search/?currentJobId=3710578757{quick}&f_JT={worktype}&geoId=101452733&keywords=%22{SEARCHES[search]}%22&location=Australia&refresh=true&sortBy=DD')
            time.sleep(3)
            jobCount = 0
            try:   
                if driver.find_element(By.CSS_SELECTOR, 'body > div.application-outlet > div.authentication-outlet > div.scaffold-layout.scaffold-layout--breakpoint-xl.scaffold-layout--list-detail.scaffold-layout--reflow.scaffold-layout--has-list-detail.jobs-search-two-pane__layout > div > div.scaffold-layout__row.scaffold-layout__header > div > h1').text:
                    print("No Jobs Found.")
                    continue
            except:
                print("Jobs Found.")
            resultCount = int(driver.find_element(By.XPATH, '//*[@id="main"]/div/div[1]/header/div/small').text.split()[0])
            print(resultCount)
            while resultCount > jobCount:
                try:
                    listjobs(worktype, SEARCHES[search])
                    jobCount += 25
                    driver.get(f'https://www.linkedin.com/jobs/search/?currentJobId=3710578757{quick}&f_JT={worktype}&geoId=101452733&keywords=%22{SEARCHES[search]}%22&location=Australia&refresh=true&sortBy=DD&start={jobCount}')
                    time.sleep(3)
                except:
                    jobCount = resultCount 

    newdata = pd.DataFrame(job_data)
    df_merged = pd.concat([df,newdata], ignore_index=True)
    df_merged = df_merged.drop_duplicates(subset=['Link'])
    df_merged['Work Type'] = df_merged['Work Type'].replace({'F': 'full-time', 'C': 'contract-temp'})
    df_merged.to_excel('linkedinjobs.xlsx', index=False)