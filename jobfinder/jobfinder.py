from dbhandler import *

# --- EDIT HERE ---
# To ignore ssl warnings run: python -W ignore jobfinder.py
# Keywords to look for
keywords = ['Data', 'Data Science', 'Analyst', 'Intern',
            'Junior', 'Trainee', 'Sommar', 'Summer', 'Student']

locations = []

if __name__ == '__main__':
    # --- CODE HERE ---
    dbh = DBHandler()
    dbh.add_companies(dbh.load_companies())

    # Get offers
    offers = filter_offers(Database.get_offers(locations), keywords)
    generate_html(offers, keywords, locations)
