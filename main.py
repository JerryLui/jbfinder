## --- EDIT HERE ---
## To ignore ssl warnings run: python -W ignore main.py
## Keywords to look for
keywords = ['Data', 'Data Science', 'Analyst', 'Intern', 
            'Junior', 'Trainee', 'Sommar', 'Summer', 'Student']
			
## Locations to look for
locations = ['Gothenburg', 'Stockholm']

## --- CODE BELOW ---
import json
def save_companies(company_dict):
    with open('teamtailor.json', 'w') as f:
        json.dump(company_dict, f, indent=2)
		
def load_companies():
    with open('teamtailor.json', 'r') as f:
        company_dict = json.load(f)
		
## Add locations to location database
def db_add_companies(dbh, company_dict):
	for company, url in company_dict.items():
		dbh.insert_company(company, url)
	dbh.commit()

from jdbhandler import jdbhandler
from jfinder import jfinder
dbh = jdbhandler()
finder = jfinder()

## Crawl for jobs from all companies in Company table and put job into Job table 
for company in dbh.get_companies():    # [id, name, url]
    if not finder.crawl_jobs(company[1], company[2]): continue    # Skip if no jobs are found
    for job in finder.crawl_jobs(company[1], company[2]):
        dept_id = dbh.insert_department(job[2])    # [job_title, job_id, job_dept, job_loc]
        dept_id = (dept_id[0] if dept_id is not None else None)
        loc_id = dbh.insert_location(job[3])
        loc_id = (loc_id[0] if loc_id is not None else None)
        dbh.insert_job(job[0], job[1], loc_id, dept_id, company[0]) # HANDLE NONE

dbh.clear_old_jobs()
dbh.commit()

## Check if any keyword is in string
def contains(string, keywords):
    for key in keywords:
        if key in string: 
            return True
    return False

def print_offer(offer):     # (title, id, loc, dept, company, url)
    print(offer[4] + ':')
    print(offer[0])
    print(offer[3], '-', offer[2])
    print('Link:', offer[5] + '/jobs/' + str(offer[1]))
    print('-'*58, '\n')

## Print offers
offers = dbh.get_offers(locations)    # (title, id, loc, dept, company, url)
for offer in dbh.get_offers(locations):
    if contains(offer[0], keywords):
        print_offer(offer)
        
dbh.close()