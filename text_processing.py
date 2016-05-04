import re


def normalize_text(text, sep=' '):
    text = text.lower().replace('_', sep)
    return re.sub(r'[^a-zA-Z0-9/-]+', sep, text)


def tokenize(text):
    return set(normalize_text(text).split())


def tokenize_field(text):
    tokens = set(normalize_text(text).split())
    return set(tokens | {
        token.rename('-') for token in tokens if '-' in tokens
    })
