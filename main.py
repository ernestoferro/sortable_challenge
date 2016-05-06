import csv
import numpy as np
from collections import defaultdict
from models import read_data, Product, Listing
from text_processing import find_word


def score(product, listing):
    manufacturer_score = 10 * sum(
        find_word(x, listing.normalized_title)
        for x in product.normalized_manufacturer
    ) + 50 * sum(
        find_word(x, listing.normalized_manufacturer)
        for x in product.normalized_manufacturer
    )
    family_score = 10 * sum(
        find_word(x, listing.normalized_title)
        for x in product.normalized_family
    )
    model_score = 50 * sum(
        find_word(x, listing.normalized_title)
        for x in (product.normalized_model | product.normalized_name)
    )
    return manufacturer_score + family_score + model_score


def filter_accessories(data, price_ratio, selector=lambda x: x):
    data = np.array(data)
    values = np.vectorize(selector)(data)
    median = np.median(values)
    reject = values <= price_ratio * median
    keep = ~reject
    return data[keep].tolist(), data[reject].tolist()


def main():
    product_json_fields = 'product_name manufacturer model family announced-date'.split()
    listing_json_fields = 'title manufacturer currency price'.split()
    product_buckets = defaultdict(set)
    products = list(read_data('data/products.txt', Product, product_json_fields))
    listings = read_data('data/listings.txt', Listing, listing_json_fields)
    to_review_listings = []
    to_review_listings_accessories = []

    for product in products:
        for token in product.tokens:
            product_buckets[token].add(product)

    for listing in listings:
        candidates = set()
        for token in listing.tokens:
            candidates.update(product_buckets[token])

        potential_products = []
        for candidate in candidates:
            match_score = score(candidate, listing)
            if match_score >= 100:
                potential_products.append(candidate)

        if len(potential_products) == 1:
            product = potential_products[0]
            product.listings.append(listing)
        elif len(potential_products) == 0:
            to_review_listings.append(listing)
        else:
            to_review_listings_accessories.append((listing, potential_products))  # accessory?

    for product in products:
        if product.listings:
            product.listings, rejected = filter_accessories(
                product.listings, 0.3, lambda x: x.price_in_cad
            )
        #if rejected:
            #from pprint import pprint
            #print(product)
            #input('')
            #pprint(rejected)
            #input('')
            #pprint(product.listings)
            #input('enter')

    print('unmatched listings', len(to_review_listings))
    print('unmatched listings (maybe accessories)', len(to_review_listings_accessories))

    with open('links.csv', 'w') as csvfile:
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
