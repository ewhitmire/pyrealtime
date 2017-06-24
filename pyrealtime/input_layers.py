import time

from pyrealtime.layer import ProducerMixin, ThreadLayer


class DummyInputLayer(ProducerMixin, ThreadLayer):
    def __init__(self, frame_generator=None, rate=30, *args, **kwargs):
        super().__init__( *args, **kwargs)
        self.frame_generator = frame_generator if frame_generator is not None else self.generate_frame
        self.rate = rate

    def generate_frame(self, counter):
        return counter

    def get_input(self):
        time.sleep(1.0/self.rate)
        data = self.frame_generator(self.counter)
        self.tick()
        return data
