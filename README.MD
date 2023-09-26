# Job Scraper

This project is for scraping job adverts from www.seek.com.au and www.linkedin.com. 

Unique jobs are appended to the jobs excel file each time you run it with the current date that it was found. Uniqueness was based on the URL of the job ad. 

A few other fields are saved and salaries are attempted to be normalised to PA. This is a WIP as most jobs use open strings for salary inputs...

## Setup

Clone https://github.com/MichaelJenningsAI/jobscraper.git

Open a terminal in the new folder.

Run `python -m venv venv` to create a new python virtual environment.

Create a new terminal and you should see (venv) before your folder location.

Run `pip install -r requirements.txt` to install all the required python packages to your new environment.

Update your search terms in `config.py` to match what jobs you want to search for. `%20` is required whereever a space would be.

Remove the `-removethis` from `credentials-removethis.py` and then update it with your linkedin account details, this is used for logging into the account.

## How to Run

In the terminal run the command `python jobscraper.py` to start searching for jobs!
