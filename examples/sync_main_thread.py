import threading

import pyrealtime as prt
import time


class InputLayer(prt.ProducerMixin, prt.SynchronousLayer):
    def __init__(self, rate=30, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._generate = self.generate
        self.rate = rate

    def generate(self, counter):
        print(threading.current_thread(), counter, "generate")
        return counter

    def get_input(self):
        time.sleep(1./self.rate)
        data = self._generate(self.counter)
        return data


class PrintLayer(prt.TransformMixin, prt.SynchronousLayer):
    def transform(self, data):
        print(threading.current_thread(), data, "print")


def main():
    print(threading.current_thread())
    raw_data = InputLayer(rate=10000, name="dummy input")
    PrintLayer(raw_data)
    prt.PrintLayer(raw_data)
    prt.LayerManager.session().run()


if __name__ == "__main__":
    main()
