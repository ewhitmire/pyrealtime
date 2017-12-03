from functools import wraps

from pyrealtime import TransformLayer


def transformer(f):
    @wraps(f)
    def wrapper(input_layer, *args, **kwds):
        transform_layer = TransformLayer(input_layer, transformer=f)
        return transform_layer
    return wrapper