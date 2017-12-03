import unittest
import pyrealtime as prt
import serial
import time

PORT = 'loop://'


class test_serial(unittest.TestCase):
    """Test serial port layers"""

    def setUp(self):
        self.s = serial.serial_for_url(PORT, timeout=10)

    def tearDown(self):
        self.s.close()
        prt.LayerManager.session().reset()

    def test_write(self):
        """Test SerialWriteLayer"""
        writer = prt.CustomInputLayer()
        prt.SerialWriteLayer.from_port(writer, self.s, encoder='bytes')
        prt.LayerManager.session().start()

        writer.supply_input("test1\n")
        writer.supply_input("test2\n")
        time.sleep(.1)
        writer.supply_input(prt.LayerSignal.STOP)

        self.assertEqual(self.s.readline(), b'test1\n')
        self.assertEqual(self.s.readline(), b'test2\n')

    def test_read(self):
        """Test SerialReadLayer"""
        reader = prt.SerialReadLayer.from_port(self.s, decoder='utf-8')
        output = prt.OutputLayer(reader)
        prt.LayerManager.session().start()

        self.s.write("test1\n".encode("UTF-8"))
        self.s.write("test2\n".encode("UTF-8"))
        time.sleep(.1)
        prt.LayerManager.session().stop()

        self.assertEqual(output.get_output(), 'test1\n')
        self.assertEqual(output.get_output(), 'test2\n')