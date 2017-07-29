from pyrealtime.input_layers import InputLayer
from pyrealtime.layer import LayerSignal
from pyrealtime.layer_manager import LayerManager
from pyrealtime.plot_layer import SimplePlotLayer
from pyrealtime.utility_layers import BufferLayer, PrintLayer


def gen_dummy_data(counter):
    data = counter % 1000
    if counter == 100:
        return LayerSignal.STOP
    return data


def main():
    serial_layer = InputLayer(gen_dummy_data, name="dummy input")
    buffer = BufferLayer(serial_layer, buffer_size=10, name="buffer")
    PrintLayer(buffer)
    SimplePlotLayer(buffer, ylim=(0, 1000))
    LayerManager.run()


if __name__ == "__main__":
    main()
