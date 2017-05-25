import threading
import matplotlib

from pyrealtime.layer import TransformMixin, ProcessLayer, ThreadLayer

matplotlib.use('TkAgg')

import time
from pylab import *
import matplotlib.animation as animation


class FigureManager(ProcessLayer):
    def __init__(self, create_fig=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fig = None
        self.axes_dict = None
        self.plot_layers = {}
        self.create_fig = create_fig if create_fig is not None else FigureManager.default_create_fig

    @staticmethod
    def default_create_fig(fig):
        ax = fig.add_subplot(111)
        return {None: ax}

    def initialize(self):
        self.fig = plt.figure()
        self.axes_dict = self.create_fig(self.fig)

        for plot_key in self.plot_layers.keys():
            plot_layer = self.plot_layers[plot_key]
            if plot_key not in self.axes_dict:
                raise KeyError("No axis created for plot %s" % plot_key)
            plot_layer.create_fig(self.fig, self.axes_dict[plot_key])

        ani = animation.FuncAnimation(self.fig, self.update_func, init_func=self.init_func, frames=None,
                                      interval=1000 / plot_layer.fps, blit=True)
        self.fig.canvas.draw()
        self.fig.canvas.draw_idle()

    def init_func(self):
        artists = []
        for plot_key in self.plot_layers.keys():
            plot_layer = self.plot_layers[plot_key]
            artists += plot_layer.init_fig()
        return artists

    def update_func(self, frame):
        artists = []
        for plot_key in self.plot_layers.keys():
            plot_layer = self.plot_layers[plot_key]
            artists += plot_layer.anim_update(frame)
        return artists

    def get_input(self):
        time.sleep(1)
        return None

    def main_thread_post_init(self):
        plt.show()

    def register_plot(self, key, plot_layer):
        if key in self.plot_layers:
            raise NameError("plot key already exists: %s" % key)
        self.plot_layers[key] = plot_layer


class PlotLayer(TransformMixin, ThreadLayer):

    def __init__(self, port_in, samples=10, fps=30, fig_manager=None, plot_config=None, plot_key=None, *args, **kwargs):
        self.data_lock = None
        self.samples = samples
        self.buf_data = None
        self.fig_manager = fig_manager if fig_manager is not None else FigureManager()
        self.fig_manager.register_plot(plot_key, self)  # TODO
        self.fps = fps
        self.plot_config = plot_config
        self.ax = None
        self.series = None

        super().__init__(port_in, parent_proc=self.fig_manager, *args, **kwargs)

    def transform(self, data):
        self.data_lock.acquire()
        self.buf_data = data
        self.data_lock.release()

    def anim_update(self, _):
        lines = []
        self.data_lock.acquire()
        if self.buf_data is not None:
            lines = self.update_fig(self.buf_data)
        self.data_lock.release()
        return lines

    def create_fig(self, fig, ax):
        self.data_lock = threading.Lock()
        self.ax = ax

        self.series = self.draw_empty_plot(ax)
        if self.plot_config is not None:
            self.plot_config(ax)

    def draw_empty_plot(self, ax):
        raise NotImplementedError

    def update_fig(self, data):
        raise NotImplementedError

    def init_fig(self):
        raise NotImplementedError


class SimplePlotLayer(PlotLayer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def draw_empty_plot(self, ax):
        h, = ax.plot([], [])
        return h,

    def post_init(self, data):
        n_channels = 1
        if isinstance(data, np.ndarray):
            n_channels = data.shape[-1]
            self.samples = data.shape[0]
        else:
            self.samples = len(data)

        self.series = []
        self.ax.set_xlim(0, self.samples)
        for channel in range(n_channels):
            handle, = self.ax.plot([], [], '-', lw=1)
            self.series.append(handle)

    def init_fig(self):
        for series in self.series:
            series.set_data([], [])
        return self.series

    def update_fig(self, data):
        x = np.linspace(1, self.samples, self.samples)
        for (i, series) in enumerate(self.series):
            if isinstance(data, np.ndarray):
                series.set_data(x, data[:, i])
            else:
                series.set_data(x, data)
        return self.series


class BarPlotLayer(PlotLayer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.series = []

    def draw_empty_plot(self, ax):
        rects = ax.bar([], [])
        return rects

    def init_fig(self):
        for series in self.series:
            series.set_height([])
        return self.series

    def post_init(self, data):
        n_channels = 1
        if isinstance(data, np.ndarray):
            n_channels = data.shape[-1]

        x = list(range(n_channels))
        y = np.zeros((n_channels,))
        rects = self.ax.bar(x, y)
        self.series = rects

    def update_fig(self, data):
        print(self.series[0].get_children())
        print(data)
        for (i, bar) in enumerate(self.series[0].get_children()):
            if isinstance(data, list) or isinstance(data, np.ndarray):
                print(data[i])
                bar.set_height(data[i])
            else:
                bar.set_height(data)
        return self.series