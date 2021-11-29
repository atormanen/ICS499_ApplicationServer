def _alt_mro(item):
    # get type if not already type
    cls = item if isinstance(item, type) else type(item)

    # recursively build _alt_mro array
    r = [cls]
    for cls in r:
        for base in cls.__bases__:
            bases = _alt_mro(base)
            [r.append(b) for b in bases if b not in r]

    # make sure object is last
    r.remove(object)
    r.append(object)
    return r


def mro(item):
    if hasattr(item, 'mro'):
        try:
            return item.mro()
        except TypeError:  # probably type.mro() call which expects an argument
            return [item, object]
    elif hasattr(type(item), 'mro'):
        return item.__class__.mro()
    else:
        return _alt_mro(item)
