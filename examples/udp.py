from pyrealtime.layer_manager import LayerManager
from pyrealtime.network_layers import UDPReadLayer
from pyrealtime.plot_layer import SimplePlotLayer
from pyrealtime.utility_layers import BufferLayer


def plot_config(ax):
    ax.set_ylim(0, 100)


def main():
    raw_data = UDPReadLayer(name="input")
    buffer = BufferLayer(raw_data, buffer_size=5, name="buffer")
    SimplePlotLayer(buffer, plot_config=plot_config)
    LayerManager.run()


if __name__ == "__main__":
    main()
