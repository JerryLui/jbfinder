class jfinder(object):
	"""
	Retrieves job offers from companies using Teamtailor as their career page service and 
	filters them by keywords and locations.
	"""

	def __init__(self, service='teamtailor'):
		"""
		Parameters
		------------
		service : str
			Job service provider
		"""
		self.service = service
		
	### WORKER FUNCTIONS ###
	def crawl(self, company, url):
		"""
		Requests and retrieves job data from company
		
		Parameters
		----------
		company : str
			Name of company
		url : str
			Url to the company's career page
			
		Returns
		----------
		list or None
			A list containing all the available jobs as [job_title, job_id, job_dept, job_loc]
		"""
		import requests
		from bs4 import BeautifulSoup
		
		# Check if data is up to date
		jobs_req = 'jobs?department_id=&location_id='       # Query all jobs all locations
		page = requests.get(url + jobs_req, verify = False) # Request all available jobs

		# Find job listings
		soup = BeautifulSoup(page.content, 'html.parser')
		jobs = soup.find('ul', {'class':'jobs'})
		if not jobs:    # Return None if no jobs available
			return None 
		jobs = jobs.find_all('li') 
		
		result = []
		for job in jobs:
			meta = job.find('span', {'class':'meta'}).get_text().title().split(' – ')
			job_title = job.find('span', {'class':'title'}).get_text().title()
			job_id = job.find('a')['href'].split('/')[-1].split('-')[0]
			job_dept = meta[0]
			job_loc = (meta[1] if len(meta) > 1 else None)
			result.append([job_title, job_id, job_dept, job_loc])
				
		return result
		
	def filter_offers(self, offers, keywords=[]):
		'''
		Filters through offers by keywords in offer title and dept
		
		Parameters
		----------
		offers : list[tuple]
			List of tuples formatted as (title, id, loc, dept, company, url)
		keywords : list[str]
			List of keyword strings to match by
		
		Returns
		----------
		list or None
			A list of offers with relevant title and dept (title, id, loc, dept, company, url), None if no match
		
		'''
		# Return all if no keywords are sepcified
		if not keywords: return offers
		
		
		def contains(string, keywords):
			for key in keywords:
				if key in string:
					return True
			return False
			
		results = []
		for offer in offers:
			if contains(offer[2], keywords) or contains(offer[0], keywords):
				results.append(offer)
		
		return (results if results else None)
		
	def to_html(self, offers, keywords=[], locations=[], file_name='jobs.html', open_browser=True):
		'''
		Writes offers to html file
		
		Parameters
		----------
		offers : list[tuple]
			List of tuples formatted as (title, id, loc, dept, company, url)
		keywords : list[str]
			List of keywords used for filtering
		locations : list[str]
			List of locations used for filtering
		file_name : str
			Path to file for writing
		'''
		# Format locations for html
		if locations:
			locations = str.join(', ', locations)
		else:
			locations = 'All'
		
		# Format keywords for html
		if keywords:
			keywords = str.join(', ', keywords)
		else:
			keywords = 'None'
		
		# Format offer for html
		offer_templ = '''<tr>
			<td>
				<strong>%s</strong><br>
				<a href='%s'>%s</a><br>
				%s - %s
			</td>
		</tr>
		'''
		
		c_offers = ''
		# offer = (title, id, loc, dept, company, url)
		for offer in offers:
			c_offers = c_offers + offer_templ % (offer[4], offer[5] + '/jobs/' + str(offer[1]), 
											offer[0], offer[3], offer[2])
		
		# HTML Template
		html_templ = '''<!DOCTYPE html>
		<html lang="en">
			<head>
				<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-alpha.6/css/bootstrap.min.css">
			</head>
			<body>
				<div class="containter col-md-4">
					<h3>Job offers</h3>
					<p>Locations: %s</p>
					<p>Keywords: %s</p>
					<table class="table table-striped">
						<thead>
							<tr>
								<th>Offers</th>
							</tr>
						</thead>
						<tbody>
							%s
						</tbody>
					</table>
				</div>
			</body>
		</html>
		''' % (locations, keywords, c_offers)
		
		# Write html to file
		with open(file_name, 'w+') as f:
			f.write(html_templ)
		
		# Open job file in browser
		if open_browser:
			import webbrowser, os
			webbrowser.open('file://' + os.path.realpath(file_name))
		
		