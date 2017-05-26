from pyrealtime.decode_layer import DecodeLayer
from pyrealtime.layer_manager import LayerManager
from pyrealtime.plot_layer import SimplePlotLayer, FigureManager
from pyrealtime.serial_layer import DummyInputLayer
import numpy as np

from pyrealtime.utility_layers import BufferLayer


def gen_dummy_data():
    data = np.random.randn(4)
    return data


def decoder(data):
    return {'x1': data[0], 'x2': data[1:]}


def plot_config(ax):
    ax.set_ylim(-2, 2)


def create_fig(fig):
    ax1 = fig.add_subplot(211)
    ax2 = fig.add_subplot(212)
    return {'x1': ax1, 'x2': ax2}


def main():
    input_layer = DummyInputLayer(gen_dummy_data, rate=30, name="dummy input")
    split_layer = DecodeLayer(input_layer, decoder=decoder, name="decoder")
    buffer_1 = BufferLayer(split_layer.get_port('x1'), buffer_size=100, name="buffer1")
    buffer_2 = BufferLayer(split_layer.get_port('x2'), buffer_size=100, name="buffer2")
    fig_manager = FigureManager(create_fig=create_fig)
    SimplePlotLayer(buffer_1, plot_key='x1', plot_config=plot_config, fig_manager=fig_manager)
    SimplePlotLayer(buffer_2, plot_key='x2', plot_config=plot_config, fig_manager=fig_manager)
    LayerManager.start()


if __name__ == "__main__":
    main()
