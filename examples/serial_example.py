from pyrealtime.layer_manager import LayerManager
from pyrealtime.plot_layer import SimplePlotLayer
from pyrealtime.utility_layers import BufferLayer
from pyrealtime.serial_layer import DummyInputLayer, AsciiSerialLayer
import numpy as np



def gen_dummy_data():
    data = np.random.randint(100, size=(1,))
    return ','.join([str(x) for x in data.tolist()])


def plot_config(ax):
    ax.set_ylim(0, 100)


def main():
    # serial_layer = DummyInputLayer(gen_dummy_data, rate=30, name="dummy input")
    serial_layer = AsciiSerialLayer(device_name='KitProg', baud_rate=115200)
    buffer = BufferLayer(serial_layer, buffer_size=100, name="buffer")
    SimplePlotLayer(buffer, plot_config=plot_config)
    LayerManager.start()


if __name__ == "__main__":
    main()
