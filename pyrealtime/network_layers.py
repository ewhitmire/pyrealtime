import socket
import socketserver
from threading import Thread

import time
from pyrealtime.layer import ProducerMixin, ThreadLayer, TransformMixin, EncoderMixin, DecoderMixin


def make_udp_layers(local_host='0.0.0.0', local_port=9000, remote_host='127.0.0.1', remote_port=9001, encoder='bytes', decoder='utf-8'):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((local_host, local_port))

    return UDPReadLayer.from_socket(sock, decoder=decoder), \
           UDPWriteLayer.from_socket(None, sock, host=remote_host, port=remote_port, encoder=encoder)


def make_tcp_client_layers(remote_host='127.0.0.1', remote_port=9001, encoder='bytes', decoder='utf-8'):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((remote_host, remote_port))

    return TCPReadLayer.from_socket(sock, decoder=decoder), \
           TCPWriteLayer.from_socket(None, sock, encoder=encoder)


def make_tcp_server(local_host='0.0.0.0', local_port=9000, encoder='bytes', decoder='utf-8'):
    server = TCPServerLayer(local_host, local_port)
    return TCPServerReadLayer(server, decoder=decoder), TCPServerWriteLayer(None, server, encoder=encoder)


class TCPHandler(socketserver.BaseRequestHandler):
    def __init__(self, *args, **kwargs):
        self.shutdown = False  # todo: make event
        super().__init__(*args, **kwargs)

    def handle(self):
        self.server.prt_server.register(self)

        while not self.shutdown:
            time.sleep(.5)

        self.server.prt_server.unregister(self)

    def read(self):
        if self.shutdown:
            return None
        try:
            data = self.request.recv(1024)
            if len(data) > 0:
                return data
            else:
                return None
        except ConnectionAbortedError:
            self.shutdown = True
            return None

    def write(self, data):
        if self.shutdown:
            return
        try:
            self.request.sendall(data)
        except ConnectionAbortedError:
            self.shutdown = True


class TCPServerWriteLayer(TransformMixin, EncoderMixin, ThreadLayer):
    def __init__(self, port_in, server, *args, **kwargs):
        super().__init__(port_in, *args, **kwargs)
        self.server = server

    def transform(self, data):
        self.server.write(self._encode(data))


class TCPServerReadLayer(ProducerMixin, DecoderMixin, ThreadLayer):
    def __init__(self, server, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.server = server

    def get_input(self):
        return self._decode(self.server.read())


class TCPServerLayer(ThreadLayer):

    def __init__(self, local_host='0.0.0.0', local_port=9000):
        super().__init__()
        self.local_host = local_host
        self.local_port = local_port
        self.server = None
        self.serve_thread = None
        self.read_layer = None
        self.handlers = []

        self.server = socketserver.TCPServer((self.local_host, self.local_port), TCPHandler)
        self.server.prt_server = self
        self.serve_thread = Thread(target=self.serve)
        self.serve_thread.start()

    def get_input(self):
        time.sleep(1)

    def register(self, handler):
        print("Got connection!")
        self.handlers.append(handler)

    def unregister(self, handler):
        print("Lost connection!")
        self.handlers.remove(handler)

    def write(self, data):
        for handler in self.handlers:
            handler.write(data)

    def read(self):
        for handler in self.handlers:
            return handler.read()

    def serve(self):
        self.server.serve_forever()

    def shutdown(self):
        super().shutdown()
        self.server.shutdown()


class UDPReadLayer(ProducerMixin, DecoderMixin, ThreadLayer):

    def __init__(self, host="0.0.0.0", port=9000, bufsize=1024, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.host = host
        self.port = port
        self.socket = None
        self.packet_count = 0
        self.bufsize = bufsize

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

    def get_input(self):
        packet, address = self.socket.recvfrom(self.bufsize)
        self.packet_count += 1
        data = self._decode(packet)
        return data


class UDPWriteLayer(TransformMixin, EncoderMixin, ThreadLayer):

    def __init__(self, port_in, host="127.0.0.1", port=9000, *args, **kwargs):
        super().__init__(port_in, *args, **kwargs)
        self.host = host
        self.port = port
        self.socket = None
        self.packet_count = 0

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

    def transform(self, data):
        self.socket.sendto(self._encode(data), (self.host, self.port))
        return None


class TCPReadLayer(ProducerMixin, DecoderMixin, ThreadLayer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.socket = None
        self.packet_count = 0
        self.bufsize = 4096

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

    def get_input(self):
        packet = self.socket.recv(self.bufsize)
        self.packet_count += 1
        data = self._decode(packet)
        self.tick()
        return data


class TCPWriteLayer(TransformMixin, EncoderMixin, ThreadLayer):

    def __init__(self, port_in, *args, **kwargs):
        super().__init__(port_in, *args, **kwargs)
        self.socket = None
        self.packet_count = 0

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

    def transform(self, data):
        self.socket.send(self._encode(data))
        return None
