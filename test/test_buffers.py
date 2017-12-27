import unittest
import pyrealtime as prt
import numpy as np


class test_buffers(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        prt.LayerManager.session().reset()

    def test_passthrough(self):
        writer = prt.CustomInputLayer()
        output = prt.OutputLayer(writer)
        prt.LayerManager.session().start()

        for i in range(5):
            writer.supply_input(i)

        for i in range(5):
            self.assertEqual(output.get_output(), i)

        writer.supply_input(prt.LayerSignal.STOP)

    def test_fixedbuffer(self):
        writer = prt.CustomInputLayer(buffer=prt.FixedBuffer(buffer_size=3))
        output = prt.OutputLayer(writer)
        prt.LayerManager.session().start()

        for i in range(4):
            writer.supply_input(i)
            writer.supply_input(i + .1)
            writer.supply_input(i + .2)

        for i in range(4):
            self.assertEqual(output.get_output(), [i, i + .1, i + .2])

        writer.supply_input(prt.LayerSignal.STOP)

    def test_fixedbuffer1d(self):
        writer = prt.CustomInputLayer(buffer=prt.FixedBuffer(buffer_size=3, use_np=True))
        output = prt.OutputLayer(writer)
        prt.LayerManager.session().start()

        for i in range(4):
            writer.supply_input(np.array([i]))
            writer.supply_input(np.array([i + .1]))
            writer.supply_input(np.array([i + .2]))

        for i in range(4):
            np.testing.assert_equal(output.get_output(), np.atleast_2d([i, i + .1, i + .2]).T)

        writer.supply_input(prt.LayerSignal.STOP)

    def test_fixedbuffer2d(self):
        writer = prt.CustomInputLayer(buffer=prt.FixedBuffer(buffer_size=2, use_np=True, shape=(3,)))
        output = prt.OutputLayer(writer)
        prt.LayerManager.session().start()

        for i in range(4):
            writer.supply_input([i, i + .01, i + .02])
            writer.supply_input([i + .1, i + .11, i + .12])

        for i in range(4):
            o = output.get_output()
            np.testing.assert_equal(o, [[i, i + .01, i + .02], [i + .1, i + .11, i + .12]])

        writer.supply_input(prt.LayerSignal.STOP)

    def test_fixedbuffer3d(self):
        writer = prt.CustomInputLayer(buffer=prt.FixedBuffer(buffer_size=20, use_np=True, shape=(3, 5)))
        output = prt.OutputLayer(writer)
        prt.LayerManager.session().start()

        data = []
        for i in range(3):
            data.append(np.zeros((20, 3, 5)))

        for i in range(60):
            x = np.random.rand(3, 5)
            data[i // 20][i % 20] = x
            writer.supply_input(x)

        for x in data:
            np.testing.assert_equal(output.get_output(), x)

        writer.supply_input(prt.LayerSignal.STOP)
