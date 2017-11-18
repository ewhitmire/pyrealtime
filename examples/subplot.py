import numpy as np

import pyrealtime as prt

RATE = 100
N_STREAMS = 7


def gen_dummy_data(counter):
    data = np.random.randn(N_STREAMS)/10 + np.sin(counter / RATE * 2 * np.pi * 3 + np.linspace(0, 2*np.pi, N_STREAMS))
    return data


def decoder(data):
    return {'x1': data[0], 'x2': data[1:4], 'x3': data[4], 'x4': data[5], 'x5': data[6]}


def plot_config(ax):
    ax.set_ylim(-2, 2)


def create_fig(fig):
    ax1 = fig.add_subplot(311)
    ax2 = fig.add_subplot(312)
    ax3 = fig.add_subplot(337)
    ax4 = fig.add_subplot(338)
    ax5 = fig.add_subplot(339)
    return {'x1': ax1, 'x2': ax2, 'x3': ax3, 'x4': ax4, 'x5': ax5}


def main():
    input_layer = prt.InputLayer(gen_dummy_data, rate=RATE, name="dummy input", print_fps=True)
    split_layer = prt.DecodeLayer(input_layer, decoder=decoder, name="decoder")

    fm = prt.FigureManager(create_fig=create_fig, fps=40)
    prt.TimePlotLayer(split_layer.get_port('x1'), plot_key='x1', window_size=1000, plot_config=plot_config, fig_manager=fm)
    prt.TimePlotLayer(split_layer.get_port('x2'), plot_key='x2', window_size=1000, n_channels=3, plot_config=plot_config, fig_manager=fm, legend=True)
    prt.TimePlotLayer(split_layer.get_port('x3'), plot_key='x3', window_size=1000, plot_config=plot_config, fig_manager=fm)
    prt.TimePlotLayer(split_layer.get_port('x4'), plot_key='x4', window_size=1000, plot_config=plot_config, fig_manager=fm)
    prt.TimePlotLayer(split_layer.get_port('x5'), plot_key='x5', window_size=1000, plot_config=plot_config, fig_manager=fm)

    prt.LayerManager.session().run()


if __name__ == "__main__":
    main()
