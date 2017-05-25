import struct

from pyrealtime.decode_layer import BufferLayer
from pyrealtime.layer_manager import LayerManager
from pyrealtime.plot_layer import SimplePlotLayer
from pyrealtime.serial_layer import  ByteSerialLayer


def parser(data):
    return struct.unpack('B', data)


def plot_config(ax):
    ax.set_ylim(0, 100)


def main():
    serial_layer = ByteSerialLayer(device_name='KitProg', baud_rate=115200, parser=parser)
    buffer = BufferLayer(serial_layer, buffer_size=100, name="buffer")
    SimplePlotLayer(buffer, plot_config=plot_config)
    LayerManager.start()


if __name__ == "__main__":
    main()
