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