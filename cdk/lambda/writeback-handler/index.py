import os
import psycopg2

print("Loading function")

DATABASE_HOST = os.environ.get('DATABASE_HOST')
DATABASE_USER = os.environ.get('DATABASE_USER', 'postgres')
DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD', 'postgres')

def handler(event, context):
    # print("Received event: " + json.dumps(event, indent=2))
    for record in event["Records"]:
        # print(record['eventID'])
        # print(record['eventName'])
        # print("DynamoDB Record: " + json.dumps(record['dynamodb'], indent=2))
        conn = None
        try:
            conn = psycopg2.connect(host=DATABASE_HOST, user=DATABASE_USER, password=DATABASE_PASSWORD)
            cur = conn.cursor()

            zip_code = record["dynamodb"]["Keys"]["zip_code"]["S"]
            latitude = record["dynamodb"]["NewImage"]["latitude"]["S"]
            longitude = record["dynamodb"]["NewImage"]["longitude"]["S"]
            city = record["dynamodb"]["NewImage"]["city"]["S"]
            state = record["dynamodb"]["NewImage"]["state"]["S"]
            county = record["dynamodb"]["NewImage"]["county"]["S"]
            print("ZIPCODE:" + zip_code)
            print("CITY:" + city)

            query = """INSERT INTO public.zipcodes (zip_code, latitude, longitude, city, state, county) VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (zip_code) DO UPDATE SET (zip_code, latitude, longitude, city, state, county) = (EXCLUDED.zip_code, EXCLUDED.latitude, EXCLUDED.longitude, EXCLUDED.city, EXCLUDED.state, EXCLUDED.county) ;"""
            data = (zip_code, latitude, longitude, city, state, county)

            cur.execute(query, data)
            conn.commit()
            cur.close()

        except (Exception, psycopg2.DatabaseError) as error:
            print("ERROR: ")
            print(error)
        finally:
            if conn is not None:
                conn.close()
            print(query)
            return ("OK", 200)
    return "Successfully processed {} records.".format(len(event["Records"]))