
#install these with 'pip install -r requirements.txt'
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import threading
import time
import re
import openpyxl
from datetime import datetime
from urllib.parse import urlparse

#these files are created in this same folder. config.py and credentials.py
from credentials import *   # will have your LINKEDIN_ACCOUNT and LINKEDIN_PASSWORD variables stored as strings.
from config import *        # will have your search variables.

def init_driver():
    driver = webdriver.Chrome()
    return driver

def seek_job_search(driver):
    """Runs seek.com.au specific webscraping and then parses the salary text to attempt to normalise it for PA."""
    
    # seek.com.au specific search variables
    job_data = []
    lastpage = False
    minimumSalary = '150000'
    worktypes = ['full-time','contract-temp']
    #daterange = 'daterange=7&'
    daterange = ''
    
    try:
        df = pd.ExcelFile('seekjobs.xlsx').parse('Sheet1')
    except:
        print("No Historical Data")
        df = pd.DataFrame()

    def listjobs(worktype, search):
        job_listings = driver.find_elements(By.XPATH, '//*[@id="app"]/div/div[4]/div/section/div[2]/div/div/div[1]/div/div/div[3]/div/div/div/div/div')
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
                location = listing.find_element(By.CSS_SELECTOR, 'div:nth-child(1) > span > a').text
                print(location)
            except:
                location = ""
            try:
                salary = listing.find_element(By.CSS_SELECTOR, 'div:nth-child(2) > div > span > span').text
                print(salary)
            except:
                salary = ""
            try:
                url = listing.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
                parsed_url = urlparse(url)
                link = parsed_url.scheme + "://" + parsed_url.netloc + parsed_url.path
            except:
                link = ""
            try:
                details = (listing.find_element(By.CSS_SELECTOR, 'div:nth-child(1) > div > div:nth-child(3) > div > span').text + listing.find_element(By.CSS_SELECTOR, 'div:nth-child(1) > div > div:nth-child(4) > div > span').text)
            except:
                try:
                    details = (listing.find_element(By.CSS_SELECTOR, 'div:nth-child(1) > div > div:nth-child(3) > div > span').text)
                except:
                    try:
                        details = (listing.find_element(By.CSS_SELECTOR, 'div:nth-child(1) > div > div:nth-child(4) > div > span').text)
                    except:
                        details = ""
                
            job_data.append({'date': date, 'Work Type': worktype, 'Search Term': search, 'Job Title': jobTitle, 'Company Name': company, 'Location': location, 'Salary': salary, 'Link': link, 'Details': details})

    def extract_number(text):
        if text is None:
            return None
        try:
            #matches = re.findall(r'\$\s*([0-9,.kpd]+)', text)
            matches = re.findall(r'\b(?:\$|K|k|p\.d|inclusive maximum rate|plus super|incl super)?\s*([0-9,.kpd]+)', text)
            print("Pattern Match")
            print(matches)
        except:
            return None
        if matches:
            print("Matches True")
            try:
                if "k".upper() in matches[1].upper():
                    matches[1] = re.findall('\d+', matches[1])
                    if "," in matches[1]:
                        matches[1] = re.sub(",", "", matches[1])
                    
                    matches[1][0] = re.search('\d+', matches[1][0]).group()
                    print("Case: 1")
                    print(int(matches[1][0]) * 1000)
                    return int(matches[1][0]) * 1000
                else:
                    matches[1] = re.sub(",", "", matches[1])
                    if "," in matches[1]:
                        matches[0] = re.sub(",", "", matches[1])
                    
                    matches[1] = re.search('\d+', matches[1]).group()
                    print("Case: 2")
                    print(matches[1])
                    print(int(matches[1]))
                    return int(matches[1])
            except:
                try:
                    print(matches[0][0])
                    if "k".upper() in matches[0].upper():
                        matches[0] = re.findall('\d+', matches[0])
                        if "," in matches[0]:
                            matches[0] = re.sub(",", "", matches[0])
                            
                        matches[0][0] = re.search('\d+', matches[0][0]).group()
                        print("Case: 3")
                        print(int(matches[0][0]) * 1000)
                        return int(matches[0][0]) * 1000
                    else:
                        if "," in matches[0]:
                            matches[0] = re.sub(",", "", matches[0])
                        
                        matches[0] = re.search('\d+', matches[0]).group()
                        print("Case: 4")
                        print(matches[0])
                        print(int(matches[0]))
                        return int(matches[0])
                except:
                    print("Failed")
                    return None
        print("Failed")
        return None

    def calculate_result(salary):
        print("Salary Text")
        print(salary)
        number = extract_number(salary)
        print("Extracted Salary")
        print(number)
        if number is None:
            return 0
        if number > 5000:
            multiplier = 1
        elif number > 400:
            multiplier = 5 * 48
        elif number > 25:
            multiplier = 5 * 48 * 8
        else:
            multiplier = 5 * 48 * 8 * 100
        print("Converted Salary")
        print(number * multiplier)
        print("----")
        return number * multiplier

    for search in range(len(SEARCHES)):
        for worktype in worktypes:
            driver.get(f'https://www.seek.com.au/jobs/{worktype}?{daterange}keywords=%22{SEARCHES[search]}%22&salaryrange={minimumSalary}-&salarytype=annual&worktype=243%2C242%2C244')
            time.sleep(0.5)
            lastpage = False
            while lastpage == False:
                try:
                    listjobs(worktype, SEARCHES[search])
                    next = driver.find_element(By.XPATH,'//*[@id="app"]/div/div[4]/div/section/div[2]/div/div/div[1]/div/div/div[6]/nav/ul/li[last()]/a')
                    next.click()
                    time.sleep(0.5)
                except:
                    lastpage = True

        newdata = pd.DataFrame(job_data)
        df_seek = pd.concat([df,newdata], ignore_index=True)
        df_seek = df_seek.drop_duplicates(subset=['Link'])
        df_seek['Salary Calculation'] = df_seek['Salary'].apply(lambda x: calculate_result(x) if x is not None else None)
        df_seek.to_excel("seekjobs.xlsx", index=False)

def linkedin_job_search(driver):
    """Runs linkedin.com specific web scraping."""
    
    # linkedin.com specific search variables
    job_data = []
    worktypes = ['F','C']

    #quick = '&f_AL=true'
    quick = ''
    
    try:
        df = pd.ExcelFile('linkedinjobs.xlsx').parse('Sheet1')
    except:
        print("No Historical Data")
        df = pd.DataFrame()

    def linkedInJobSearch(worktype, search):
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
                    linkedInJobSearch(worktype, SEARCHES[search])
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

if __name__ == "__main__":
    driverLinkedin = init_driver()
    driverSeek = init_driver()
    
    seek_thread = threading.Thread(target=seek_job_search, args=(driverSeek,))
    linkedin_thread = threading.Thread(target=linkedin_job_search, args=(driverLinkedin,))

    seek_thread.start()
    linkedin_thread.start()

    seek_thread.join()
    linkedin_thread.join()
    
    try:
        df_linkedin = pd.ExcelFile('linkedinjobs.xlsx').parse('Sheet1')
        df_seek = pd.ExcelFile('seekjobs.xlsx').parse('Sheet1')
        
        df_linkedin['Source'] = "LinkedIn"
        df_seek['Source'] = "Seek"
        
        df_combined = pd.concat([df_seek, df_linkedin], ignore_index=True)
        df_combined.to_excel('jobs.xlsx', index=False)
    except:
        print("Error loading data")
    