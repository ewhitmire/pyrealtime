import pyaudio

from pyrealtime.layer import ProducerMixin, ThreadLayer


class MicrophoneInputLayer(ProducerMixin, ThreadLayer):

    def __init__(self, host="localhost", port=9000, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pyaudio = None
        self.stream = None

    def initialize(self):
        super().initialize()
        self.pyaudio = pyaudio.PyAudio()
        self.stream = self.pyaudio.open(format=LOCAL_MIC_FORMAT,
               channels=CHANNELS,
               rate=SAMPLE_RATE,
               input=True,
               frames_per_buffer=chunk)

    def get_input(self):
        packet, address = self.sock.recvfrom(10000)
        self.packet_count += 1
        self.tick()
        return packet
