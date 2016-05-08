import csv
import os


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
