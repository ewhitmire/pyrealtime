import numpy as np
import pyrealtime as prt


def gen_dummy_data(counter):
    data = np.random.randint(100, size=(3,))
    return data


def decode(data):
    return {'x1': data[0], 'x2': data[1:]}


def create_fig(fig):
    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)
    return {'x1': ax1, 'x2': ax2}


def main():
    raw_data = prt.InputLayer(gen_dummy_data, rate=5000, name="dummy input")
    decode_layer = prt.TransformLayer(raw_data, transformer=decode, name="decode_layer", multi_output=True)

    fig_manager = prt.FigureManager(create_fig=create_fig)
    prt.TimePlotLayer(decode_layer.get_port('x1'), plot_key='x1', window_size=1000, ylim=(0,100), fig_manager=fig_manager)
    prt.BarPlotLayer(decode_layer.get_port('x2'), plot_key='x2', ylim=(0,100), fig_manager=fig_manager)
    prt.LayerManager.session().run()


if __name__ == "__main__":
    main()
