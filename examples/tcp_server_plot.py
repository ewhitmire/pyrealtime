import pyrealtime as prt


@prt.transformer(multi_output=True)
def parse_data(data):
    try:
        # Assuming packet is formatted as "xxx,yyy"
        values = [float(x) for x in data.split(",")]
        return {"p1": values[0], "p2": values[1]}
    except:
        print("Malformed data")
        return None


def create_fig(fig):
    return {"ax1": fig.add_subplot(2, 1, 1), "ax2": fig.add_subplot(2, 1, 2)}


def main():
    reader, writer = prt.make_tcp_server(local_host='0.0.0.0', local_port=9903)

    parsed = parse_data(reader)

    fm = prt.FigureManager(create_fig=create_fig)
    prt.TimePlotLayer(parsed.get_port("p1"), plot_key="ax1", fig_manager=fm, ylim=(0, 10))
    prt.TimePlotLayer(parsed.get_port("p2"), plot_key="ax2", fig_manager=fm, ylim=(0, 10))

    prt.LayerManager.session().run()


if __name__ == "__main__":
    main()
