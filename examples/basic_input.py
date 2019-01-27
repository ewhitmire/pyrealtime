import pyrealtime as prt


def main():
    raw_data = prt.InputLayer(name="custom input", print_fps=True)
    prt.PrintLayer(raw_data)

    prt.LayerManager.session().run()


if __name__ == "__main__":
    main()
