import queue
import time
from threading import Timer, Event

from pyrealtime.layer import ProducerMixin, ThreadLayer


class InputLayer(ProducerMixin, ThreadLayer):
    def __init__(self, frame_generator=None, rate=30, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._generate = frame_generator if frame_generator is not None else self.generate
        self.rate = rate
        self.event = Event()

    def generate(self, counter):
        return counter

    def get_input(self):
        time.sleep(1./self.rate)
        data = self._generate(self.counter)
        return data


class CustomInputLayer(ProducerMixin, ThreadLayer):
    def __init__(self, *args, **kwargs):
        super().__init__( *args, **kwargs)
        self.custom_input_queue = queue.Queue()

    def supply_input(self, data):
        self.custom_input_queue.put(data)

    def get_input(self):
        try:
            data = self.custom_input_queue.get(True, 1)
        except queue.Empty:
            return None
        return data


class OneShotInputLayer(ProducerMixin, ThreadLayer):
    def __init__(self, value, *args, **kwargs):
        super().__init__( *args, **kwargs)
        self.value = value

    def generate(self, counter):
        return counter

    def get_input(self):
        if self.counter == 0:
            return self.value
        else:
            time.sleep(1)
            return
