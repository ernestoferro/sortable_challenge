import json
from text_processing import normalize_text, tokenize


class Product:
    def __init__(self, name, manufacturer, model, family, announced_date):
        self.name = name
        self.manufacturer = manufacturer
        self.model = model
        self.family = family
        self.announced_date = announced_date
        self.listings = set()
        self.normalized_manufacturer = normalize_text(manufacturer, ' ')
        self.normalized_family = normalize_text(family, ' ')
        self.normalized_model = normalize_text(model, ' ')
        self.tokens = tokenize(
            ' '.join([name, manufacturer, model, family])
        ) | {
            self.normalized_manufacturer,
            self.normalized_family,
            self.normalized_model
        }

    def __repr__(self):
        return str(self)

    def __str__(self):
        return 'Product("{}")'.format(self.name)


class Listing:
    def __init__(self, title, manufacturer, currency, price):
        self.title = title
        self.manufacturer = manufacturer
        self.currency = currency
        self.price = price
        self.tokens = tokenize(title + ' ' + manufacturer)
        self.normalized_title = normalize_text(title, ' ')

    def __repr__(self):
        return str(self)

    def __str__(self):
        return 'Listing("{} {} {}")'.format(self.title, self.currency, self.price)


def read_data(path, cls, fields):
    with open(path, 'rt', encoding='utf-8') as data_file:
        for line in data_file:
            data = json.loads(line)
            values = [data.get(field, '') for field in fields]
            yield cls(*values)
