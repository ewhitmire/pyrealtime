import numpy as np

class BaseBuffer:
    def buffer(self, data):
        raise NotImplementedError()


class Passthrough(BaseBuffer):
    def buffer(self, data):
        return [data]


class FixedBuffer(BaseBuffer):
    def __init__(self, buffer_size=10, shape=(1,), axis=None, use_np=False):
        self.buffer_size = buffer_size
        self.use_np = use_np
        if use_np:
            self._buffer = np.zeros((buffer_size, *shape))
        else:
            self._buffer = [0] * buffer_size

        self.counter = 0
        self.axis = axis

    def get_len(self, data):
        if self.axis is None:
            return 1
        else:
            return min(data.shape[self.axis], self.buffer_size - self.counter)

    def buffer(self, data):
        # assert self.axis is None or data.shape[self.axis] < self.buffer_size

        new_data_len = self.get_len(data)
        to_return = []
        while new_data_len > 0:
            if self.axis is None:
                self._buffer[self.counter:self.counter+new_data_len] = data if new_data_len > 1 else [data]
                data = []
            else:
                # print(new_data_len, self.axis)
                self._buffer[self.counter:self.counter + new_data_len] = data.take(range(new_data_len), self.axis)
                data = data.take(range(new_data_len, data.shape[self.axis]), self.axis)
            self.counter += new_data_len
            if self.counter == self.buffer_size:
                self.counter = 0
                if self.use_np:
                    to_return.append(np.copy(self._buffer))
                else:
                    to_return.append(self._buffer[:])

            if self.axis is None:
                new_data_len = 0
            else:
                new_data_len = self.get_len(data)
        return to_return
