import numpy as np

from pyrealtime.layer_manager import LayerManager
from pyrealtime.plotting.base import SimplePlotLayer
from pyrealtime.serial_layer import SerialReadLayer
from pyrealtime.utility_layers import BufferLayer


def gen_dummy_data(counter):
    data = np.random.randint(100, size=(1,))
    return ','.join([str(x) for x in data.tolist()])


def main():
    # serial_layer = InputLayer(gen_dummy_data, rate=30, name="dummy input")
    serial_layer = SerialReadLayer(device_name='KitProg', baud_rate=115200)
    buffer = BufferLayer(serial_layer, buffer_size=100, name="buffer")
    SimplePlotLayer(buffer, ylim=(0, 100))
    LayerManager.run()


if __name__ == "__main__":
    main()
