from pyrealtime.layer import ProducerMixin, ThreadLayer, TransformMixin


def find_serial_port(name):
    try:
        import serial
        import serial.tools.list_ports
    except ImportError:
        raise ModuleNotFoundError("PySerial not found")
    ports = list(serial.tools.list_ports.comports())
    port = None
    for p in ports:
        if name in p.description:
            port = p.device

    if port is None:
        print("Error: could not find port: %s." % name)
        print("Available ports:")
        for p in ports:
            print("%s: %s" % (p, p.description))

    return port


class SerialWriteLayer(TransformMixin, ThreadLayer):
    def __init__(self, port_in, baud_rate, device_name, encoder=None, *args, **kwargs):
        self.ser = None
        self.baud_rate = baud_rate
        self.device_name = device_name
        self._encode = encoder if encoder is not None else self.encode
        super().__init__(port_in, *args, **kwargs)

    @classmethod
    def from_port(cls, port_in, serial, *args, **kwargs):
        layer = cls(port_in=port_in, baud_rate=None, device_name=None, *args, **kwargs)
        layer.ser = serial
        return layer

    def encode(self, data):
        return data

    def initialize(self):

        try:
            import serial
            import serial.tools.list_ports
        except ImportError:
            raise ModuleNotFoundError("PySerial not found")

        if self.ser is None:
            port = find_serial_port(self.device_name)
            self.ser = serial.Serial(port, self.baud_rate, timeout=5)

    def transform(self, data):
        self.ser.write(self._encode(data))


class SerialReadLayer(ProducerMixin, ThreadLayer):
    def __init__(self, baud_rate, device_name, parser=None, *args, **kwargs):
        self.ser = None
        self.baud_rate = baud_rate
        self.device_name = device_name
        self._parse = parser if parser is not None else self.parse
        super().__init__(*args, **kwargs)

    @classmethod
    def from_port(cls, serial, *args, **kwargs):
        layer = cls(baud_rate=None, device_name=None, *args, **kwargs)
        layer.ser = serial
        return layer

    def parse(self, data):
        return data

    def initialize(self):

        try:
            import serial
        except ImportError:
            raise ModuleNotFoundError("PySerial not found")

        if self.ser is None:
            port = find_serial_port(self.device_name)
            self.ser = serial.Serial(port, self.baud_rate, timeout=5)

    def get_input(self):
        line = self.ser.readline()
        try:
            line = line.decode('utf-8').strip()
        except UnicodeDecodeError:
            line = None
            pass

        return self._parse(line)


class ByteSerialReadLayer(SerialReadLayer):
    def __init__(self, num_bytes=1, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.num_bytes = num_bytes

    def get_input(self):
        data = self.ser.read(self.num_bytes)
        return self._parse(data)