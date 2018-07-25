from pyrealtime import ThreadLayer, TransformMixin
import numpy as np

class ExponentialFilter(TransformMixin, ThreadLayer):

    def __init__(self, *args, alpha, batch=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.alpha = alpha
        self.batch = batch
        self.prev = None

    def transform(self, data):
        if self.batch:
            new_data = np.zeros(data.shape)
            if self.prev is None:
                self.prev = data[0, :]
            for i in range(data.shape[0]):
                new = data[i, :] * self.alpha + self.prev * (1 - self.alpha)
                self.prev = new
                new_data[i, :] = new
            return new_data

        if self.prev is None:
            self.prev = data
        new = data * self.alpha + self.prev * (1-self.alpha)
        self.prev = new
        return new



class SOSFilter(TransformMixin, ThreadLayer):

    def __init__(self, port_in, sos, *args, axis=-1, shape=(1,), **kwargs):
        self.sos = sos
        import scipy.signal
        self.axis = axis
        zi = scipy.signal.sosfilt_zi(sos)
        self.state = np.broadcast_to(np.expand_dims(zi,-1), tuple(list(zi.shape) + list(shape)))
        super().__init__(port_in, *args, **kwargs)

    def transform(self, data):
        import scipy.signal
        y, new_state = scipy.signal.sosfilt(self.sos, data, zi=self.state, axis=self.axis)
        self.state = new_state
        return y