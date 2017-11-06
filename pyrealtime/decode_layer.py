from pyrealtime.layer import TransformMixin, ThreadLayer, MultiOutputMixin
import numpy as np


def comma_decoder(data):
    """A simple parser that splits data by commas

    :param string data: data to parse
    :return: numpy array of floats
    :rtype: np.ndarray
    """
    try:
        data = np.array([float(x) for x in data.split(',')])
    except ValueError:
        return None
    return data


class DecodeLayer(TransformMixin, MultiOutputMixin, ThreadLayer):
    """Decode Layer

    """
    def __init__(self, port_in, decoder=comma_decoder, port_names=None, *args, **kwargs):
        super().__init__(port_in, *args, **kwargs)
        self.decode = decoder
        if port_names is not None:
            for port_name in port_names:
                self._register_port(port_name)

    # def post_init(self, data):
    #     decoded = self.decode(data)
    #     if isinstance(decoded, dict):
    #         for port_name in decoded.keys():
    #             self._register_port(port_name)

    def transform(self, data):
        """

        :param data:
        :return:
        """
        data_dict = self.decode(data)
        return data_dict

