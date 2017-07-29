from pyrealtime.input_layers import InputLayer
from pyrealtime.layer import TransformLayer
from pyrealtime.layer_manager import LayerManager
from pyrealtime.network_layers import make_udp_layers
from pyrealtime.utility_layers import PrintLayer

def main():

    # Send out frame count, print response
    reader, writer = make_udp_layers(local_port=56789, remote_port=56788)
    PrintLayer(reader, label="reader: ")
    writer.set_input(InputLayer())

    # Loopback layer
    reader2, writer2 = make_udp_layers(local_port=56788, remote_port=56789)
    writer2.set_input(TransformLayer(reader2, lambda x: int(x)*2))

    LayerManager.run()

if __name__ == "__main__":
    main()