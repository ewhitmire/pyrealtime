import pyrealtime as prt
import scipy.signal


BUFFER_SIZE = 512
SAMPLE_RATE = 10000
PLOT_SIZE_SEC = 2

F_PASS = [35, 65]
F_STOP = [30, 70]


def make_filter():
    def norm_freq(freqs):
        return [x*2/SAMPLE_RATE for x in freqs]
    N, Wn = scipy.signal.buttord(norm_freq(F_PASS), norm_freq(F_STOP), .001, 80, analog=False)
    print(N, Wn)
    sos = scipy.signal.butter(N, Wn, 'bandpass', analog=False, output='sos')
    return sos


def main():
    daq_in = prt.DAQLayer(buffer_size=BUFFER_SIZE, sample_rate=SAMPLE_RATE)
    filter_layer = prt.SOSFilter(daq_in, make_filter())

    concat = prt.stack([daq_in, filter_layer])

    prt.TimePlotLayer(concat, window_size=PLOT_SIZE_SEC*SAMPLE_RATE, ylim=(-1, 1), n_channels=2)
    prt.LayerManager.session().run()


if __name__ == '__main__':
    main()