import re


def normalize_text(text):
    text = text.lower().replace('_', ' ')
    return re.sub(r'[^ a-zA-Z0-9/-]+', '', text)


def tokenize(text):
    return set(normalize_text(text).split())


def tokenize_field(text):
    normalized_text = normalize_text(text)
    tokens = {normalized_text}
    if '-' in normalized_text:
        tokens.add(normalized_text.replace('-', ' '))
        tokens.add(normalized_text.replace('-', ''))
    if ' ' in normalized_text:
        tokens.add(normalized_text.replace(' ', ''))
    return tokens


def find_word(word, text):
    return (
        (' ' + word + ' ') in text or
        text.startswith(word + ' ') or
        text.endswith(' ' + word)
    )
    #return bool(re.search(r'\b' + word + r'\b', text))
