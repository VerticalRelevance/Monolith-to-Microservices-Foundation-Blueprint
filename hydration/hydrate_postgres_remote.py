import psycopg2

conn = psycopg2.connect("host=54.163.127.52 user=postgres password=postgres")
cur = conn.cursor()

# cur.execute("""
# set AUTOCOMMIT on""")

cur.execute(
    """

-- DROP TABLE IF EXISTS public.zipcodes;

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

"""
)


with open("../data/USCities.csv", "r") as f:
    next(f)  # Skip the header row.
    cur.copy_from(f, "zipcodes", sep=",")
conn.commit()
