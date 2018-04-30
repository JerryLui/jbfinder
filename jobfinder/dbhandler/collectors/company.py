'''
Quick way to gather sites using Teamtailor with Google Custom Search API.
Note this is limited by Google to 100 entries, meaning max 10 pages with 10 results each page.
'''


## Loads key from single line keyfiles
def load_key(filename=''):
    if not filename: return None
    with open(filename, 'r') as f:
        return f.read()


## Load companies from json file
import json
import requests


def load_companies(filename='teamtailor.json'):
    with open(filename, 'r') as f:
        d = json.load(f)
    return d


# Get existing companies
company_dict = load_companies()
# Personal api key and cse id
api_key = load_key('cfg/api_key.hidden')
cse_id = load_key('cfg/cse_id.hidden')

## Avoid duplicate urls	
url_set = set(company_dict.values())


## Adds JSON content to dictionary
def add_to_dict(content):
    results = json.loads(content)
    for result in results['items']:
        title = result['htmlTitle'].split('-')[0].strip()
        print(title)
        if not company_dict.get(title, 0):
            real_url = requests.get('http://' + result['displayLink'], verify=False).url
            if real_url in url_set:  # Checked second to title because anoter request is requied
                print('Already in set!')
                return
            print(real_url)
            company_dict[title] = real_url  # Add to dict
            url_set.add(real_url)  # Add to url_set
        else:
            print('Already in dict!')
        print('-' * 40)


## API Request URL
url = ('https://www.googleapis.com/customsearch/v1?'
       'q=site%3A*.teamtailor.com'  # Query: site:*.teamtailor.com
       '&cx={}'  # cse_id
       '&start={}'  # index of result
       '&key={}')  # api_key

for i in range(2, 92, 10):
    r = requests.get(url.format(cse_id, i, api_key))
    print('\nQuery %s to %s' % (str(i), str(i + 10)))
    add_to_dict(r.content)

## Add locations to location database
## NOTE: Still requires some manual scrubbing
from jdbhandler import jdbhandler


def db_add_companies(dbh, c_dict):
    for company, url in c_dict.items():
        dbh.insert_company(company, url)
    dbh.commit()


dbh = jdbhandler()
db_add_companies(dbh, company_dict)
dbh.close()
