from pyrealtime.input_layers import DummyInputLayer
from pyrealtime.layer import LayerTrigger, MergeLayer
from pyrealtime.layer_manager import LayerManager
from pyrealtime.utility_layers import PrintLayer


def main():

    concat = MergeLayer(None, trigger=LayerTrigger.LAYER, trigger_source='in2', discard_old=False)
    concat.set_input(DummyInputLayer(rate=.5), 'in1')
    concat.set_input(DummyInputLayer(rate=2), 'in2')
    PrintLayer(concat)

    LayerManager.run()

if __name__ == "__main__":
    main()