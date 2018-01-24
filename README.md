# jbfinder

A lot of companies use a third party service as their Career Page which means the same crawler can be used for companies using the same service. I have gathered some of the companies using Teamtailor as seen in teamtailor.json.

- jobs.html output from program
- main.py edit keywords and locations by your preference
- jdbhandler.py handles communication with the SQLite database
- jfinder.py helper class for main
- google_teamtailor.py used to gather list of companies using teamtailor using Google's api

In main.py I have written some quick code to update the db and print out offers of interest based on given keywords and locations. 

*I do realize that a db isn't really necessary and the code can be written much shorter, but where's the fun in that.*

## TODO:
- Update for concurrent retrieval
- Add industry branches to DB for better filtering
- Clean Location Table, and improve insert_location method in jfinder
- Improve insert_job method in jdbhandler to only update entry last_seen instead of creating new (DB)
- Futher expand Company table.
    ex. Google "site:karriar.* teamtailor"

- Create crawler for REKRY
- Create crawler for Jobvite https://www.jobvite.com/
- Create crawler for 50skills https://www.50skills.com/
- Create crawler for workable https://www.workable.com/
- Create crawler for northzone http://www.ventureloop.com/northzone/
