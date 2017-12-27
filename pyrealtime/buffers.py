import numpy as np

class BaseBuffer:
    def buffer(self, data):
        raise NotImplementedError()


class Passthrough(BaseBuffer):
    def buffer(self, data):
        return data


class FixedBuffer(BaseBuffer):
    def __init__(self, buffer_size=10, shape=(1,), use_np=False):
        self.buffer_size = buffer_size
        self.use_np = use_np
        if use_np:
            self._buffer = np.zeros((buffer_size, *shape))
        else:
            self._buffer = [0] * buffer_size

        self.counter = 0

    def buffer(self, data):
        self._buffer[self.counter] = data
        self.counter += 1
        if self.counter == self.buffer_size:
            self.counter = 0
            if self.use_np:
                return np.copy(self._buffer)
            else:
                return self._buffer[:]
