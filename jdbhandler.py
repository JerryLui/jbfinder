class jdbhandler(object):
    '''
    Overlay for handling data communications
    '''
    
    ''' 
    TODO: 
        Add Company Branches for a better filter
    '''
    def __init__(self, file='db/finder.sqlite'):
        '''
        Initiates a connection to database
        '''
        import sqlite3
        import atexit
        
        self.file = file
        self.conn = sqlite3.connect(self.file)
        self.cur = self.conn.cursor()
        
        ## Translate cities into English
        self.loc_dict = {'Göteborg':'Gothenburg',
                         'København':'Copenhagen',
                         'Lund':'Lund'}
        
        ## Doesn't work...
        def close():
            self.conn.close()
        
        atexit.register(close)
    
    def get_cursor(self):
        '''
        Returns connection cursor
        '''
        return self.cur
    
    def get_locdict(self):
        '''
        Returns location dictionary
        '''
        return self.loc_dict

    def commit(self):
        '''
        Commits changes in connection
        '''
        self.conn.commit()
    
    def close(self):
        '''
        Closes the connection
        '''
        self.conn.close()
    
    def insert_job(self, title, job_id, location_id, dept_id, company_id):
        '''
        Inserts job into Job table

        Parameters
        ----------
        title : str
            Job title
        job_id : int
            Internal id of input job
        location_id : int
            id number of location in Location table
        dept_id : int
            id number of department in Departments table
        company_id : int
            id number of company in Company table
        '''
        self.cur.execute('''INSERT OR REPLACE INTO Job (title, job_id, location_id, dept_id, company_id) 
                    VALUES (?, ?, ?, ?, ?)''',
                   (title, job_id, location_id, dept_id, company_id))


    def insert_company(self, company, url):
        '''
        Inserts company and url into Company table

        Parameters
        ----------
        company : str
            Name of company
        url : str
            Url to companies career site

        Returns
        ----------
        int
            The id number of given company
        '''
        self.cur.execute('''INSERT OR IGNORE INTO Company (name, url) VALUES (?, ?)''',
                   (company.title(), url))
        self.cur.execute('''SELECT id FROM Company WHERE name = ?''', (company,))
        return self.cur.fetchone()

    def insert_location(self, location):
        '''
        Inserts location to Location table

        Parameters
        ----------
        location : str
            Name of location

        Returns
        ----------
        int
            The id number of given location
        '''
        if location is None: return None
        
        # Translates text to English
        for key in self.loc_dict:
            if key in location:
                location = self.loc_dict[key]

        self.cur.execute('''INSERT OR IGNORE INTO Location (name) VALUES (?)''', (location,))
        self.cur.execute('''SELECT id FROM Location WHERE name = ?''', (location,))
        return self.cur.fetchone()

    def insert_department(self, department):
        '''
        Inserts a department to Department table

        Parameters
        ----------
        department : str
            Name of department

        Returns
        ----------
        int
            The id number given department
        '''
        if department is None:
            return None
        
        self.cur.execute('''INSERT OR IGNORE INTO Department (name) VALUES (?)''', (department,))
        self.cur.execute('''SELECT id FROM Department WHERE name = ?''', (department,))
        return self.cur.fetchone()

    def get_companies(self):
        '''
        Gets all the companies in the DB with id, name, url

        Returns
        --------
        list
            A list of tuples containing the companies formatted as (id, name, url)
        '''
        self.cur.execute('''SELECT * FROM Company''')
        return self.cur.fetchall()
    
    def get_locations(self):
        '''
        Gets all locations in DB
        
        Returns
        --------
        list
            A list of tuples contaning locations formatted as (id, name)
        '''
        self.cur.execute('''SELECT * FROM Location''')
        return self.cur.fetchall()
    
    def get_departments(self):
        '''
        Gets all departments in DB
        
        Returns
        --------
        list
            A list of tuples containing departments formtted as (id, name)
        '''
        self.cur.execute('''SELECT * FROM Departmen''')
        return self.cur.fetchall()

    def get_all_jobs(self):
        '''
        Gets all jobs in DB ordered by company name and job id
        
        Returns
        --------
        list
            A list of tuples containing jobs formatted as (title, id, loc, dept, company, url)
        '''
        self.cur.execute('''
            SELECT 
                Job.title, Job.id, Location.name, Department.name, Company.name, Company.url
            FROM 
                Job JOIN Location JOIN Department JOIN Company
            ON 
                Job.location_id = Location.id AND 
                Job.dept_id = Department.id AND
                Job.company_id = Company.id
            ORDER BY 
                Company.name, Job.id
        ''')
        return self.cur.fetchall()
    
    def get_offers(self, locations = []):
        '''
        Gets a list of all jobs at location in locations.
        Since python SQLite3 doesn't have FTS3 keyword filtering has to be done in Python.
		
		Returns
		--------
		list
			A list of tuples containing jobs formatted as (title, id, loc, dept, company, url)
        '''
        if len(locations) < 1:
            return self.get_all_jobs()
        
        qst = '?'
        placeholder = ', '.join(qst for e in locations)
        query = '''
            SELECT 
                Job.title, Job.id, Location.name, Department.name, Company.name, Company.url
            FROM 
                Job JOIN Location JOIN Department JOIN Company
            ON 
                Job.location_id = Location.id AND 
                Job.dept_id = Department.id AND
                Job.company_id = Company.id
            WHERE
                Location.name IN (%s)
            ORDER BY 
                Company.name, Job.id
            ''' % placeholder
        self.cur.execute(query, locations)
        return self.cur.fetchall()
        
    
    # Unsafe delim
    def clear_old_jobs(self):
        '''
        Deletes jobs older than 7 days
        '''
        dlim = '-7 day'
        self.cur.execute('''DELETE FROM Job WHERE last_seen < DATE('now', ?)''', (dlim,))
        
    
    def create_db(self):
        '''
        Creates DB Schema
        '''

        # DB Schema
        self.cur.executescript('''
        --DROP TABLE IF EXISTS Job;
        --DROP TABLE IF EXISTS Company;
        --DROP TABLE IF EXISTS Location;
        --DROP TABLE IF EXISTS Department;

        CREATE TABLE IF NOT EXISTS Job (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            title VARCHAR(255),
            job_id INTEGER,
            last_seen DATETIME DEFAULT CURRENT_DATE,

            -- Foreign Keys
            company_id INTEGER,
            dept_id INTEGER,
            location_id INTEGER
        );

        CREATE UNIQUE INDEX unq_job ON Job (title, job_id, company_id)

        CREATE TABLE IF NOT EXISTS Company (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            name VARCHAR(255) UNIQUE,
            url VARCHAR(2083)
        );

        CREATE TABLE IF NOT EXISTS Location (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            name VARCHAR(255) UNIQUE
        );

        CREATE TABLE IF NOT EXISTS Department (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            name VARCHAR(255) UNIQUE
        );
        ''')

        self.commit()
    
