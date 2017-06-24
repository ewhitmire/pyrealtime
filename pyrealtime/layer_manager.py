import multiprocessing

import time
from warnings import warn


class LayerManager:
    layers = []
    stop_event = multiprocessing.Event()
    input_prompts = multiprocessing.Queue()

    @staticmethod
    def reset():
        LayerManager.layers = []
        LayerManager.stop_event = multiprocessing.Event()
        LayerManager.input_prompts = multiprocessing.Queue()

    @staticmethod
    def add_layer(layer):
        LayerManager.layers.append(layer)
        return layer

    @staticmethod
    def start():
        warn("LayerManager.start renamed to LayerManager.run")
        LayerManager.run()

    @staticmethod
    def run():
        for layer in LayerManager.layers:
            layer.start(LayerManager.stop_event)

        while not LayerManager.stop_event.is_set():
            LayerManager.handle_input()
            time.sleep(0.1)

        for layer in LayerManager.layers:
            layer.join()

        LayerManager.reset()

    @staticmethod
    def handle_input():
        if not LayerManager.input_prompts.empty():
            input_prompt = LayerManager.input_prompts.get()
            response = input(input_prompt.prompt)
            input_prompt.response = response
            input_prompt.event.set()

    @staticmethod
    def input(prompt):
        input_prompt = InputPrompt(prompt)
        LayerManager.input_prompts.put(input_prompt)
        return input_prompt.execute()


class InputPrompt:
    def __init__(self, prompt):
        self.prompt = prompt
        self.response = None
        self.event = multiprocessing.Event()

    def execute(self):
        self.event.wait()
        return self.response
