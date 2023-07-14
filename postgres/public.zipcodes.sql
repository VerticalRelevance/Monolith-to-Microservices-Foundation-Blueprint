-- Table: public.zipcodes

-- DROP TABLE IF EXISTS public.zipcodes;

CREATE TABLE IF NOT EXISTS postgres.zipcodes
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

ALTER TABLE IF EXISTS postgres.zipcodes
    OWNER to postgres;