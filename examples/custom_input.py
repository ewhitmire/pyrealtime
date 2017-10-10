from pyrealtime.input_layers import CustomInputLayer
from pyrealtime.layer_manager import LayerManager
from pyrealtime.utility_layers import PrintLayer


def main():
    raw_data = CustomInputLayer(name="custom input")
    print_layer = PrintLayer(raw_data)
    LayerManager.start()

    while True:
        data = input("enter data:")
        if data == 'stop':
            break
        raw_data.supply_input(data)

    LayerManager.stop()
    LayerManager.join()


if __name__ == "__main__":
    main()
