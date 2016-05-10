from collections import defaultdict
from models import Product, Listing, load_models, save_json_by_line
from text_processing import find_word


def is_potential_match(product, listing):
    # checks if any of the fields contain the other.
    # Useful for "Konica Minolta" that could be written as "Minolta"
    same_manufacturer = (
        find_word(product.normalized_manufacturer, listing.normalized_manufacturer) or
        find_word(listing.normalized_manufacturer, product.normalized_manufacturer)
    )
    complete_name_mentioned = find_word(product.standarized_name, listing.normalized_title)
    model_mentioned = any(
        find_word(x, listing.normalized_title)
        for x in (product.tokenized_model | product.tokenized_name)
    )
    return complete_name_mentioned or (same_manufacturer and model_mentioned)


def filter_by_product_name(products, listing):
    '''
    Returns true if all tokens in the product name are found in the normalized title and
    manufacturer.
    This is useful when more than one match is found based only on the manufacturer and
    model. In this case the family can help remove the false positives. One thing to
    notice is that the name usually includes the family and sometimes the family field
    is not included.
    '''

    return list(filter(
        lambda p: all(
            token in ' '.join([listing.normalized_title, listing.normalized_manufacturer])
            for token in p.name.lower().split('_')
        ), products
    ))


def filter_accessories(data, price_ratio, selector=lambda x: x):
    if not data:
        return [], []
    values = [selector(x) for x in data]
    median = sorted(values)[len(values) // 2]  # ignoring the case for even number of elements
    keep, reject = [], []
    for value, datum in zip(values, data):
        if value <= price_ratio * median:
            reject.append(datum)
        else:
            keep.append(datum)
    return keep, reject


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
        for token in listing.tokens:
            candidates.update(product_buckets[token])

        potential_products = [
            candidate
            for candidate in candidates
            if is_potential_match(candidate, listing)
        ]

        # If there's more than one match using manufacturer and model, try to disambiguate
        # by looking for all product.name tokens in listing.title and listing.manufacturer
        if len(potential_products) > 1:
            print(potential_products)
            potential_products = filter_by_product_name(potential_products, listing)
        if len(potential_products) == 1:
            product = potential_products[0]
            product.listings.append(listing)
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
