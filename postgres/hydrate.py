import psycopg2
conn = psycopg2.connect("host=localhost dbname=zipcodes user=postgres")
cur = conn.cursor()
with open('../data/USCities.csv', 'r') as f:
    next(f) # Skip the header row.
    cur.copy_from(f, 'zipcodes', sep=',')
conn.commit()