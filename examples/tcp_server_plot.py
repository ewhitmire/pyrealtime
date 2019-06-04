import pyrealtime as prt


# A parsing function that takes in a string received from the TCP client and splits it into two channels of data
@prt.transformer(multi_output=True)
def parse_data(data):
    try:
        # Assuming packet is formatted as "xxx,yyy"
        values = [float(x) for x in data.split(",")]

        # return a dict of values so it can be split up into subplots
        return {"p1": values[0], "p2": values[1]}
    except:
        print("Malformed data")
        return None


def create_fig(fig):
    # Create two subplots, named ax1, ax2
    return {"ax1": fig.add_subplot(2, 1, 1), "ax2": fig.add_subplot(2, 1, 2)}


def main():
    # Set up TCP server on port 9903
    reader, writer = prt.make_tcp_server(local_host='0.0.0.0', local_port=9903)

    # Parse data coming from the client
    parsed = parse_data(reader)

    # Create figure with two subplots
    fm = prt.FigureManager(create_fig=create_fig)

    # Add two plots to figure, using .get_port to access a specific element of the dictionary
    prt.TimePlotLayer(parsed.get_port("p1"), plot_key="ax1", fig_manager=fm, ylim=(0, 10))
    prt.TimePlotLayer(parsed.get_port("p2"), plot_key="ax2", fig_manager=fm, ylim=(0, 10))

    prt.LayerManager.session().run()


if __name__ == "__main__":
    main()
