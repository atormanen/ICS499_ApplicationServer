from typing import Collection


def cslist(items: Collection = None, conjunction='and', *, use_oxford_comma=True, separator: str = ', ', ):
    """Creates a comma separated list"""
    if items is None:
        items = tuple()
    elif not isinstance(items, Collection):
        items = (items, )

    # a, b, and c

    # Handle single item by returning the item
    if 1 == len(items):
        return ''.join([str(item) for item in items])

    if use_oxford_comma and 2 < len(items):
        conjunction_str = f', {conjunction} '
    else:
        conjunction_str = f' {conjunction} '

    return conjunction_str.join((separator.join(items[0:-1]), items[-1]))
