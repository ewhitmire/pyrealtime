import pyrealtime as prt


def main():
    concat = prt.MergeLayer(None, trigger=prt.LayerTrigger.LAYER, trigger_source='in2', discard_old=False)
    concat.set_input(prt.InputLayer(rate=.5), 'in1')
    concat.set_input(prt.InputLayer(rate=2), 'in2')
    prt.PrintLayer(concat)

    prt.LayerManager.session().run()

if __name__ == "__main__":
    main()
