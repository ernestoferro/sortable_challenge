# Sortable
A simple, yet working solution for the [Sortable challenge](http://sortable.com/challenge/).  I've worked with MDM (Master Data Management) systems from IBM/Initiate and I'm familiar with their probabilistic approach, but I decided to implement a simpler rules based approach for this solution.

The main reasons are (in no particular order):
- How unstructured the content of the listing's title field is. In the use cases I'm familiar with, the fields' content while unstructured are much simpler and follow more rules (I'm thinking about demographic fields). In those cases simple metrics like edit distance with tokenization give a good scoring mechanism. I'm not convinced it'll work out as well here. (Side note, the scores are weighted based on how unlikely the event is. For example, finding two people with John as their name is much more likely than finding two people named Rupert)
- The low number of fields that can be used to group records.
- While simpler, a rules based approach can yield fewer false positives (but at the same time it'll have more false negatives).
- And the fact that even IBM/Initiate uses a rules based approach for linking different entities (for example, linking service providers with locations). The main reason for this is the different schema of the record (Person vs Location in our example).


# Requirements
-  Python 3.3 or greater

# How to run it
    $ python3 main.py

# How it works
## Big picture
1. Create buckets of the products based on their "normalized" manufacturer.
2. Using the "normalized" manufacturer and title as keys for the product buckets, retrieve potential product candidates.
3. Analize all candidates. If exactly one match is found, add that listing to the matched product.
4. After all listings have been processed and grouped, look for false positives based on the price.  This step tries to remove accessories that have been incorrectly linked to the main product.
5. Write the final results file.

## Details
### 1. Create product buckets.

First, the manufacturer field is normalized, which basically means that uncommon characters will be removed and that words with dashes will be processed to include a version without the dashes and another with a space. For example: The normalized version of 'cyber-shot' is 'cyber-shot cybershot cyber shot'. See the unit tests and implementation for more details.

In this particular case, we are about being able to reach the products of a given manufacturer not only by its name, but also the tokens in the manufacturer field.

### 2. Retrieve product candidates.

In this step we take the manufacturer and title field, normalized them, split both of them by spaces and use those tokens as keys to retrieve the candidates to evaluate. As long as the manufacturer or part of it is mentioned, the product will be retrieve for evaluation. Notice that the data structure being used to collect the product is a set, meaning that duplicates are not a posibility.

### 3. Analyze and filter candidates. Perform linking.

The basic rule for the first round of filtering is:

If the standarized product name ('Casio_QV-5000SX' -> 'casio qv 5000sx') in found inside the standarized listing's title, then the product is considered a potential link. It is worth mentioning that this looks for complete words. Meaning that 'Model B' would not be "inside" 'Model B2'. Otherwise, if the manufacturer is the same (see the function 'is_potential_match' for more details) and any of the alternative version of the product name or model is found in the normalized listing title, then the product is also considered a potential link. For example, if the product name is 'dsc-123', then the strings 'dsc-123', 'dsc 123' and 'dsc123' will all be searched inside the listing as complete entities.

After this initial filtering, if only one product has being matched, then it is considered a link.  If more than one product is matched, a second round of filtering is performed. In this case we look for the products which names' tokens are all found inside the listing normalized title and/or manufacturer. This is useful when two products have the same manufacturer and model but different families ("Canon_IXUS_300_HS" and "Canon-ELPH-300HS").

If we still have more than one match, the listing is considered to be an accessory.

### 4. Remove false positives based on price (accessories)

At this point we have the listings grouped by product, and some of those listings might be accessories (false positives). In order to remove them, I'm assuming that accessories are cheaper than then product itself. Based on that, I take the median of all the prices, assume that represents the price of the product and then remove all listings below a given fraction of that price. This approach turned out to work quite well in practice.
