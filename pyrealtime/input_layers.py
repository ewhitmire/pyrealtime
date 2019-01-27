import asyncio
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

    async def get_input(self):
        await asyncio.sleep(1./self.rate)
        data = self._generate(self.counter)
        return data


class CustomInputLayer(ProducerMixin, ThreadLayer):
    pass


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
