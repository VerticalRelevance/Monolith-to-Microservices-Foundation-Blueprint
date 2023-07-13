import boto3

csv_file_path = "../data/USCities.csv"
table_name = "zipcodes"
db_table = boto3.resource('dynamodb').Table(table_name)
line_seperator = ','


def save_to_dynamodb(column_names, values):
    item = dict()

    for idx, column_name in enumerate(column_names):
        item[column_name.lower()] = values[idx]

    return db_table.put_item(
        Item=item
    )

def handler():
    with open(csv_file_path, 'r', encoding='utf-8-sig') as f:
        column_names = next(f).strip("\n").split(line_seperator)
        for line in f:
            values = line.strip("\n").split(line_seperator)
            result = save_to_dynamodb(column_names, values)
            print(result)
    print("FINISHED IMPORT")

handler()