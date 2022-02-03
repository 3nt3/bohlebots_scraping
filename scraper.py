from bs4 import BeautifulSoup
import requests
from datetime import datetime
import sqlite3
from sys import stdout
import time

db = sqlite3.connect('lol.sqlite3')
cursor = db.cursor()

# create table
cursor.execute('''CREATE TABLE IF NOT EXISTS entries (
    id integer PRIMARY KEY AUTOINCREMENT ,
    name varchar(50),
    opened_at TIMESTAMP,
    UNIQUE(name, opened_at) 
    )''')
db.commit()

while True:
    print("[ * ] querying... ", end="")
    r = requests.get('http://bohlebots.de/door/liste.php')
    if not r.ok:
        print(f"http request failed with status {r.status_code}")
        exit()
    print(f"status {r.status_code}")

    entries = []

    print("[ * ] parsing... ")
    soup = BeautifulSoup(r.text, 'html.parser')
    for table in soup.find_all('table'):
        trs = []

        for tr in table.find_all('tr'):
            trs.append(tr)

        for i, tr in enumerate(trs):
            tds = tr.find_all('td')
            if tds[0].text.strip() != "":
                print(f"[ * ] row {i}/{len(trs)-2}", end='\r')
                entry = (tds[0].text.strip(), datetime.strptime(
                    tds[1].text.strip(), '%Y-%m-%d-%H-%M-%S').timestamp())

                cursor.executemany(
                    '''INSERT OR IGNORE INTO entries (name, opened_at) VALUES (?, ?) ''', [entry])
        print('')

    db.commit()
    time.sleep(1)

db.close()
