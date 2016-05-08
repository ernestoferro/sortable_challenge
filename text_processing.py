import re


def standardize_text(text):
    text = re.sub(r'[_\/,]', ' ', text.lower())
    return re.sub(r'[^\. a-zA-Z0-9/-]+', '', text)


def normalize_text(text):
    tokens = standardize_text(text).split()

    extra_tokens = []
    for token in tokens:
        if '-' in token:
            extra_tokens.append(token.replace('-', ''))
            extra_tokens.append(token.replace('-', ' '))
    return ' '.join(tokens + extra_tokens)


def tokenize_field(text):
    text = standardize_text(text)
    tokens = {text}

    if '-' in text:
        tokens.add(text.replace('-', ' '))
        tokens.add(text.replace('-', ''))
    if ' ' in text:
        tokens.add(text.replace(' ', ''))
    return tokens


def find_word(word, text):
    # this used to be a regex, but this is much faster
    return (
        (' ' + word + ' ') in text or
        text.startswith(word + ' ') or
        text.endswith(' ' + word) or
        word == text
    )
