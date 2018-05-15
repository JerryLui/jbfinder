#!/usr/bin/python
# vim: set fileencoding=UTF8 :
import sqlite3
import os
import json
import atexit

from .netcrawler import crawl


class DBHelper(object):
    """
    Higher level helper functions for Database handling.
    """

    def __init__(self, db_file=''):
        """
        Creates a handler on given db. Uses default db if not specified.

        Parameters
        ----------
        db_file : str
            File path to db file.
        """
        self.db = DatabaseAPI(db_file)
        self.path = os.path.dirname(os.path.abspath(__file__))

        atexit.register(self.close)

    def close(self):
        self.db.close()

    def save_companies(self, company_dict, file_name=''):
        if not file_name:
            file_name = os.path.join(self.path, 'collectors', 'data', 'teamtailor.json')

        with open(file_name, 'w') as f:
            json.dump(company_dict, f, indent=2)

    def load_companies(self, file_name=''):
        if not file_name:
            file_name = os.path.join(self.path, 'collectors', 'data', 'teamtailor.json')

        with open(file_name, 'r') as f:
            return json.load(f)

    def add_companies(self, companies):
        if type(companies) == str:
            companies = self.load_companies(companies)

        for company, url in companies.items():
            self.db.insert_company(company, url)
        self.db.commit()

    def update_jobs(self, company_filter, clear_old=True):
        """
        Updates job list with departments and locations.

        Parameters
        ----------
        clear_old : bool
            Wether or not to clear old data, use this during debugging.

        """
        print('Updating companies...')
        companies = self.db.get_companies()
        companies = list(filter(lambda x: x[1].lower() in map(str.lower, company_filter), companies))

        for company in companies:  # [id, name, url]
            print(company)
            if not crawl(company[1], company[2]):
                continue  # Skip if no jobs are found
            for job in crawl(company[1], company[2]):  # [job_title, job_id, job_dept, job_loc]
                dept_id = self.db.insert_department(job[2])
                loc_id = self.db.insert_location(job[3])
                self.db.insert_job(job[0], job[1], loc_id, dept_id, company[0])
            self.db.commit()

        if clear_old:
            self.db.clear_old_jobs()


class DatabaseAPI(object):
    """
    Internal API for database handling

    TODO: Make insert_job method only update last_seen date if job already exists
    TODO: Add Company Branches for a better filter
    """

    def __init__(self, file=None):
        """
        Initiates a connection to database

        Parameters
        ----------
        file : str
            Location of db file
        """
        # Get relative path to db file if no file specified.
        if not file:
            file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db', 'db.sqlite')

        self.file = file
        self.conn = sqlite3.connect(self.file)
        self.cur = self.conn.cursor()

        # For English translations of cities.
        self.loc_dict = {'Gothenburg': 'Göteborg',
                         'København': 'Copenhagen',
                         'Warszawa': 'Warsaw'}

    def commit(self):
        """
        Commits changes in connection
        """
        self.conn.commit()

    def close(self):
        """
        Closes the connection
        """
        self.conn.close()

    def insert_job(self, title, job_id, location_id, dept_id, company_id):
        """
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
        """
        self.cur.execute("""INSERT OR REPLACE INTO Job (title, job_id, location_id, dept_id, company_id) 
                            VALUES (?, ?, ?, ?, ?)""", (title, job_id, location_id, dept_id, company_id))

    def insert_company(self, company, url):
        """
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
        """
        self.cur.execute("""INSERT OR IGNORE INTO Company (name, url) VALUES (?, ?)""",
                (company, url))
        self.cur.execute("""SELECT id FROM Company WHERE name = ?""", (company,))

        comp = self.cur.fetchone()
        return comp[0] if comp is not None else None

    def insert_location(self, location):
        """
        Inserts location to Location table

        Parameters
        ----------
        location : str
            Name of location

        Returns
        ----------
        int
            The id number of given location
        """
        if location is None:
            return None

        # Translates text to English
        for key in self.loc_dict:
            if key in location:
                location = self.loc_dict[key]

        self.cur.execute("""INSERT OR IGNORE INTO Location (name) VALUES (?)""", (location,))
        self.cur.execute("""SELECT id FROM Location WHERE name = ?""", (location,))

        loc = self.cur.fetchone()
        return loc[0] if loc is not None else None

    def insert_department(self, department):
        """
        Inserts a department to Department table

        Parameters
        ----------
        department : str
            Name of department

        Returns
        ----------
        int
            The id number given department
        """
        if department is None:
            return None

        self.cur.execute("""INSERT OR IGNORE INTO Department (name) VALUES (?)""", (department,))
        self.cur.execute("""SELECT id FROM Department WHERE name = ?""", (department,))

        dept = self.cur.fetchone()
        return dept[0] if dept is not None else None

    def get_companies(self):
        """
        Gets all the companies in the DB with id, name, url

        Returns
        --------
        list
            A list of tuples containing the companies formatted as (id, name, url)
        """
        self.cur.execute("""SELECT * FROM Company""")
        return self.cur.fetchall()

    def get_locations(self):
        """
        Gets all locations in DB

        Returns
        --------
        list
            A list of tuples contaning locations formatted as (id, name)
        """
        self.cur.execute("""SELECT * FROM Location""")
        return self.cur.fetchall()

    def get_departments(self):
        """
        Gets all departments in DB

        Returns
        --------
        list
            A list of tuples containing departments formtted as (id, name)
        """
        self.cur.execute("""SELECT * FROM Department""")
        return self.cur.fetchall()

    def get_all_jobs(self):
        """
        Gets all jobs in DB ordered by company name and job id

        Returns
        --------
        list
            A list of tuples containing jobs formatted as (title, id, loc, dept, company, url)
        """
        self.cur.execute("""
            SELECT 
                Job.title, Job.job_id, Location.name, Department.name, Company.name, Company.url, Job.last_seen
            FROM 
                Job JOIN Location JOIN Department JOIN Company
            ON 
                Job.location_id = Location.id AND 
                Job.dept_id = Department.id AND
                Job.company_id = Company.id
            ORDER BY 
                Company.name, Job.id
        """)
        return self.cur.fetchall()

    def get_jobs(self, locations=None):
        """
        Gets a list of all jobs at location in locations.
        Since python SQLite3 doesn't have FTS3 keyword filtering has to be done in Python.

        Returns
        --------
        list with locations
        """
        if not locations:
            return self.get_all_jobs()

        qst = '?'
        placeholder = ', '.join(qst for e in locations)
        query = """
            SELECT 
                Job.title, Job.job_id, Location.name, Department.name, Company.name, Company.url, Job.last_seen
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
            """ % placeholder
        self.cur.execute(query, locations)
        return self.cur.fetchall()

    # Unsafe delim
    def clear_old_jobs(self):
        """
        Deletes jobs older than 7 days
        """
        limit = '-7 day'
        self.cur.execute("""DELETE FROM Job WHERE last_seen < DATE('now', ?)""", (limit,))

    def create_db(self):
        """
        Creates DB Schema
        """

        # DB Schema
        self.cur.executescript("""
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

        CREATE UNIQUE INDEX unq_job ON Job (title, job_id, company_id);

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
        """)

        self.commit()
