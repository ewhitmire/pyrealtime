import socket

from pyrealtime.layer import ProducerMixin, ThreadLayer, TransformMixin


class UDPInputLayer(ProducerMixin, ThreadLayer):

    def __init__(self, host="0.0.0.0", port=9000, socket=None, parser=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.host = host
        self.port = port
        self.sock = socket
        self.packet_count = 0
        self.parser = parser if parser is not None else self.parse

    def make_socket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_address = (self.host, self.port)
        sock.bind(server_address)
        return sock

    def initialize(self):
        super().initialize()
        if self.sock is None:
            self.sock = self.make_socket()

    def parse(self, data):
        return data

    def get_input(self):
        packet, address = self.sock.recvfrom(1024)
        self.packet_count += 1
        data = self.parser(packet)
        self.tick()
        return data


class UDPOutputLayer(TransformMixin, ThreadLayer):

    def __init__(self, port_in, host="localhost", port=9000, socket=None, *args, **kwargs):
        super().__init__(port_in, *args, **kwargs)
        self.host = host
        self.port = port
        self.packet_count = 0
        self.sock = socket

    def make_socket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return sock

    def initialize(self):
        super().initialize()
        if self.sock is None:
            self.sock = self.make_socket()

    def encode(self, data):
        return data #  .encode('utf-8')

    def transform(self, data):
        self.sock.sendto(self.encode(data), (self.host, self.port))
        return None
