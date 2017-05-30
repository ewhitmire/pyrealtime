import time

from pyrealtime.layer import ProducerMixin, ThreadLayer


class DummyInputLayer(ProducerMixin, ThreadLayer):
    def __init__(self, data_producer, rate, *args, **kwargs):
        super().__init__( *args, **kwargs)
        self.data_producer = data_producer
        self.rate = rate

    def get_input(self):
        time.sleep(1.0/self.rate)
        data = self.data_producer()
        self.tick()
        return data
