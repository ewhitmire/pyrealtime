import multiprocessing
import threading

import time
from warnings import warn

import pyrealtime


class LayerManager:
    class __LayerManager:
        def __init__(self):
            # multiprocessing.set_start_method('spawn')
            self.layers = {}
            self.stop_event = multiprocessing.get_context('spawn').Event()
            self.input_prompts = multiprocessing.get_context('spawn').Queue()
            self.show_monitor = False

        def reset(self):
            self.layers = {}
            self.stop_event = multiprocessing.get_context('spawn').Event()
            self.input_prompts = multiprocessing.get_context('spawn').Queue()

        def add_layer(self, layer, only_monitor=False):
            self.layers[layer] = only_monitor
            return layer

        def run(self, show_monitor=False):
            """

            :param show_monitor:
            """
            self.start(show_monitor)

            while not self.stop_event.is_set():
                self.handle_input()
                try:
                    time.sleep(0.1)
                except KeyboardInterrupt:
                    self.stop_event.set()

            self.join()

        def start(self, show_monitor=False):
            self.show_monitor = show_monitor  # cache this so the forked process knows what to do
            for (layer, only_monitor) in self.layers.items():
                if not only_monitor:
                    layer.start(self.stop_event)

            if show_monitor:
                self.start_monitor()

        def start_monitor(self):
            t = threading.Thread(target=self.monitor_thread)
            t.daemon = False
            t.start()

        def monitor_thread(self):
            while not self.stop_event.is_set():
                time.sleep(1)
                for layer in self.layers:
                    if isinstance(layer, pyrealtime.layer.TransformMixin):
                        for name, port in layer.ports_in.items():
                            print("%s: %d" % (layer.name, port.qsize()))

        def join(self):
            for (layer, only_monitor) in self.layers.items():
                if not only_monitor:
                    layer.join()

            self.reset()

        def stop(self):
            self.stop_event.set()

        def handle_input(self):
            if not self.input_prompts.empty():
                input_prompt = self.input_prompts.get()
                response = input(input_prompt.prompt)
                input_prompt.response = response
                input_prompt.event.set()

        def input(self, prompt):
            input_prompt = InputPrompt(prompt)
            self.input_prompts.put(input_prompt)
            return input_prompt.execute()

        def __setstate__(self, state):
            print("SET STATE")
            # Restore instance attributes (i.e., filename and lineno).
            self.__dict__.update(state)
            if LayerManager.show_monitor:
                LayerManager.start_monitor()

    _instance = None

    def __getattr__(self, name):
        return getattr(self._instance, name)

    @staticmethod
    def session():
        if not LayerManager._instance:
            LayerManager._instance = LayerManager.__LayerManager()
        return LayerManager._instance









class InputPrompt:
    def __init__(self, prompt):
        self.prompt = prompt
        self.response = None
        self.event = multiprocessing.Event()

    def execute(self):
        self.event.wait()
        return self.response
