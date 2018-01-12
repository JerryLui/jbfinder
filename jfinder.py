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
    def crawl_jobs(self, company, url):
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
        jobs_req = '/jobs?department_id=&location_id='      # Get all jobs from all locations
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