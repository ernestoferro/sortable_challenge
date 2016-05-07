import numpy as np
from collections import defaultdict
from models import Product, Listing, load_models, save_json_by_line
from text_processing import find_word


def does_link(product, listing):
    # checks if any of the fields contain the other.
    # Useful for "Konica Minolta" that could be written as "Minolta"
    same_manufacturer = (
        find_word(product.normalized_manufacturer, listing.normalized_manufacturer) or
        find_word(listing.normalized_manufacturer, product.normalized_manufacturer)
    ) and find_word(product.normalized_manufacturer, listing.normalized_title)
    model_mentioned = any(
        find_word(x, listing.normalized_title)
        for x in (product.normalized_model | product.normalized_name)
    )
    return same_manufacturer and model_mentioned


def filter_accessories(data, price_ratio, selector=lambda x: x):
    if not data:
        return [], []
    data = np.array(data)
    values = np.vectorize(selector)(data)
    median = np.median(values)
    reject = values <= price_ratio * median
    keep = ~reject
    return data[keep].tolist(), data[reject].tolist()


def main():
    product_json_fields = 'product_name manufacturer model family announced-date'.split()
    listing_json_fields = 'title manufacturer currency price'.split()

    products = list(load_models('data/products.txt', Product, product_json_fields, 'utf-8'))
    listings = load_models('data/listings.txt', Listing, listing_json_fields, 'utf-8')

    to_review_listings = []
    product_buckets = defaultdict(set)

    # Group products by the words in the manufacturer field
    for product in products:
        for token in product.normalized_manufacturer.split():
            product_buckets[token].add(product)

    for listing in listings:
        # Retrieve candidates
        candidates = set()
        for token in listing.normalized_manufacturer.split():
            candidates.update(product_buckets[token])

        potential_products = [
            candidate
            for candidate in candidates
            if does_link(candidate, listing)
        ]

        # If there's one potential product for current listing, use it
        if len(potential_products) == 1:
            product = potential_products[0]
            product.listings.append(listing)
        # Else, save it for review
        else:
            to_review_listings.append(listing)

    # Remove listings if their price is under 0.3 of the median price (accessory?)
    for product in products:
        product.listings, rejected = filter_accessories(
            product.listings, 0.3, lambda x: x.price_in_cad
        )
        if rejected:
            to_review_listings.extend(rejected)

    # Save results
    save_json_by_line('results.txt', (
        {
            'product_name': product.name,
            'listings': [l.as_dict() for l in product.listings]
        }
        for product in products
    ), encoding='utf-8')


if __name__ == '__main__':
    main()
