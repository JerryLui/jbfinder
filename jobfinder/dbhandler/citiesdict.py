from .dbhandler import DBHandler
import json

"""
For future implementation of a better location dict.
"""

city_file = 'collectors/data/swedish_cities.json'

with open(city_file, 'r') as f:
    cities = json.load(f)

cities.extend(['New York', 'Chicago', 'Los Angeles', 'Miami', 'Washington',
               'São Paulo', 'London', 'Edinburgh', 'Berlin', 'Munich', 'Leipzig',
               'Helsinki', 'Oslo', 'Copenhagen', 'Reykjavík', 'Warsaw', 'Amsterdam',
               'Bristol', 'Sydney'])

