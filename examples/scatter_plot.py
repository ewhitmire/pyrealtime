import pyrealtime as prt
from examples.utils import gen_randn_data
import numpy as np


def gen_randn_list(counter):
    return np.random.randn(1)[0], np.random.randn(1)[0]


def main():
    x = prt.InputLayer(gen_randn_data, rate=30, name="dummy x")
    y = prt.InputLayer(gen_randn_data, rate=30, name="dummy y")

    data = prt.stack((x, y))

    # Buffer some data and plot the entire buffer
    buffered_data = prt.BufferLayer(data, buffer_size=10)
    fm = prt.FigureManager()
    prt.ScatterPlotLayer(buffered_data, xlim=(-1,1), ylim=(-1,1), fig_manager=fm)
    #
    # # Use internal buffer
    # prt.AggregateScatterPlotLayer(data, buffer_size=500, xlim=(-1,1), ylim=(-1,1))
    #
    # # Without using numpy
    # list_data = prt.InputLayer(gen_randn_list, rate=30)
    # prt.AggregateScatterPlotLayer(list_data, buffer_size=500, xlim=(-1,1), ylim=(-1,1))

    prt.LayerManager.session().run()


if __name__ == "__main__":
    main()
