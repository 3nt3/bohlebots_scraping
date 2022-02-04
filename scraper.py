from bs4 import BeautifulSoup
import requests
from datetime import datetime
import sqlite3
from sys import stdout
import time
import threading
from flask import Flask
import psycopg2

db = psycopg2.connect(database="asdf", user="postgres",
                      password="asdf", host="db", port="5432")

cursor = db.cursor()

# create table
cursor.execute('''CREATE TABLE IF NOT EXISTS entries (
    id SERIAL PRIMARY KEY,
    name varchar(50),
    opened_at TIMESTAMP,
    UNIQUE(name, opened_at) 
    )''')
db.commit()

app = Flask(__name__)


@app.route('/')
def api():
    return "hello world"


def scrape():
    cursor = db.cursor()
    print("[ * ] querying... ", end="")
    r = requests.get('http://bohlebots.de/door/liste.php')
    if not r.ok:
        print(f"http request failed with status {r.status_code}")
        return
    print(f"status {r.status_code}")

    soup = BeautifulSoup(r.text, 'html.parser')
    for table in soup.find_all('table'):
        trs = []

        for tr in table.find_all('tr'):
            trs.append(tr)

        for i, tr in enumerate(trs):
            tds = tr.find_all('td')
            if tds[0].text.strip() != "":
                entry = (tds[0].text.strip(), datetime.strptime(
                    tds[1].text.strip(), '%Y-%m-%d-%H-%M-%S'))

                cursor.execute(
                    '''INSERT INTO entries (name, opened_at) VALUES (%s, %s) ON CONFLICT DO NOTHING ''', (entry[0], entry[1]))

    db.commit()


threading.Timer(5, scrape).start()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)

db.close()
