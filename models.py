import json
from text_processing import normalize_text, tokenize_field


class Product:
    def __init__(self, name, manufacturer, model, family, announced_date):
        self.name = name
        self.manufacturer = manufacturer
        self.model = model
        self.family = family
        self.announced_date = announced_date
        self.listings = []
        self.normalized_manufacturer = normalize_text(manufacturer)
        self.normalized_model = tokenize_field(model)
        self.normalized_name = tokenize_field(name)

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
        self.normalized_title = normalize_text(title)
        self.normalized_manufacturer = normalize_text(manufacturer)

    def as_dict(self):
        return {
            'title': self.title,
            'manufacturer': self.manufacturer,
            'currency': self.currency,
            'price': self.price
        }

    def __repr__(self):
        return str(self)

    def __str__(self):
        return 'Listing("{} {}")'.format(self.title, self.price_in_cad)


def load_models(path, cls, fields, encoding='utf-8'):
    with open(path, 'rt', encoding=encoding) as data_file:
        for line in data_file:
            data = json.loads(line)
            values = [data.get(field, '') for field in fields]
            yield cls(*values)


def save_json_by_line(path, iterable, encoding='utf-8'):
    with open(path, 'wt', encoding=encoding) as data_file:
        for data in iterable:
            data_file.write('{}\n'.format(
                json.dumps(data, ensure_ascii=False)
            ))
