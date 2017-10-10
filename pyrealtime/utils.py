from multiprocessing import queues

import multiprocessing

import os


class SharedCounter:
    def __init__(self, ctx):
        self.val = ctx.Value('i', 0)
        self.lock = ctx.Lock()

    def increment(self):
        with self.lock:
            self.val.value += 1

    def decrement(self):
        with self.lock:
            self.val.value -= 1

    @property
    def value(self):
        with self.lock:
            return self.val.value


class Queue(multiprocessing.queues.Queue):
    """ A multiprocessing queue with an accurate qsize function. This was may to get around the qsize
    NotImplementedError on MacOS. This was adapted from https://github.com/vterron/lemon and
    http://eli.thegreenplace.net/2012/01/04/shared-counter-with-pythons-multiprocessing/
    """

    def __init__(self, *args, ctx):
        super(Queue, self).__init__(*args, ctx=ctx)
        self.size = SharedCounter(ctx)

    def put(self, *args, **kwargs):
        self.size.increment()
        super(Queue, self).put(*args, **kwargs)

    def get(self, *args, **kwargs):
        data = super(Queue, self).get(*args, **kwargs)
        self.size.decrement()
        return data

    def qsize(self):
        """ Reliable implementation of multiprocessing.Queue.qsize() """
        return self.size.value

    def empty(self):
        """ Reliable implementation of multiprocessing.Queue.empty() """
        return not self.qsize()

    def __getstate__(self):
        return (self.size,) + super().__getstate__()

    def __setstate__(self, state):
        self.size = state[0]
        super().__setstate__(state[1:])
