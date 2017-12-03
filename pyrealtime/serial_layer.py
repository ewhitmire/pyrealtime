from pyrealtime.layer import ProducerMixin, ThreadLayer, TransformMixin, EncoderMixin, DecoderMixin


def find_serial_port(name):
    """Utility function to scan available serial ports by name. The returned object is intended to be passed to the
    :meth:`~pyrealtime.serial_layer.SerialWriteLayer.from_port` constructor of
    :class:`~pyrealtime.serial_layer.SerialReadLayer` or :class:`~pyrealtime.serial_layer.SerialWriteLayer`.

    :param name: The name of the serial port to scan for. It will return the first available port containing name.
    :return: A closed serial port object
    """
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


class SerialWriteLayer(TransformMixin, EncoderMixin, ThreadLayer):
    """Sends data to a serial port
    """
    def __init__(self, port_in, baud_rate, device_name, *args, **kwargs):
        """
        :param port_in: Source of data to send
        :param baud_rate: Baud rate or serial port (e.g. 9600, 115200, etc). See pyserial documentation for more details
        :param device_name: Full or partial name of the device (e.g. 'COM2' or 'Arduino'). The port will be obtained using :func:`~pyrealtime.serial_layer.find_serial_port`.
        """
        self.ser = None
        self.baud_rate = baud_rate
        self.device_name = device_name
        super().__init__(port_in, *args, **kwargs)

    @classmethod
    def from_port(cls, port_in, serial, *args, **kwargs):
        """Creates a layer from an existing serial object

        :param serial: Serial port object, either created using pyserial or from :func:`~pyrealtime.serial_layer.find_serial_port`.
        """
        layer = cls(port_in=port_in, baud_rate=None, device_name=None, *args, **kwargs)
        layer.ser = serial
        return layer

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


class SerialReadLayer(ProducerMixin, DecoderMixin, ThreadLayer):
    """Reads data from a serial port
    """
    def __init__(self, baud_rate, device_name, *args, **kwargs):
        """
        :param baud_rate: Baud rate or serial port (e.g. 9600, 115200, etc). See pyserial documentation for more details
        :param device_name: Full or partial name of the device (e.g. 'COM2' or 'Arduino'). The port will be obtained using :func:`~pyrealtime.serial_layer.find_serial_port`.
        """
        self.ser = None
        self.baud_rate = baud_rate
        self.device_name = device_name
        super().__init__(*args, **kwargs)

    @classmethod
    def from_port(cls, serial, *args, **kwargs):
        """Creates a layer from an existing serial object

        :param serial: Serial port object, either created using pyserial or from :func:`~pyrealtime.serial_layer.find_serial_port`.
        """
        layer = cls(baud_rate=None, device_name=None, *args, **kwargs)
        layer.ser = serial
        return layer

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
        return self._decode(line)


class ByteSerialReadLayer(SerialReadLayer):
    def __init__(self, num_bytes=1, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.num_bytes = num_bytes

    def get_input(self):
        data = self.ser.read(self.num_bytes)
        return self._decode(data)