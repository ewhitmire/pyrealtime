from pyrealtime.input_layers import InputLayer
from pyrealtime.layer_manager import LayerManager
from pyrealtime.plot_layer import SimplePlotLayer
from pyrealtime.utility_layers import BufferLayer, PrintLayer


class CounterLayer(InputLayer):
    def __init__(self, target, *args, **kwargs):
        self.target = target
        super().__init__(*args, **kwargs)

    def generate_frame(self, counter):
        if counter == self.target:
            # can trigger a shutdown by returning stop signal or calling stop method
            # return LayerSignal.STOP
            self.stop()
        return counter



def main():
    for target in [20, 40, 60]:
        in_layer = CounterLayer(target=target)
        buffer = BufferLayer(in_layer, buffer_size=10, name="buffer")
        PrintLayer(buffer)
        SimplePlotLayer(buffer, ylim=(0, 100))
        LayerManager.run()


if __name__ == "__main__":
    main()
