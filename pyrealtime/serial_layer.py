from datetime import datetime, timedelta
import time
from random import random

import numpy as np
import serial
import serial.tools.list_ports

from pyrealtime.layer import ProducerMixin, TransformMixin, ThreadLayer


class PrintLayer(TransformMixin, ThreadLayer):
    def transform(self, data):
        print(data)
        return data


class SerialLayer(ProducerMixin, ThreadLayer):
    def __init__(self, baud_rate, device_name, *args, **kwargs):
        self.ser = None
        self.num_frames_in_win = 0
        self.start_time = 0
        # self.callback = callback
        self.baud_rate = baud_rate
        self.device_name = device_name
        super().__init__(*args, **kwargs)

    def initialize(self):
        print("Scanning serial ports for device: %s" % self.device_name)
        time.sleep(1)
        ports = list(serial.tools.list_ports.comports())
        port = None
        for p in ports:
            print("%s: %s" % (p, p.description))
            if self.device_name in p.description:
                print("Found port: %s" % p.description)
                port = p.device
        if port is None:
            print("Error: could not find port")
            return
        self.ser = serial.Serial(port, self.baud_rate, timeout=5)
        self.ser.readline()  # Throw away first sample because it may be partial

    def get_input(self):
        self.start_time = datetime.now()
        line = self.ser.readline()
        try:
            self.num_frames_in_win += 1

            if datetime.now() - self.start_time > timedelta(seconds=5):
                print(self.num_frames_in_win / 5.0)
                self.start_time = datetime.now()
                self.num_frames_in_win = 0
            return line
        except ValueError:
            print("Decode error: %s" % line)
        # self.stop_event.set()
        return None


class DummyInputLayer(ProducerMixin, ThreadLayer):
    def __init__(self, data_producer, rate, *args, **kwargs):
        super().__init__( *args, **kwargs)
        self.data_producer = data_producer
        self.rate = rate

    def get_input(self):
        time.sleep(1.0/self.rate)
        return self.data_producer()
