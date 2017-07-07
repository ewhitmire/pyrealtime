from datetime import datetime, timedelta
import time
from random import random

import numpy as np
import serial
import serial.tools.list_ports

from pyrealtime.decode_layer import comma_decoder
from pyrealtime.layer import ProducerMixin, TransformMixin, ThreadLayer, FPSMixin


class SerialLayer(ProducerMixin, ThreadLayer):
    def __init__(self, baud_rate, device_name, parser=None, *args, **kwargs):
        self.ser = None
        self.baud_rate = baud_rate
        self.device_name = device_name
        self.parser = parser
        super().__init__(*args, **kwargs)

    def parse(self, data):
        if self.parser is None:
            return data
        return self.parser(data)

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

    def get_input(self):
        raise NotImplementedError


class ByteSerialLayer(SerialLayer):
    def __init__(self, num_bytes=1, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.num_bytes = num_bytes

    def get_input(self):
        data = self.ser.read(self.num_bytes)
        self.tick()
        return self.parse(data)


class AsciiSerialLayer(SerialLayer):
    def __init__(self, parser=comma_decoder, *args, **kwargs):
        super().__init__(parser=parser, *args, **kwargs)
        self.skip = True

    def get_input(self):

        line = self.ser.readline()
        try:
            line = line.decode('utf-8').strip()
        except UnicodeDecodeError:
            line = None
            pass

        if self.skip:
            self.skip = False
            return None
        self.tick()
        return self.parse(line)

