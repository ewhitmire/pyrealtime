import pyrealtime as prt


def main():
    process = prt.SubprocessLayer(None, 'python subproc_utils/subproc_datagen.py')

    # Sets up server and sends data
    reader, writer = prt.make_tcp_server()
    writer.set_input(process)

    # Reads data
    client_reader, client_writer = prt.make_tcp_client_layers('127.0.0.1', 9000)
    client_reader._parse = lambda x: x.decode('utf-8').strip()
    prt.PrintLayer(client_reader)

    prt.LayerManager.session().run()


if __name__ == "__main__":
    main()