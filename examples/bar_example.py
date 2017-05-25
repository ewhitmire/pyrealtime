from pyrealtime.decode_layer import BufferLayer
from pyrealtime.layer_manager import LayerManager
from pyrealtime.plot_layer import SimplePlotLayer, BarPlotLayer
from pyrealtime.serial_layer import DummyInputLayer, AsciiSerialLayer
import numpy as np


def gen_dummy_data():
    data = np.random.randint(100, size=(1,))
    return data


def plot_config(ax):
    ax.set_ylim(0, 100)


def main():
    raw_data = DummyInputLayer(gen_dummy_data, rate=30, name="dummy input")
    BarPlotLayer(raw_data, plot_config=plot_config)
    LayerManager.start()


if __name__ == "__main__":
    main()
