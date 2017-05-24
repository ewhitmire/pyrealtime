from pyrealtime.decode_layer import DecodeLayer, BufferLayer
from pyrealtime.layer_manager import LayerManager
from pyrealtime.plot_layer import PlotLayer, SimplePlotLayer
from pyrealtime.serial_layer import SerialLayer, PrintLayer, DummyInputLayer
import numpy as np


def gen_dummy_data():
    data = np.random.randint(100, size=(3,))
    return ','.join([str(x) for x in data.tolist()]).encode('utf-8')


def plot_config(ax):
    ax.set_ylim(0, 100)


def main():
    # serial_layer = DummyInputLayer(gen_dummy_data, rate=30, name="dummy input")
    serial_layer = SerialLayer(device_name='KitProg', baud_rate=115200)
    decode_layer = DecodeLayer(serial_layer, name="decoder")
    buffer = BufferLayer(decode_layer, buffer_size=100, name="buffer")
    plot_layer = SimplePlotLayer(buffer, plot_config=plot_config)
    LayerManager.start()


if __name__ == "__main__":
    main()
