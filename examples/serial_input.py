import pyrealtime as prt
from examples.utils import gen_dummy_data


def main():
    serial_layer = prt.InputLayer(gen_dummy_data, rate=30, name="dummy input")
    # serial_layer = prt.SerialReadLayer(device_name='KitProg', baud_rate=115200)
    prt.TimePlotLayer(serial_layer, buffer_size=100, ylim=(0, 100))
    prt.LayerManager.session().run()


if __name__ == "__main__":
    main()
