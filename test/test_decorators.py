import unittest
import pyrealtime as prt
import time


@prt.transformer
def transform_func(data):
    return data + 1


class test_decorators(unittest.TestCase):
    """Test decorators"""

    def setUp(self):
        pass

    def tearDown(self):
        prt.LayerManager.session().reset()

    @prt.method_dec(prt.transformer)
    def transform_meth(self, data):
        return data+1

    def test_dec_meth(self):
        """Test method_dc"""
        writer = prt.CustomInputLayer()
        output = prt.OutputLayer(self.transform_meth(writer))
        prt.LayerManager.session().start()

        writer.supply_input(1)
        writer.supply_input(5)
        time.sleep(.1)
        writer.supply_input(prt.LayerSignal.STOP)

        self.assertEqual(output.get_output(), 2)
        self.assertEqual(output.get_output(), 6)

    def test_dec_fun(self):
        """Test transformer"""
        writer = prt.CustomInputLayer()
        output = prt.OutputLayer(transform_func(writer))
        prt.LayerManager.session().start()

        writer.supply_input(1)
        writer.supply_input(5)
        time.sleep(.1)
        writer.supply_input(prt.LayerSignal.STOP)

        self.assertEqual(output.get_output(), 2)
        self.assertEqual(output.get_output(), 6)

