"""
Parse Swedish city data from SCB in excel format to JSON format
"""
import json
import pandas as pd

file_name = r"C:\Users\JerryL\Documents\Aptiv\Python\Projects\jobfinder\jobfinder\dbhandler\collectors\data\mi0810_2017a01_tatorter2015.xlsx"
xl = pd.ExcelFile(file_name)
df = xl.parse(skiprows=11)
df = df.iloc[1:]

with open('swedish_cities.json', 'w') as f:
	json.dump(df.Kommunnamn.unique().tolist(), f)

if __name__ == '__main__':
	import sys
	if sys.argv == 2:
		file_name = sys.argv[1]

