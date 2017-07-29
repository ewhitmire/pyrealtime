import math

from matplotlib.colors import hsv_to_rgb
from matplotlib.widgets import Button
from pyrealtime.input_layers import InputLayer
from pyrealtime.layer import TransformMixin, ThreadLayer
from pyrealtime.layer_manager import LayerManager
from pyrealtime.plot_layer import PlotLayer
import numpy as np

import matplotlib.pyplot as plt
from pyrealtime.utility_layers import BufferLayer, MeanLayer


def gen_dummy_data(counter):
    data = np.random.randint(100, size=(1,))
    return data


TARGET = 50
RED_H = 0
GREEN_H = 0.28


class CirclePlotter(PlotLayer):

    def draw_empty_plot(self, ax):
        h, = ax.plot([], [], '.', markersize=50)
        self.button = Button(plt.axes([0.7, 0.01, 0.1, 0.05]), 'Zero')
        self.button.on_clicked(self.clicked)
        return h,

    def clicked(self, _):
        self.raise_event("click", True)

    def init_fig(self):
        self.ax.set_ylim(0, 100)
        self.series[0].set_data(0, [])
        return self.series

    def update_fig(self, data):
        self.series[0].set_data(0, data)
        hue = self.hue_transfer_function(data)
        color = hsv_to_rgb([hue, 1, 0.75])
        self.series[0].set_color(color)
        return self.series

    @staticmethod
    def hue_transfer_function(data):
        max_error = max((1 - TARGET) ** 2, TARGET ** 2)
        error = (data - TARGET) ** 2
        return RED_H + GREEN_H * math.exp(-3 * error / max_error)


class OffsetLayer(TransformMixin, ThreadLayer):

    def __init__(self, port_in, offset=0, *args, **kwargs):
        super().__init__(port_in, *args, **kwargs)
        self.offset = offset
        self.save_next_flag = False

    def handle_signal(self, signal):
        if signal:
            self.save_next_flag = True

    def transform(self, data):
        if self.save_next_flag:
            self.save_next_flag = False
            self.offset = data
        return data - self.offset


def main():
    raw_data = InputLayer(gen_dummy_data, rate=20, name="dummy input")
    buffer = BufferLayer(raw_data, buffer_size=10)
    offset = OffsetLayer(MeanLayer(buffer), offset=25)
    plotter = CirclePlotter(offset)
    offset.set_signal_in(plotter.get_port('click'))
    LayerManager.run()


if __name__ == "__main__":
    main()
