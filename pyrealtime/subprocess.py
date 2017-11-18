from threading import Thread

import pyrealtime as prt


class SubprocessLayer(prt.TransformMixin, prt.ThreadLayer):
    def __init__(self, port_in, cmd, *args, encoder=None, decoder=None, **kwargs):
        super().__init__(port_in, *args, **kwargs)
        self.cmd = cmd
        self.proc = None
        self.read_thread = None
        self._encode = encoder if encoder is not None else self.encode
        self._decode = decoder if decoder is not None else self.decode

    def encode(self, data):
        return data + "\n"

    def decode(self, data):
        return data.rstrip().decode('utf-8')

    def initialize(self):
        try:
            import pexpect.popen_spawn
        except ImportError:
            raise ModuleNotFoundError("pexpect required to use subprocess layers")
        self.proc = pexpect.popen_spawn.PopenSpawn(self.cmd)
        self.read_thread = Thread(target=self.read_loop)
        self.read_thread.start()

    def read_loop(self):
        import pexpect
        while True:
            try:
                index = self.proc.expect(".*\n")
                data = self.proc.match[index]
                self.handle_output(self._decode(data))
            except pexpect.exceptions.EOF:
                print("end of file")
                return prt.LayerSignal.STOP

    def transform(self, data):
        self.proc.write(self._encode(data))
        return None
