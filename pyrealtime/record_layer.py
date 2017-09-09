from datetime import datetime

import numpy as np
import time

from pyrealtime.layer import ThreadLayer, TransformMixin, ProducerMixin


class RecordLayer(TransformMixin, ThreadLayer):
    def __init__(self, port_in, filename=None, encoder=None, file_prefix="recording", append_time=False, *args, **kwargs):
        super().__init__(port_in, *args, **kwargs)
        if filename is None:
            filename = RecordLayer.make_new_filename(file_prefix)
        self.filename = filename
        self.file = None
        self.append_time = append_time
        self.encoder = encoder if encoder is not None else self.encode

    def encode(self, data):
        if isinstance(data, list):
            line = ",".join([str(x) for x in data])
        elif isinstance(data, np.ndarray):
            line = ",".join([str(x) for x in data.tolist()])
        else:
            line = str(data)

        if self.append_time:
            line = "%f,%s" % (time.time(), line)
        line += "\n"

        return line.encode('utf-8')

    def post_init(self, data):
        self.file = open(self.filename, 'wb')

    def transform(self, data):
        line = self.encoder(data)
        self.file.write(line)
        self.file.flush()

    @staticmethod
    def make_new_filename(prefix):
        timestamp = datetime.now().strftime("%y_%m_%d_%H_%M_%S")
        return "%s_%s.txt" % (prefix, timestamp)


class PlaybackLayer(ProducerMixin, ThreadLayer):
    def __init__(self, filename=None, rate=1, strip_time=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filename = filename
        self.file = None
        self.interval = 1 / rate
        self.strip_time = strip_time

    def decode(self, line):
        data = line.decode('utf-8').strip()
        if self.strip_time:
            data = data[data.index(',')+1:]
        return data

    def initialize(self):
        self.file = open(self.filename, 'rb')

    def get_input(self):
        line = self.file.readline()
        if len(line) == 0:
            time.sleep(1)
            return None
        time.sleep(self.interval)
        return self.decode(line)


class AudioWriter(TransformMixin, ThreadLayer):
    def __init__(self, port_in, filename=None, sample_rate=44100, *args, **kwargs):
        super().__init__(port_in, *args, **kwargs)
        if filename is None:
            filename = RecordLayer.make_new_filename('recording')
        self.filename = filename
        self.sample_rate = sample_rate

    def transform(self, data):
        import scipy.io.wavfile
        scipy.io.wavfile.write(self.filename, self.sample_rate, data)

    @staticmethod
    def make_new_filename():
        timestamp = datetime.now().strftime("%y_%m_%d_%H_%M_%S")
        return "recording_%s.txt" % timestamp
