import socket

from pyrealtime.layer import ProducerMixin, ThreadLayer, TransformMixin


def make_udp_layers(local_host='0.0.0.0', local_port=9000, remote_host='127.0.0.1', remote_port=9001, *args, **kwargs):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((local_host, local_port))

    return UDPReadLayer.from_socket(sock, *args, **kwargs), \
           UDPWriteLayer.from_socket(None, sock, host=remote_host, port=remote_port, *args, **kwargs)

def make_tcp_layers(remote_host='127.0.0.1', remote_port=9001, *args, **kwargs):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((remote_host, remote_port))

    return TCPReadLayer.from_socket(sock, *args, **kwargs), \
           TCPWriteLayer.from_socket(None, sock, *args, **kwargs)


class UDPReadLayer(ProducerMixin, ThreadLayer):

    def __init__(self, host="0.0.0.0", port=9000, bufsize=1024, parser=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.host = host
        self.port = port
        self.socket = None
        self.packet_count = 0
        self.bufsize = bufsize
        self._parse = parser if parser is not None else self.parse

    @classmethod
    def from_socket(cls, sock, *args, **kwargs):
        layer = cls(host=None, port=None, *args, **kwargs)
        layer.socket = sock
        return layer

    def make_socket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_address = (self.host, self.port)
        self.socket.bind(server_address)
        return self.socket

    def initialize(self):
        super().initialize()
        if self.socket is None:
            self.socket = self.make_socket()

    def parse(self, data):
        return data.decode('utf-8')

    def get_input(self):
        packet, address = self.socket.recvfrom(self.bufsize)
        self.packet_count += 1
        data = self._parse(packet)
        self.tick()
        return data


class UDPWriteLayer(TransformMixin, ThreadLayer):

    def __init__(self, port_in, host="127.0.0.1", port=9000, encoder=None, *args, **kwargs):
        super().__init__(port_in, *args, **kwargs)
        self.host = host
        self.port = port
        self.socket = None
        self.packet_count = 0
        self._encode = encoder if encoder is not None else self.encode

    @classmethod
    def from_socket(cls, port_in, sock, host, port, *args, **kwargs):
        layer = cls(port_in, host=host, port=port, *args, **kwargs)
        layer.socket = sock
        return layer

    def make_socket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return sock

    def initialize(self):
        super().initialize()
        if self.socket is None:
            self.socket = self.make_socket()

    def encode(self, data):
        if data is not bytes:
            data = str(data).encode('UTF-8')
        return data

    def transform(self, data):
        self.socket.sendto(self._encode(data), (self.host, self.port))
        return None



class TCPReadLayer(ProducerMixin, ThreadLayer):

    def __init__(self, parser=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.socket = None
        self.packet_count = 0
        self.bufsize = 4096
        self._parse = parser if parser is not None else self.parse

    @classmethod
    def from_socket(cls, sock, *args, **kwargs):
        layer = cls(*args, **kwargs)
        layer.socket = sock
        return layer

    # def make_socket(self):
    #     self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #     # server_address = (self.host, self.port)
    #     # self.socket.bind(server_address)
    #     return self.socket

    def initialize(self):
        super().initialize()
        # if self.socket is None:
        #     self.socket = self.make_socket()

    def parse(self, data):
        return data.decode('utf-8')

    def get_input(self):
        packet = self.socket.recv(self.bufsize)
        self.packet_count += 1
        data = self._parse(packet)
        self.tick()
        return data


class TCPWriteLayer(TransformMixin, ThreadLayer):

    def __init__(self, port_in, encoder=None, *args, **kwargs):
        super().__init__(port_in, *args, **kwargs)
        self.socket = None
        self.packet_count = 0
        self._encode = encoder if encoder is not None else self.encode

    @classmethod
    def from_socket(cls, port_in, sock, *args, **kwargs):
        layer = cls(port_in, *args, **kwargs)
        layer.socket = sock
        return layer

    # def make_socket(self):
    #     sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     return sock

    def initialize(self):
        super().initialize()
        # if self.socket is None:
        #     self.socket = self.make_socket()

    def encode(self, data):
        if data is not bytes:
            data = str(data).encode('UTF-8')
        return data

    def transform(self, data):
        self.socket.send(self._encode(data))
        return None
