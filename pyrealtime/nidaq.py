import pyrealtime as prt
import numpy as np


class DAQLayer(prt.ProducerMixin, prt.ThreadLayer):

    def __init__(self, *args, device_name="Dev1", buffer_size=512, sample_rate=10000, **kwargs):
        self.buffer = np.zeros((buffer_size,))
        self.task = None
        self.stream_reader = None
        self.buffer_size = buffer_size
        self.sample_rate = sample_rate
        self.device_name = device_name
        super().__init__(*args, **kwargs)

    def initialize(self):
        import nidaqmx
        import nidaqmx.constants as daq
        try:
            system = nidaqmx.system.System.local()
            driver = system.driver_version
        except OSError:
            print("nidaqmx driver not found")
            raise

        self.task = nidaqmx.Task()

        try:
            self.task.ai_channels.add_ai_voltage_chan(self.device_name+"/ai0", terminal_config=daq.TerminalConfiguration.DIFFERENTIAL)
        except:
            print("Device not found")
            self.task.close()
            raise
        self.task.timing.cfg_samp_clk_timing(self.sample_rate, sample_mode=daq.AcquisitionType.CONTINUOUS)
        import nidaqmx.stream_readers
        self.stream_reader = nidaqmx.stream_readers.AnalogSingleChannelReader(self.task.in_stream)

    def get_input(self):
        data = self.stream_reader.read_many_sample(self.buffer, number_of_samples_per_channel=self.buffer_size)
        return self.buffer[0:data]
