import threading
import multiprocessing

from pyrealtime.layer_manager import LayerManager


class Port(object):
    def __init__(self):
        self.out_queues = []

    def get_output(self):
        out_queue = multiprocessing.Queue()
        self.out_queues.append(out_queue)
        return out_queue

    def handle_output(self, data):
        for queue in self.out_queues:
            queue.put(data)


class BaseOutputLayer(object):
    def __init__(self, *args, **kwargs):
        self.port = Port()

    def handle_output(self, data):
        self.port.handle_output(data)

    def get_output(self):
        return self.port.get_output()


class BaseInputLayer(object):

    def get_input(self):
        raise NotImplementedError


class BaseLayer(BaseInputLayer, BaseOutputLayer):

    def __init__(self, name="", *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        LayerManager.add_layer(self)
        self.name = name
        self.is_first = True
        self.stop_event = None

    def post_init(self, data):
        pass

    def start(self, stop_event):
        self.stop_event = stop_event

    def transform(self, data):
        return data

    def initialize(self):
        pass

    def process_loop(self):
        while not self.stop_event.is_set():
            data = self.get_input()
            if data is None:
                continue
            if self.is_first:
                self.post_init(data)
                self.is_first = False
            data_transformed = self.transform(data)
            self.handle_output(data_transformed)

    def join(self):
        raise NotImplementedError




# class InProcLayer(BaseLayer): pass


class ThreadLayer(BaseLayer):
    def __init__(self, *args, **kwargs):
        # print("thread layer init")
        super().__init__(*args, **kwargs)
        self.thread = threading.Thread(target=self.run_thread)
        self.thread.daemon = True

    def run_thread(self):
        self.initialize()
        self.process_loop()

    def start(self, *args, **kwargs):
        super(ThreadLayer, self).start(*args, **kwargs)
        self.thread.start()

    def join(self):
        self.thread.join()


class ProcessLayer(BaseLayer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.process = multiprocessing.Process(target=self.run_proc)
        self.thread = None

    def run_proc(self):

        self.initialize()
        self.thread = threading.Thread(target=self.process_loop)
        self.thread.daemon = False
        self.thread.start()
        self.main_thread_post_init()

    def main_thread_post_init(self):
        pass

    def start(self, *args, **kwargs):
        super(ProcessLayer, self).start(*args, **kwargs)
        self.process.start()

    def join(self):
        self.process.join()


class MultiOutputMixin(BaseOutputLayer):
    def __init__(self, *args, **kwargs):
        self.ports = {}
        super().__init__(*args, **kwargs)

    def get_port(self, port):
        if port in self.ports:
            return self.ports[port]
        raise NameError("Port %s does not exist" % port)

    def _register_port(self, port):
        if port in self.ports:
            raise NameError("Port %s already exists" % port)
        self.ports[port] = Port()

    def handle_output(self, data):
        for key in self.ports.keys():
            self.ports[key].handle_output(data[key])
        super().handle_output(data)


class ProducerMixin(BaseInputLayer):

    def get_input(self):
        raise NotImplementedError


class TransformMixin(BaseInputLayer):
    def __init__(self, port_in, *args, **kwargs):
        self.port_in = port_in.get_output()
        super().__init__(*args, **kwargs)

    def get_input(self):
        # print("%d: Blocking for input" % threading.get_ident())
        data = self.port_in.get()  # TODO: Handle None
        return data