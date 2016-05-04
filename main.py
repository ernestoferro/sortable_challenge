import csv
import re
from collections import defaultdict
from models import read_data, Product, Listing


def find_word(word, text):
    return bool(re.search(r'\b' + re.escape(word) + r'\b', text))


def score(product, listing):
    manufacturer_score = 2 * find_word(product.normalized_manufacturer, listing.normalized_title)
    family_score = 10 * find_word(product.normalized_family, listing.normalized_title)
    model_score = 50 * find_word(product.normalized_model, listing.normalized_title)
    return manufacturer_score + family_score + model_score


def main():
    product_json_fields = 'product_name manufacturer model family announced-date'.split()
    listing_json_fields = 'title manufacturer currency price'.split()
    product_buckets = defaultdict(set)
    products = list(read_data('data/products.txt', Product, product_json_fields))

    for product in products:
        for token in product.tokens:
            product_buckets[token].add(product)

    to_review_listings = []
    to_review_listings_accessories = []

    for listing in read_data('data/listings.txt', Listing, listing_json_fields):
        candidates = set()
        for token in listing.tokens:
            candidates.update(product_buckets[token])

        potential_products = []
        for candidate in candidates:
            match_score = score(candidate, listing)
            if match_score > 60:
                potential_products.append(candidate)

        if len(potential_products) == 1:
            product = potential_products[0]
            product.listings.add(listing)
        elif len(potential_products) == 0:
            to_review_listings.append(listing)
        else:
            to_review_listings_accessories.append((listing, potential_products))  # accessory?

    print('unmatched listings', len(to_review_listings))
    print('unmatched listings (maybe accessories)', len(to_review_listings_accessories))

    with open('links.csv', 'w') as csvfile:
        fieldnames = ['product', 'listing']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for product in products:
            product_cell = '{}, {}, {}'.format(product.manufacturer, product.family, product.model)
            if not product.listings:
                writer.writerow({'product': product_cell, 'listing': 'MISSING'})
                continue

            writer.writerow({'product': product_cell})
            for listing in product.listings:
                writer.writerow({'listing': listing.title})

    with open('unmatched_listings.csv', 'w') as csvfile:
        fieldnames = ['listing', 'accessories']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for listing in to_review_listings:
            writer.writerow({'listing': listing.title})

        for listing, potential_products in to_review_listings_accessories:
            writer.writerow({
                'listing': listing.title,
                'accessories': ' ### '.join(p.name for p in potential_products)
            })


if __name__ == '__main__':
    main()
