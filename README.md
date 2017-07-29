# PyRealtime

PyRealtime is a package that simplifies building realtime pipeline systems Python. 
It is designed to be simple enough to start visualizing data in just a few lines and scalable enough to support more complex workflows.
It supports realtime plotting (Matplotlib), serial communication (Pyserial), and socket connections out of the box.
It uses a declarative data flow syntax, which means you specify *how* the pipeline should behave and then you *run* the pipeline.

For example, you can build a real time plot of data coming from a serial port in just three lines.

```python
from pyrealtime.layer_manager import LayerManager
from pyrealtime.plot_layer import SimplePlotLayer
from pyrealtime.serial_layer import SerialReadLayer
from pyrealtime.utility_layers import BufferLayer

serial_layer = SerialReadLayer(device_name='COM2', baud_rate=9600)
SimplePlotLayer(BufferLayer(serial_layer, buffer_size=100), ylim=(0, 100))
LayerManager.run()
```

Features:
* Serial port read/write
* Realtime plotting using Matplotlib
* UDP Socket read/write
* Audio input from microphone
* Realtime 3D visualizations using PyGame
* Data logging to a file
* Realtime playback of recorded sessions

## Installation

### Dependencies
PyRealtime explicitly requires `numpy` and `Matplotlib`. For other optional features, other packages are required.
 * `pyserial` for serial communication
 * `pygame` for 3D visualizaton
 * `pyaudio` and `scipy` for audio input
