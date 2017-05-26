import socket

from pyrealtime.layer import ProducerMixin, ThreadLayer, FPSMixin, TransformMixin


class UDPInputLayer(ProducerMixin, ThreadLayer):

    def __init__(self, host="localhost", port=9000, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.host = host
        self.port = port
        self.sock = None
        self.packet_count = 0

    def initialize(self):
        super().initialize()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_address = (self.host, self.port)
        self.sock.bind(server_address)

    def parse(self, data):
        return data

    def get_input(self):
        packet, address = self.sock.recvfrom(10000)
        self.packet_count += 1
        data = self.parse(packet)
        self.tick()
        return data


class UDPOutputLayer(TransformMixin, ThreadLayer):

    def __init__(self, port_in, host="localhost", port=9000, *args, **kwargs):
        super().__init__(port_in, *args, **kwargs)
        self.host = host
        self.port = port
        self.packet_count = 0
        self.sock = None

    def initialize(self):
        super().initialize()
        if self.sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # server_address = (self.host, self.port)
            # self.sock.bind(server_address)  # TODO: not right

    def parse(self, data):
        return data

    def encode(self, data):
        return data #  .encode('utf-8')

    def transform(self, data):
        self.sock.sendto(self.encode(data), (self.host, self.port))
        return None
