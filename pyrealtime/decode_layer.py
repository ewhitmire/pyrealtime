from pyrealtime.layer import TransformMixin, ThreadLayer
import numpy as np


def comma_decoder(data):
    """A simple parser that splits data by commas

    :param string data: data to parse
    :return: numpy array of floats
    :rtype: np.ndarray
    """
    if isinstance(data, bytes):
        data = data.decode('latin')
    try:
        data = np.array([float(x) for x in data.split(',')])
    except ValueError:
        return None
    return data