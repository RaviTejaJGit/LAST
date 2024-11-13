import csv
import os

async def find(element):
    if os.path.exists('urls.csv'):
        with open('urls.csv', mode='r', newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == element:
                    return True
    return False