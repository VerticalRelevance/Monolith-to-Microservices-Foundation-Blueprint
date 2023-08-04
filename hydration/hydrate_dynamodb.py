import boto3
import csv
import sys
import json

csv_file_path = "../data/USCities.csv"
cdk_output_file = "../cdk/output.json"


def main():
    with open(cdk_output_file) as f:
        outputs = json.load(f)

    table_name = outputs["zipcode-microservice"]["TableName"]
    db_table = boto3.resource("dynamodb").Table(table_name)

    with open(csv_file_path, newline='') as f:
        reader = csv.DictReader(f)
        reader.fieldnames = [name.lower() for name in reader.fieldnames]
        try:
            with db_table.batch_writer() as batch:
                for row in reader:
                    batch.put_item(row)
                    print(f'Writing row: {row}')
        except csv.Error as e:
            sys.exit('file {}, line {}: {}'.format(
                csv_file_path, reader.line_num, e))


if __name__ == "__main__":
    main()
