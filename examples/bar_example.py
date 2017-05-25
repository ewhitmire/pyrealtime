from pyrealtime.decode_layer import BufferLayer, DecodeLayer
from pyrealtime.layer_manager import LayerManager
from pyrealtime.plot_layer import SimplePlotLayer, BarPlotLayer, FigureManager
from pyrealtime.serial_layer import DummyInputLayer, AsciiSerialLayer
import numpy as np


def gen_dummy_data():
    data = np.random.randint(100, size=(3,))
    return data

def decode(data):
    return {'x1': data[0], 'x2': data[1:]}

def plot_config(ax):
    ax.set_ylim(0, 100)


def create_fig(fig):
    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)
    return {'x1': ax1, 'x2': ax2}


def main():
    raw_data = DummyInputLayer(gen_dummy_data, rate=5, name="dummy input")
    decode_layer = DecodeLayer(raw_data, decoder=decode)
    buffer = BufferLayer(decode_layer.get_port('x1'))
    # buffer2 = BufferLayer(decode_layer.get_port('x2'))

    fig_manager = FigureManager(create_fig=create_fig)
    SimplePlotLayer(buffer, plot_key='x1', plot_config=plot_config, fig_manager=fig_manager)
    # SimplePlotLayer(buffer2, plot_key='x2', plot_config=plot_config, fig_manager=fig_manager)
    BarPlotLayer(decode_layer.get_port('x2'), plot_key='x2', plot_config=plot_config, fig_manager=fig_manager)
    LayerManager.start()


if __name__ == "__main__":
    main()
