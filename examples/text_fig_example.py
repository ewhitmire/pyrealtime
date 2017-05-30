from pyrealtime.input_layers import DummyInputLayer
from pyrealtime.layer_manager import LayerManager
from pyrealtime.plot_layer import TextPlotLayer


def gen_dummy_data():
    return "test"


def main():
    raw_data = DummyInputLayer(gen_dummy_data, rate=5, name="dummy input")
    TextPlotLayer(raw_data)
    LayerManager.start()

if __name__ == "__main__":
    main()
