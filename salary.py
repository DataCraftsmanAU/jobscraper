import pandas as pd
import re

"""Missing Edge Cases
"up to ~$180,000k + benefits"

"""

def calculate_result(salary):
    "Normalises the input to be an annual salary based on 48 weeks of work per year, 5 days per week, 8 hours per day."
    #TODO Need to scale the calculate result with the minimum salary
    number = extract_number(salary)
    if number is None:
        return 0
    if number < 2050: #Edge case for years.
        if number >= 2023:
            return None
    if number > 5000:
        multiplier = 1
    elif number > 300:
        multiplier = 5 * 48
    elif number > 25:
        multiplier = 5 * 48 * 8
    else:
        return 0
    return number * multiplier

def largerNumber(match):
    "Extracts the larger of 2 numbers out of a list."
    try:
        match = match[1]
    except:
        try:
            match = match[0]
        except:
            return None
    return match

def parseNumber(match):
    "Extracts an int out of the input string."
    match = largerNumber(match)
    match = re.findall('\d+', match)
    match = int(match[0])
    return match

def extract_number(text): 
    "Parses text to find any resemblence of a salary using regex combinations. > 90% accurate."
    try:
        text = text.upper()
        if re.findall("^[^\d]*$", text):
            #No numbers in the field
            return None
        if re.findall(r'\b\d{3},\d{3}\b', text):
            match = re.findall(r'\b\d{3},\d{3}\b', text)
            match = largerNumber(match)
            match = match.replace(",", "")
            match = int(match)
            return match
        
        if re.findall(r'\$\d+-\d+K', text):
            match = re.findall(r'\$\d+-\d+K', text)
            match = largerNumber(match)
            match = re.findall('\d+', match)
            match = largerNumber(match)
            match = int(match) * 1000
            return match
        
        if re.findall(r'\$\d+-\d+', text):
            match = re.findall(r'\$\d+-\d+', text)
            match = largerNumber(match)
            match = re.findall('\d+', match)
            match = largerNumber(match)
            match = int(match)
            if match < 500:
                match = match * 1000
            return match
        
        if re.findall(r'\d{3}K', text):
            match = re.findall(r'\d{3}K', text)
            match = parseNumber(match) * 1000
            return match
        
        if re.findall(r'\$\d{6}', text):
            match = re.findall(r'\$\d{6}', text)
            match = parseNumber(match)
            return match
        
        if re.findall(r'\$\d{4}', text):
            match = re.findall(r'\$\d{4}', text)
            match = parseNumber(match)
            return match
            
        if re.findall(r'\$\d{1}K', text):
            match = re.findall(r'\$\d{1}K', text)
            match = parseNumber(match) * 1000
            return match

        if re.findall(r'\$\d{3}', text):
            match = re.findall(r'\$\d{3}', text)
            match = parseNumber(match)
            return match
            
        if re.findall(r'\$\d{2}', text):
            match = re.findall(r'\$\d{2}', text)
            match = parseNumber(match)
            return match
        
        if re.findall(r"\$\d{1,3}(,\d{3})*", text):
            match = text.replace(",", "")
            match = re.findall(r'\$\d{4}', match)
            match = parseNumber(match)
            return match
        
        if re.findall(r'\d{6}', text):
            match = re.findall(r'\d{6}', text)
            match = parseNumber(match)
            return match
        
        if re.findall(r'\d{4}', text):
            match = re.findall(r'\d{4}', text)
            match = parseNumber(match)
            return match
        
        if re.findall(r'\d{3}', text):
            match = re.findall(r'\d{3}', text)
            match = parseNumber(match)
            return match
        
        if re.findall(r'\d{2}', text):
            match = re.findall(r'\d{2}', text)
            match = parseNumber(match)
            return match
        
        return None
    except:
        #No variables provided.
        return None