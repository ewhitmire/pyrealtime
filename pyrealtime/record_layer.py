from datetime import datetime

import numpy as np

from pyrealtime.layer import ThreadLayer, TransformMixin


class RecordLayer(TransformMixin, ThreadLayer):
    def __init__(self, port_in, filename=None, encoder=None, *args, **kwargs):
        super().__init__(port_in, *args, **kwargs)
        if filename is None:
            filename = RecordLayer.make_new_filename()
        self.filename = filename
        self.file = None
        self.encoder = encoder

    def encode(self, data):
        if self.encoder is not None:
            return self.encoder(data)
        else:
            if isinstance(data, list):
                line = ",".join([str(x) for x in data])
            elif isinstance(data, np.ndarray):
                line = ",".join([str(x) for x in data.tolist()])
            else:
                line = str(data)
            return line + "\n"

    def initialize(self):
        self.file = open(self.filename, 'wb')

    def transform(self, data):
        line = self.encode(data)
        if isinstance(line, str):
            line = line.encode('utf-8')
        self.file.write(line)
        self.file.flush()

    @staticmethod
    def make_new_filename():
        timestamp = datetime.now().strftime("%y_%m_%d_%H_%M_%S")
        return "recording_%s.txt" % timestamp