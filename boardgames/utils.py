import unidecode


def format_str(user_str):
    return unidecode.unidecode(user_str).lower()
