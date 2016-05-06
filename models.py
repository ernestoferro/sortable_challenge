import json
from text_processing import normalize_text, tokenize, tokenize_field


class Product:
    def __init__(self, name, manufacturer, model, family, announced_date):
        self.name = name
        self.manufacturer = manufacturer
        self.model = model
        self.family = family
        self.announced_date = announced_date
        self.listings = []
        self.normalized_manufacturer = tokenize_field(manufacturer)
        self.normalized_family = tokenize_field(family)
        self.normalized_model = tokenize_field(model)
        self.normalized_name = tokenize_field(name)
        self.tokens = tokenize(
            ' '.join([name, manufacturer, model, family])
        )

    def __repr__(self):
        return str(self)

    def __str__(self):
        return 'Product("{}")'.format(self.name)


class Listing:
    to_cad = {  # as in May 2016
        'CAD': 1.0,
        'EUR': 1.46,
        'GBP': 1.85,
        'USD': 1.27
    }

    def __init__(self, title, manufacturer, currency, price):
        self.title = title
        self.manufacturer = manufacturer
        self.currency = currency
        self.price = price
        self.price_in_cad = float(price) * Listing.to_cad[currency]
        self.tokens = tokenize(title + ' ' + manufacturer)
        self.normalized_title = normalize_text(title)
        self.normalized_manufacturer = normalize_text(manufacturer)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return 'Listing("{} {}")'.format(self.title, self.price_in_cad)


def read_data(path, cls, fields):
    with open(path, 'rt', encoding='utf-8') as data_file:
        for line in data_file:
            data = json.loads(line)
            values = [data.get(field, '') for field in fields]
            yield cls(*values)
