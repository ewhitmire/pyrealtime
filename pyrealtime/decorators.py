from functools import wraps, update_wrapper, partial

from pyrealtime import TransformLayer


def method_dec(decorator):
    """
    Converts a function decorator into a method decorator
    """
    def _dec(func):
        def _wrapper(self, *args, **kwargs):
            def bound_func(*args2, **kwargs2):
                return func(self, *args2, **kwargs2)
            # bound_func has the signature that 'decorator' expects i.e.  no
            # 'self' argument, but it is a closure over self so it can call
            # 'func' correctly.
            return decorator(bound_func)(*args, **kwargs)
        return wraps(func)(_wrapper)
    update_wrapper(_dec, decorator)
    # Change the name, to avoid confusion, as this is *not* the same
    # decorator.
    _dec.__name__ = 'method_dec(%s)' % decorator.__name__
    return _dec


def transformer(f=None, **kwargs):
    # If called without method, we've been called with optional arguments.
    # We return a decorator with the optional arguments filled in.
    # Next time round we'll be decorating method.
    if f is None:
        return partial(transformer, **kwargs)
    if 'name' not in kwargs:
        kwargs['name'] = 'transformer'
    @wraps(f)
    def wrapper(input_layer, *args, **kwds):
        transform_layer = TransformLayer(input_layer, *args, transformer=f, **kwds, **kwargs)
        return transform_layer
    return wrapper

# def transformer(f, **kwargs):
#     # @wraps(f)
#     # def wrapper(input_layer, *args, **kwds):
#     #     transform_layer = TransformLayer(input_layer, *args, transformer=f, **kwds, **kwargs)
#     #     return transform_layer
#
#     def wrap(f):
#         print("Inside wrap()")
#
#         def wrapped_f(input_layer, *args, **kwds):
#             transform_layer = TransformLayer(input_layer, *args, transformer=f, **kwds, **kwargs)
#             return transform_layer
#
#         return wrapped_f
#
#     return wrap
#     # return wrapper