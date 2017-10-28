import pyrealtime as prt


def main():
    raw_data = prt.UDPReadLayer(name="input")
    prt.TimePlotLayer(raw_data, buffer_size=5, ylim=(0, 100))
    prt.LayerManager.session().run()


if __name__ == "__main__":
    main()
