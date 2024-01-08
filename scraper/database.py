import sqlite3
import json

def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except sqlite3.Error as e:
        print(e)
    return conn

def create_tables(conn):

    create_countries_table = """
    CREATE TABLE IF NOT EXISTS countries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        country_name TEXT NOT NULL,
        country_code TEXT NOT NULL,
        save_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    create_roadtrips_table = """
    CREATE TABLE IF NOT EXISTS roadtrips (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        country_id INTEGER,
        name TEXT NOT NULL,
        duration TEXT,
        price TEXT,
        save_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (country_id) REFERENCES countries (id)
    );
    """
    cursor = conn.cursor()
    cursor.execute(create_countries_table)
    cursor.execute(create_roadtrips_table)
    conn.commit()

def insert_country(conn, country_name, country_code):
    country_exists = conn.cursor().execute("SELECT id FROM countries WHERE country_name=?", (country_name,)).fetchone()
    if country_exists:
        return country_exists[0]
    else:
        sql = ''' INSERT INTO countries(country_name, country_code)
                  VALUES(?,?) '''
        cur = conn.cursor()
        cur.execute(sql, (country_name, country_code))
        conn.commit()
        return cur.lastrowid

def roadtrip_exists(conn, roadtrip_name, country_name):
    """ Vérifier si le roadtrip existe déjà dans la base de données. """
    try:
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM destinations WHERE roadtrip_name=? AND country_name=?", (roadtrip_name, country_name))
        return cur.fetchone() is not None
    except sqlite3.Error as e:
        print(f"Erreur de base de données : {e}")
        return False

def insert_roadtrip(conn, country_id, roadtrip_name, duration, price):
    if not roadtrip_exists(conn, roadtrip_name, country_id):
        sql = ''' INSERT INTO roadtrips(country_id, name, duration, price)
                  VALUES(?,?,?,?) '''
        cur = conn.cursor()
        cur.execute(sql, (country_id, roadtrip_name, duration, price))
        conn.commit()
        return cur.lastrowid
    else:
        print(f"Roadtrip '{roadtrip_name}' already exists in the database.")
        return None



def get_country_id(conn, country_name):
    try:
        cur = conn.cursor()
        cur.execute("SELECT id FROM countries WHERE country_name = ?", (country_name,))
        result = cur.fetchone()
        return result[0] if result else None
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    
def roadtrip_exists(conn, roadtrip_name, country_id):
    """ Check if the roadtrip already exists in the database. """
    try:
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM roadtrips WHERE name = ? AND country_id = ?", (roadtrip_name, country_id))
        return cur.fetchone() is not None
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False

def load_country_codes(json_file):
    with open(json_file, 'r') as file:
        return json.load(file)

def insert_countries_from_json(conn, json_file):
    countries = load_country_codes(json_file)
    for country_name, country_code in countries.items():
        insert_country(conn, country_name, country_code)

def get_all_countries(conn):
    cur = conn.cursor()
    cur.execute("SELECT country_name FROM countries")
    return [row[0] for row in cur.fetchall()]


if __name__ == '__main__':
    database = "/Users/simondaniel/Desktop/Scraping-project/scraper/data.db"
    json_file = "/Users/simondaniel/Desktop/Scraping-project/scraper/countries.json"

    conn = create_connection(database)
    with conn:
        create_tables(conn)
        insert_countries_from_json(conn, json_file)

