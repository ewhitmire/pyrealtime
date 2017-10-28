import pyrealtime as prt


def gen_dummy_data(counter):
    data = counter % 1000
    if counter == 100:
        return prt.LayerSignal.STOP
    return data


def main():
    serial_layer = prt.InputLayer(gen_dummy_data)
    prt.PrintLayer(serial_layer)
    prt.TimePlotLayer(serial_layer, buffer_size=10, ylim=(0, 1000))
    prt.LayerManager.session().run()


if __name__ == "__main__":
    main()
