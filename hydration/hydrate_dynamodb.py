import boto3
import csv
import sys

csv_file_path = "../data/USCities.csv"
table_name = "zipcodes"
db_table = boto3.resource("dynamodb").Table(table_name)


def main():
    with open(csv_file_path, newline='') as f:
        reader = csv.DictReader(f)
        reader.fieldnames = [name.lower() for name in reader.fieldnames]
        try:
            with db_table.batch_writer() as batch:
                for row in reader:
                    batch.put_item(row)
                    print(f'Writing row: {row}')
        except csv.Error as e:
            sys.exit('file {}, line {}: {}'.format(csv_file_path, reader.line_num, e))


if __name__ == "__main__":
    main()
