import multiprocessing


class LayerManager:
    layers = []
    stop_event = multiprocessing.Event()

    @staticmethod
    def add_layer(layer):
        LayerManager.layers.append(layer)
        return layer

    @staticmethod
    def start():
        for layer in LayerManager.layers:
            layer.start(LayerManager.stop_event)

        for layer in LayerManager.layers:
            layer.join()
