import pyrealtime as prt


def gen_dummy_data(counter):
    return "test %s" % counter

def main():

    raw_data = prt.InputLayer(gen_dummy_data, rate=1, name="dummy input")
    reader, writer = prt.make_tcp_server()
    writer.set_input(raw_data)
    prt.PrintLayer(reader)

    prt.LayerManager.session().run()

if __name__ == "__main__":
    main()