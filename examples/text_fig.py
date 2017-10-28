import pyrealtime as prt

def gen_dummy_data(counter):
    return "test %s" % counter


def main():
    raw_data = prt.InputLayer(gen_dummy_data, rate=5, name="dummy input")
    prt.TextPlotLayer(raw_data)
    prt.LayerManager.session().run()

if __name__ == "__main__":
    main()
