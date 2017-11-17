import pyrealtime as prt


def gen_dummy_data(counter):
    return "test %s" % counter


def main():
    raw_data = prt.InputLayer(gen_dummy_data, rate=1, name="dummy input")
    process = prt.SubprocessLayer(raw_data, 'python subproc_utils/subproc_echo.py')
    prt.PrintLayer(process)
    prt.LayerManager.session().run()


if __name__ == "__main__":
    main()
