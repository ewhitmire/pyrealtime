import threading

import matplotlib

from pyrealtime.layer import TransformMixin, ProcessLayer, ThreadLayer, MultiOutputMixin

import time
import copy
import matplotlib.animation as animation
from matplotlib import pyplot as plt
import numpy as np

import numpy as np

def _blit_draw(self, artists, bg_cache):
    # Handles blitted drawing, which renders only the artists given instead
    # of the entire figure.
    updated_ax = []
    for a in artists:
        # If we haven't cached the background for this axes object, do
        # so now. This might not always be reliable, but it's an attempt
        # to automate the process.
        if a.axes not in bg_cache:
            # bg_cache[a.axes] = a.figure.canvas.copy_from_bbox(a.axes.bbox)
            # change here
            bg_cache[a.axes] = a.figure.canvas.copy_from_bbox(a.axes.figure.bbox)
        a.axes.draw_artist(a)
        updated_ax.append(a.axes)

    # After rendering all the needed artists, blit each axes individually.
    for ax in set(updated_ax):
        # and here
        # ax.figure.canvas.blit(ax.bbox)
        ax.figure.canvas.blit(ax.figure.bbox)


class FigureManager(ProcessLayer):
    def __init__(self, create_fig=None, fps=30, keep_plot_open=False, *args, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = "FigureManager"
        super().__init__(*args, **kwargs)
        self.fig = None
        self.axes_dict = None
        self.plot_layers = {}
        self.create_fig = create_fig if create_fig is not None else FigureManager.default_create_fig
        self.anim = None
        self.fps = fps
        self.keep_plot_open = keep_plot_open

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

        # matplotlib.animation.Animation._blit_draw = _blit_draw
        self.anim = animation.FuncAnimation(self.fig, self.update_func, init_func=self.init_func, frames=None,
                                      interval=1000 / self.fps, blit=True)

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
        try:
            plt.show()
        except KeyboardInterrupt:
            print("exiting figure")
        print("done showing")
        self.shutdown()

    def register_plot(self, key, plot_layer):
        if key in self.plot_layers:
            raise NameError("plot key already exists: %s" % key)
        self.plot_layers[key] = plot_layer

    def shutdown(self):
        if not self.keep_plot_open:
            def close_fig():
                plt.close(self.fig)
            # plt.close hangs for some reason, so doing this in a daemon thread
            t = threading.Thread(target=close_fig, daemon=True)
            t.start()
        self.stop_event.set()
        super().shutdown()


class PlotLayer(MultiOutputMixin, TransformMixin, ThreadLayer):

    def __init__(self, port_in, samples=10, fig_manager=None, plot_config=None, plot_key=None, create_fig=None, legend=False, *args, **kwargs):
        self.data_lock = None
        self.samples = samples
        self.buf_data = None
        self.fig_manager = fig_manager if fig_manager is not None else FigureManager(create_fig=create_fig)
        self.fig_manager.register_plot(plot_key, self)  # TODO
        self.plot_config = plot_config
        self.ax = None
        self.series = None
        self.to_return = None
        self.legend = legend
        self.h_legend = None
        self.legend_dict = dict()
        self.trigger_legend_redraw = False

        super().__init__(port_in, parent_proc=self.fig_manager, *args, **kwargs)

    def transform(self, data):
        self.data_lock.acquire()
        self.buf_data = data
        self.data_lock.release()

        self.data_lock.acquire()
        to_return_copy = copy.copy(self.to_return)
        self.to_return = None
        self.data_lock.release()
        return to_return_copy

    def raise_event(self, key, value):
        # TODO: Check if thread safe
        self.data_lock.acquire()
        if self.to_return is None:
            self.to_return = {}
        self.to_return[key] = value
        self.data_lock.release()

    def anim_update(self, _):
        lines = []
        self.data_lock.acquire()
        if self.buf_data is not None:
            lines = self.update_fig(self.buf_data)
        self.data_lock.release()
        # if self.trigger_legend_redraw:
        #     lines += self.h_legend.get_lines()
        #     self.trigger_legend_redraw = False
        #     # self.fig_manager.anim._blit = False

        return lines

    def create_fig(self, fig, ax):
        self.data_lock = threading.Lock()
        self.ax = ax

        self.series = self.draw_empty_plot(ax)
        if self.plot_config is not None:
            self.plot_config(ax)

    def post_init(self, data):
        super().post_init(data)
        if self.legend:
            self.h_legend = self.ax.legend(loc='upper left')
            for legline, origline in zip(self.h_legend.get_lines(), self.series):
                legline.set_picker(5)  # 5 pts tolerance
                self.legend_dict[legline] = origline
            self.fig_manager.fig.canvas.mpl_connect('pick_event', self.on_pick)

    def on_pick(self, event):
        # on the pick event, find the orig line corresponding to the
        # legend proxy line, and toggle the visibility
        legline = event.artist
        origline = self.legend_dict[legline]
        vis = not origline.get_visible()
        origline.set_visible(vis)
        # Change the alpha on the line in the legend so we can see what lines
        # have been toggled
        if vis:
            legline.set_alpha(1)
        else:
            legline.set_alpha(0.2)
        self.trigger_legend_redraw = True

    def draw_empty_plot(self, ax):
        raise NotImplementedError

    def update_fig(self, data):
        raise NotImplementedError

    def init_fig(self):
        raise NotImplementedError


class SimplePlotLayer(PlotLayer):
    def __init__(self, port_in, ylim=None, *args, **kwargs):
        super().__init__(port_in, *args, **kwargs)
        self.ylim = ylim

    def draw_empty_plot(self, ax):
        return []

    def post_init(self, data):
        n_channels = 1
        import numpy as np
        if isinstance(data, np.ndarray):
            n_channels = data.shape[-1]
            self.samples = data.shape[0]
        else:
            self.samples = len(data)

        self.series = []
        self.ax.set_xlim(0, self.samples)
        if self.ylim is not None:
            self.ax.set_ylim(self.ylim)
        for channel in range(n_channels):
            handle, = self.ax.plot([], [], '-', lw=1)
            self.series.append(handle)

        super().post_init(data)

    def init_fig(self):
        for series in self.series:
            series.set_data([], [])
        return self.series

    def update_fig(self, data):
        import numpy as np
        x = np.linspace(1, self.samples, self.samples)
        for (i, series) in enumerate(self.series):
            if isinstance(data, np.ndarray):
                series.set_data(x, data[:, i])
            else:
                series.set_data(x, data)
        return self.series


class TimePlotLayer(PlotLayer):
    def __init__(self, port_in, window_size=100, n_channels=None, ylim=None, lw=1, *args, **kwargs):
        super().__init__(port_in, *args, **kwargs)
        self.window_size = window_size
        self.n_channels = n_channels
        self.ylim = ylim
        self.lw = lw
        self.buffer = None

        self.use_np = False
        self.num_ticks = 5
        # self.x_time_locs = np.linspace(0, window_size, self.num_ticks)
        # self.x_time = np.linspace(-window_size, 0, self.num_ticks)

    def draw_empty_plot(self, ax):
        return []

    def post_init(self, data):
        import numpy as np
        if isinstance(data, np.ndarray):
            self.use_np = True

        if self.n_channels is None:
            if self.use_np:
                self.n_channels = data.shape[-1] if len(data.shape) > 1 else 1
            else:
                self.n_channels = 1

        self.buffer = np.zeros((self.window_size, self.n_channels))

        self.series = []
        self.ax.set_xlim(0, self.window_size)
        # self.ax.set_xticks(self.x_time_locs)
        # self.ax.set_xticklabels(self.x_time)
        self.ax.get_xaxis().set_animated(True)
        if self.ylim is not None:
            self.ax.set_ylim(self.ylim)
        for channel in range(self.n_channels):
            handle, = self.ax.plot([], [], '-', lw=self.lw, label=channel)
            self.series.append(handle)

        super().post_init(data)

    def init_fig(self):
        for series in self.series:
            series.set_data([], [])
        return self.series

    def update_fig(self, data):
        import numpy as np
        x = np.linspace(1, self.window_size, self.window_size)
        for (i, series) in enumerate(self.series):
            if isinstance(data, np.ndarray):
                series.set_data(x, data[:, i])
            else:
                series.set_data(x, data)
        return self.series + [self.ax.get_xaxis()]

    def transform(self, data):
        # assert (len(data) < self.window_size)
        if self.use_np and len(data.shape) == 1:
            if len(data) == self.n_channels:
                data = np.atleast_2d(data)
            else:
                data = np.atleast_2d(data).T

        if self.use_np:
            if not np.isscalar(data):
                data_size = data.shape[0]
            else:
                data_size = 1

            self.buffer = np.roll(self.buffer, shift=-data_size, axis=0)
            if not np.isscalar(data):
                self.buffer[-data_size:, :] = data
            else:
                self.buffer[-1, :] = data
        else:
            if isinstance(data, list):
                if len(data) == self.n_channels:
                    data_size = 1
                else:
                    data_size = len(data)
            else:
                data_size = 1
            self.buffer = np.roll(self.buffer, shift=-data_size, axis=0)
            if isinstance(data, list):
                self.buffer[-data_size:, :] = data
            else:
                self.buffer[-1, :] = data

        # self.x_time += data_size
        # self.ax.set_xticklabels(self.x_time)
        super().transform(self.buffer)


class BarPlotLayer(PlotLayer):
    def __init__(self, port_in, ylim=None, *args, **kwargs):
        super().__init__(port_in, *args, **kwargs)
        self.ylim = ylim
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

        if self.ylim is not None:
            self.ax.set_ylim(self.ylim)

    def update_fig(self, data):
        for (i, bar) in enumerate(self.series.get_children()):
            if isinstance(data, list) or isinstance(data, np.ndarray):
                bar.set_height(data[i])
            else:
                bar.set_height(data)
        return self.series


class TextPlotLayer(PlotLayer):
    def __init__(self, port_in, *args, **kwargs):
        super().__init__(port_in, *args, **kwargs)
        self.h_text = None

    def draw_empty_plot(self, ax):
        ax.set_axis_off()
        self.h_text = ax.text(0.5, 0.5, "", horizontalalignment='center', verticalalignment='center', fontsize=15)
        return self.h_text,

    def init_fig(self):
        return self.update_fig("")

    def update_fig(self, data):
        self.h_text.set_text(data)
        return self.h_text,

