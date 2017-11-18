import pyrealtime as prt


def main():
    raw_data = prt.CustomInputLayer(name="custom input")
    prt.PrintLayer(raw_data)
    prt.LayerManager.session().start()

    while True:
        data = input("enter data:")
        if data == 'stop':
            break
        raw_data.supply_input(data)

    prt.LayerManager.session().stop()
    prt.LayerManager.session().join()


if __name__ == "__main__":
    main()
