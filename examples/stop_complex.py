import pyrealtime as prt


class CounterLayer(prt.InputLayer):
    def __init__(self, target, *args, **kwargs):
        self.target = target
        super().__init__(*args, **kwargs)

    def generate(self, counter):
        if counter == self.target:
            # can trigger a shutdown by returning stop signal or calling stop method
            # return LayerSignal.STOP
            self.stop()
        return counter


def main():
    for target in [20, 40, 60]:
        in_layer = CounterLayer(target=target)
        prt.PrintLayer(in_layer)
        prt.TimePlotLayer(in_layer, buffer_size=10, ylim=(0, 100))
        prt.LayerManager.session().run()


if __name__ == "__main__":
    main()
