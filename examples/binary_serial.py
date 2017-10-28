import struct
import pyrealtime as prt


def parser(data):
    return struct.unpack('B', data)


def plot_config(ax):
    ax.set_ylim(0, 100)


def main():
    serial_layer = prt.ByteSerialReadLayer(device_name='KitProg', baud_rate=115200, parser=parser)
    buffer = prt.BufferLayer(serial_layer, buffer_size=100, name="buffer")
    prt.SimplePlotLayer(buffer, plot_config=plot_config)
    prt.LayerManager.session().run()


if __name__ == "__main__":
    main()
