from dbhandler import *

# --- EDIT HERE ---
# To ignore ssl warnings run: python -W ignore jobfinder.py
# Keywords to look for
company_of_interest = ['Nepa', 'Collector', 'iZettle', 'Storytel', 'Paradox', 'Teamtailor', 'Hemnet']

keywords = ['Data', 'Data Science', 'Analyst', 'Intern',
            'Junior', 'Trainee', 'Sommar', 'Summer', 'Student']

locations = []

if __name__ == '__main__':
    db = DatabaseAPI()
    dbh = DBHelper()
    dbh.add_companies(dbh.load_companies())

    # Update db
    dbh.update_jobs(company_of_interest)

    # Get offers
    offers = filter_offers(DatabaseAPI.get_jobs(locations=locations), keywords)
    generate_html(offers, keywords, locations)
