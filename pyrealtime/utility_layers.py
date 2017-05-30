import math
from statistics import mean

from pyrealtime.layer import TransformMixin, ThreadLayer


class PrintLayer(TransformMixin, ThreadLayer):
    def transform(self, data):
        print(data)
        return data


class AggregateLayer(TransformMixin, ThreadLayer):
    def __init__(self, port_in, in_place=False, *args, **kwargs):
        super().__init__(port_in, *args, **kwargs)
        self.buffer = None
        self.in_place = in_place
        assert self.in_place  # TODO
        self.use_np = False
        self.is_saving = False  # TODO
        self.should_flush = False  # TODO

    def post_init(self, data):
        super().post_init(data)

        import numpy as np
        if isinstance(data, np.ndarray):
            self.use_np = True

        if self.use_np:
            import numpy as np
            if self.in_place:
                n_channels = data.shape[-1] if len(data.shape) > 1 else 1
            else:
                n_channels = data.shape[-1]
            self.buffer = np.zeros((0, n_channels))
        else:
            self.buffer = []

    def handle_signal(self, signal):
        pass

    def start_saving(self):
        print('start')
        self.is_saving = True

    def stop_saving(self):
        print('stop')
        self.is_saving = False
        self.should_flush = True

    def transform(self, data):
        if self.is_saving:
            if self.use_np and len(data.shape) == 1:
                import numpy as np
                data = np.atleast_2d(data).T

            if self.use_np:
                import numpy as np
                self.buffer = np.concatenate((self.buffer, data), axis=0)
            else:
                self.buffer += data

        if self.should_flush:
            self.should_flush = False
            return self.buffer
        return None


class BufferLayer(TransformMixin, ThreadLayer):
    def __init__(self, port_in, buffer_size=10, in_place=False, *args, **kwargs):
        super().__init__(port_in, *args, **kwargs)
        self.buffer_size = buffer_size
        self.use_np = False
        self.buffer = None
        self.in_place = in_place
        # TODO: assert overlap = 0 if in_place is false and other cases

    def post_init(self, data):
        import numpy as np
        if isinstance(data, np.ndarray):
            self.use_np = True

        if self.use_np:
            import numpy as np
            if self.in_place:
                n_channels = data.shape[-1] if len(data.shape) > 1 else 1
            else:
                n_channels = data.shape[-1]
            self.buffer = np.zeros((self.buffer_size, n_channels))
        else:
            self.buffer = [None] * self.buffer_size

    def transform(self, data):
        if self.in_place:
            return self.in_place_transform(data)
        else:
            return self.normal_transform(data)

    def normal_transform(self, data):
        if self.use_np:
            self.buffer[0:-1,:] = self.buffer[1:,:]
            self.buffer[-1,:] = data
        else:
            self.buffer[0:-1] = self.buffer[1:]
            self.buffer[-1] = data

        return self.buffer

    def in_place_transform(self, data):
        assert(len(data) < self.buffer_size)
        if self.use_np and len(data.shape) == 1:
            import numpy as np
            data = np.atleast_2d(data).T

        data_size = len(data)
        if self.use_np:
            import numpy as np
            self.buffer = np.roll(self.buffer, shift=-data_size, axis=0)
            self.buffer[-data_size:,:] = data
        else:
            self.buffer[0:-data_size] = self.buffer[data_size:]
            self.buffer[-data_size:] = data
        return self.buffer


class SlidingWindow(TransformMixin, ThreadLayer):
    def __init__(self, port_in, buffer_size=10, overlap=0, *args, **kwargs):
        super().__init__(port_in, *args, **kwargs)
        self.buffer_size = buffer_size
        self.overlap = overlap
        self.use_np = False
        self.buffer = None
        # TODO: assert overlap = 0 if in_place is false and other cases

    def post_init(self, data):
        import numpy as np
        if isinstance(data, np.ndarray):
            self.use_np = True

        if self.use_np:
            import numpy as np
            n_channels = data.shape[-1] if len(data.shape) > 1 else 1
            self.buffer = np.zeros((self.buffer_size, n_channels))
        else:
            self.buffer = [None] * self.buffer_size

    def transform(self, data):
        if self.use_np and len(data.shape) == 1:
            import numpy as np
            data = np.atleast_2d(data).T

        if self.use_np:
            import numpy as np
            self.buffer = np.concatenate((self.buffer, data))
        else:
            self.buffer = self.buffer + data

        data_size = len(self.buffer)
        step_size = self.buffer_size - self.overlap

        num_full_buffers, num_extra = self.analyze_slide(data_size, self.buffer_size, step_size)

        for i in range(num_full_buffers):
            if self.use_np:
                out_buffer = self.get_slice(i)
            else:
                out_buffer = self.get_slice(i)
            self.handle_output(out_buffer)

        if self.use_np:
            self.buffer = self.buffer[num_full_buffers*step_size:,:]
        else:
            self.buffer = self.buffer[num_full_buffers*step_size:]

        return None

    def get_slice(self, slice_index):
        step_size = self.buffer_size - self.overlap
        start_index = slice_index * step_size
        if self.use_np:
            return self.buffer[start_index:start_index+self.buffer_size, :]
        else:
            return self.buffer[start_index:start_index+self.buffer_size]

    @staticmethod
    def analyze_slide(n, frame_len, frame_step):
        frame_len = int(round(frame_len))
        frame_step = int(round(frame_step))
        if n <= frame_len:
            num_frames = 0
            extra = n
        else:
            num_frames = 1 + int(math.floor((1.0 * n - frame_len) / frame_step))
            extra = n - ((num_frames -1)* frame_step + (frame_len - frame_step))
        return num_frames, extra


class MeanLayer(TransformMixin, ThreadLayer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.use_np = False

    def post_init(self, data):
        import numpy as np
        if isinstance(data, np.ndarray):
            self.use_np = True

    def transform(self, data):
        if self.use_np:
            import numpy as np
            return np.mean(data)
        else:
            return mean(data)