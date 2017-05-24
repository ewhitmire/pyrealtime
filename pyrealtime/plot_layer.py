import threading
import matplotlib

from pyrealtime.layer import TransformMixin, ProcessLayer

matplotlib.use('TkAgg')

import time
from pylab import *
import matplotlib.animation as animation

#
# class FigureManager(ProcessLayer):
#     def __init__(self):
#         self.fig = None


class PlotLayer(TransformMixin, ProcessLayer):

    def __init__(self, port_in, samples=10, fps=20, fig_manager=None, plot_config=None, *args, **kwargs):
        self.data_lock = None
        self.samples = samples
        self.buf_data = None
        self.fig = None # _manager = fig_manager if fig_manager is not None else FigureManager()
        self.fps = fps
        self.plot_config = plot_config
        super().__init__(port_in, *args, **kwargs)

    def initialize(self):
        self.data_lock = threading.Lock()
        self.fig = self.create_fig()
        ani = animation.FuncAnimation(self.fig, self.anim_update, init_func=self.init_fig, frames=None, interval=1000 / self.fps, blit=True)
        plt.draw()
        plt.pause(0.01)

    def main_thread_post_init(self):
        plt.show()

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

    def create_fig(self):
        raise NotImplementedError

    def update_fig(self, data):
        raise NotImplementedError

    def init_fig(self):
        raise NotImplementedError


class SimplePlotLayer(PlotLayer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.series = []
        self.ax = None

    def create_fig(self):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        self.ax = ax
        h, = ax.plot([], [])
        self.series.append(h)
        self.plot_config(ax)
        return fig

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