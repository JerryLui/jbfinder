# jbfinder

A lot of companies use a third party service as their Career Page which means the same crawler can be used for companies using the same service. I have gathered some of the companies using Teamtailor as seen in teamtailor.json.

- jdbhandler.py handles communication with the SQLite database
- jfinder.py is a crawler for jobs

In main.py I have written some quick code to update the db and print out offers of interest based on given keywords and locations. 

*I do realize that a db isn't really necessary and the code can be written much shorter, but where's the fun in that.*

### TODO:
- Store soup so that only one request per day is required
- Save as JSON
- Update for concurrent retrieval
- Expand career dict by crawling through brands and checking for following patterns
    + jobb(a).company.*
    + karriar.company.*
    + job(s).company.*
    + career(s).company.*
    + company.teamtailor.*
    
    ex. Google "site:karriar.* teamtailor"
- Create engine for Jobvite https://www.jobvite.com/
- Create engine for 50skills https://www.50skills.com/
- Create engine for workable https://www.workable.com/
- Create engine for northzone http://www.ventureloop.com/northzone/
