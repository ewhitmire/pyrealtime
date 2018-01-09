from pyrealtime import ThreadLayer, TransformMixin


class ExponentialFilter(TransformMixin, ThreadLayer):

    def __init__(self, *args, alpha, **kwargs):
        super().__init__(*args, **kwargs)
        self.alpha = alpha
        self.prev = None

    def transform(self, data):
        if self.prev is None:
            self.prev = data
        new = data * self.alpha + self.prev * (1-self.alpha)
        self.prev = new
        return new



class SOSFilter(TransformMixin, ThreadLayer):

    def __init__(self, port_in, sos, *args, **kwargs):
        self.sos = sos
        import scipy.signal
        self.state = scipy.signal.sosfilt_zi(sos)
        super().__init__(port_in, *args, **kwargs)

    def transform(self, data):
        import scipy.signal
        y, new_state = scipy.signal.sosfilt(self.sos, data, zi=self.state)
        self.state = new_state
        return y