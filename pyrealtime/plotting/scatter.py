from pyrealtime.plotting.base import PlotLayer


class ScatterPlotLayer(PlotLayer):

    def __init__(self, port_in, xlim=None, ylim=None, *args, **kwargs):
        super().__init__(port_in, *args, **kwargs)
        self.xlim = xlim
        self.ylim = ylim

    def draw_empty_plot(self, ax):
        return []

    def post_init(self, data):
        n_channels = 1
        import numpy as np
        if isinstance(data, np.ndarray):
            n_channels = data.shape[1]

        self.series = []
        if self.xlim is not None:
            self.ax.set_xlim(self.xlim)
        if self.ylim is not None:
            self.ax.set_ylim(self.ylim)
        for channel in range(n_channels):
            handle = self.ax.scatter([], [], marker='.')
            self.series.append(handle)

    def init_fig(self):
        for series in self.series:
            series.set_offsets([])
        return self.series

    def update_fig(self, data):
        import numpy as np
        for (i, series) in enumerate(self.series):
            if isinstance(data, np.ndarray):
                series.set_offsets(data[:, i, :])
            else:
                series.set_offsets(data)
        return self.series


class AggregateScatterPlotLayer(ScatterPlotLayer):
    def __init__(self, port_in, buffer_size=100, n_channels=None, *args, **kwargs):
        super().__init__(port_in, *args, **kwargs)
        self.buffer_size = buffer_size
        self.n_channels = n_channels
        self.buffer = None

    def draw_empty_plot(self, ax):
        return []
        # h = ax.scatter([], [])
        # return h,

    def post_init(self, data):
        import numpy as np
        if isinstance(data, np.ndarray):
            self.use_np = True
        if self.use_np:
            import numpy as np
            if self.n_channels is None:
                self.n_channels = data.shape[-2] if len(data.shape) > 1 else 1
            self.buffer = np.zeros((self.buffer_size, self.n_channels, 2))
        else:
            if self.n_channels is None:
                self.n_channels = 1
            self.buffer = [None] * self.buffer_size

        if self.xlim is not None:
            self.ax.set_xlim(self.xlim)
        if self.ylim is not None:
            self.ax.set_ylim(self.ylim)
        self.series = []
        for channel in range(self.n_channels):
            handle = self.ax.scatter([], [], marker='.')
            self.series.append(handle)

    def init_fig(self):
        for series in self.series:
            series.set_offsets([])
        return self.series

    def update_fig(self, data):
        import numpy as np
        for (i, series) in enumerate(self.series):
            if isinstance(data, np.ndarray):
                series.set_offsets(data[:, i, :])
            else:
                series.set_offsets(data)
        return self.series

    def transform(self, data):
        # assert (len(data) < self.window_size)
        if self.use_np:
            import numpy as np
            if not np.isscalar(data):
                data_size = data.shape[0]
            else:
                data_size = 1
            self.buffer = np.roll(self.buffer, shift=-data_size, axis=0)
            if not np.isscalar(data):
                self.buffer[-data_size:, :, :] = data
            else:
                self.buffer[-1, :] = data
        else:
            if isinstance(data, list):
                data_size = len(data)
            else:
                data_size = 1
            self.buffer[0:-data_size] = self.buffer[data_size:]
            if isinstance(data, list):
                self.buffer[-data_size:] = data
            else:
                self.buffer[-1] = data

        # self.x_time += data_size
        # self.ax.set_xticklabels(self.x_time)
        super().transform(self.buffer)
