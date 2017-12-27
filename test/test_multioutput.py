import unittest
import pyrealtime as prt
import time


@prt.transformer
def transform_func(data):
    return data + 1


class test_multioutput(unittest.TestCase):
    """Test multioutput"""

    def setUp(self):
        pass

    def tearDown(self):
        prt.LayerManager.session().reset()

    @prt.method_dec(prt.transformer)
    def transform_meth(self, data):
        return data+1

    def test_multi(self):
        writer = prt.CustomInputLayer(multi_output=True)
        output = prt.OutputLayer(writer)
        out_a = prt.OutputLayer(transform_func(writer.get_port('a')))
        out_b = prt.OutputLayer(transform_func(writer.get_port('b')))
        prt.LayerManager.session().start()

        data = {'a': 1, 'b': 2}
        writer.supply_input(data)

        self.assertEqual(output.get_output(), data)
        self.assertEqual(out_a.get_output(), data['a'] + 1)
        self.assertEqual(out_b.get_output(), data['b'] + 1)

        writer.supply_input(prt.LayerSignal.STOP)
