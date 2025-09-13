import datetime
import json
from datetime import datetime


def get_countries(countries_map, cell_name, row):
    return [countries_map.get(name.strip()) for name in row.get(cell_name).split(',')] if row.get(cell_name) else []

def parse_date(value):
    if not value:
        return {'from': None}
    for date_format in ("%d.%m.%Y", "%d/%m/%Y"):
        try:
            return {'from': datetime.strptime(value, date_format).timestamp() * 1000}
        except ValueError:
            continue

    raise ValueError(f"Date format for '{value}' is not supported")

def load_template(filepath):
    print(filepath)
    return json.load(open(filepath, 'r', encoding='utf-8'))

def read_from_json(filepath: str, key: str, value: str):
    with open(filepath, 'r', encoding='utf-8') as file:
        countries = {doc[key]: doc[value] for doc in json.load(file)}
        return countries

