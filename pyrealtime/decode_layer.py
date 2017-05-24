from pyrealtime.layer import TransformMixin, ThreadLayer, MultiOutputMixin
import numpy as np


def comma_decoder(data):
    data = np.array([float(x) for x in data.decode('utf-8').split(',')])
    return data


class DecodeLayer(TransformMixin, MultiOutputMixin, ThreadLayer):
    def __init__(self, port_in, decoder=comma_decoder, port_names=None, *args, **kwargs):
        super().__init__(port_in, *args, **kwargs)
        self.decode = decoder
        if port_names is not None:
            for port_name in port_names:
                self._register_port(port_name)

    def post_init(self, data):
        decoded = self.decode(data)
        if isinstance(decoded, dict):
            for port_name in decoded.keys():
                self._register_port(port_name)

    def transform(self, data):
        data_dict = self.decode(data)
        return data_dict


class BufferLayer(TransformMixin, ThreadLayer):
    def __init__(self, port_in, buffer_size=10, *args, **kwargs):
        super().__init__(port_in, *args, **kwargs)
        self.buffer_size = buffer_size
        self.use_np = False
        self.buffer = None

    def post_init(self, data):
        import numpy as np
        if isinstance(data, np.ndarray):
            self.use_np = True

        if self.use_np:
            import numpy as np
            n_channels = data.shape[-1]
            self.buffer = np.zeros((self.buffer_size, n_channels))
        else:
            self.buffer = [None] * self.buffer_size

    def transform(self, data):
        if self.use_np:
            self.buffer[0:-1,:] = self.buffer[1:,:]
            self.buffer[-1,:] = data
        else:
            self.buffer[0:-1] = self.buffer[1:]
            self.buffer[-1] = data

        return self.buffer
