import csv
import os
import asyncio
from clicks import click


async def append_csv(url):
    with open('urls.csv', mode='a', newline='') as file:  # Open in write mode to create a new file
        writer = csv.writer(file)
        writer.writerow([url])

async def trav_csv(page, depth):
    depth = int(depth)+1
    if os.path.exists('urls.csv'):
        with open('urls.csv', mode='r', newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                print("\n", row[0])
                await click(page, row[0], depth)  # Pass depth to click


async def find(element):
    if os.path.exists('urls.csv'):
        with open('urls.csv', mode='r', newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == element:
                    return True
    return False