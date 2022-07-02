from urllib.parse import urljoin


def build_url(base: str, part: str, prefix=None, suffix=None):
    if prefix and suffix:
        built_part = ''.join([prefix, '/', part, '/', suffix])
    elif prefix and not suffix:
        built_part = ''.join([prefix, '/', part])
    elif not prefix and suffix:
        built_part = ''.join([part, '/', suffix])
    else:
        built_part = part
    
    complete_url = urljoin(base, built_part)
    return complete_url