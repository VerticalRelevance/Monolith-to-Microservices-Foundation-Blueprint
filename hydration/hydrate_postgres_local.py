import psycopg2
conn = psycopg2.connect("host=localhost dbname=zipcodes user=postgres")
cur = conn.cursor()

# cur.execute("""
# set AUTOCOMMIT on""")

cur.execute("""
CREATE TABLE IF NOT EXISTS zipcodes
(
    zip_code text COLLATE pg_catalog."default" NOT NULL,
    latitude text COLLATE pg_catalog."default",
    longitude text COLLATE pg_catalog."default",
    city text COLLATE pg_catalog."default",
    state text COLLATE pg_catalog."default",
    county text COLLATE pg_catalog."default",
    CONSTRAINT zipcodes_pkey PRIMARY KEY (zip_code)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS zipcodes
    OWNER to postgres;
""")




with open('../data/USCities.csv', 'r') as f:
    next(f) # Skip the header row.
    cur.copy_from(f, 'zipcodes', sep=',')
conn.commit()