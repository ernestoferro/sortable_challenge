import csv
import json
import os
import sys
from pprint import pprint


def save_for_review(products, to_review_listings):
    print('unmatched:', len(to_review_listings))
    os.makedirs('output', exist_ok=True)

    with open('output/links.csv', 'w') as csvfile:
        fieldnames = ['product', 'listing', 'price']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for product in products:
            product_cell = '{}, {}, {}'.format(product.manufacturer, product.family, product.model)
            if not product.listings:
                writer.writerow({'product': product_cell, 'listing': 'MISSING'})
                continue

            writer.writerow({'product': product_cell})
            for listing in product.listings:
                writer.writerow({'listing': listing.title, 'price': listing.price_in_cad})

    with open('output/unmatched_listings.csv', 'w') as csvfile:
        fieldnames = ['listing']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for listing in to_review_listings:
            writer.writerow({'listing': listing.title})


def compare_results(path1, path2):
    with open(path1, 'rt') as file1, open(path2, 'rt') as file2:
        for line1, line2 in zip(file1, file2):
            data1 = json.loads(line1)
            data2 = json.loads(line2)
            assert data1['product_name'] == data2['product_name']
            listings1 = set(frozenset(x.items()) for x in data1['listings'])
            listings2 = set(frozenset(x.items()) for x in data2['listings'])
            before = listings1 - listings2
            after = listings2 - listings1
            if before or after:
                print(data1['product_name'])
                print('BEFORE')
                pprint(before)
                print('-' * 40)
                print('AFTER')
                pprint(after)
                input()


if __name__ == '__main__':
    compare_results(sys.argv[1], sys.argv[2])
