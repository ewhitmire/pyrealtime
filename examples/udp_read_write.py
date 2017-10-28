import pyrealtime as prt


def main():

    # Send out frame count, print response
    reader, writer = prt.make_udp_layers(local_port=56789, remote_port=56788)
    prt.PrintLayer(reader, label="reader: ")
    writer.set_input(prt.InputLayer())

    # Loopback layer
    reader2, writer2 = prt.make_udp_layers(local_port=56788, remote_port=56789)
    writer2.set_input(prt.TransformLayer(reader2, lambda x: int(x)*2))

    prt.LayerManager.session().run()

if __name__ == "__main__":
    main()