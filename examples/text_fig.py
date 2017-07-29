from pyrealtime.input_layers import InputLayer
from pyrealtime.layer_manager import LayerManager
from pyrealtime.plot_layer import TextPlotLayer


def gen_dummy_data(counter):
    return "test %s" % counter


def main():
    raw_data = InputLayer(gen_dummy_data, rate=5, name="dummy input")
    TextPlotLayer(raw_data)
    LayerManager.run()

if __name__ == "__main__":
    main()
