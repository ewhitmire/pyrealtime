# PyRealtime
[![Documentation Status](https://readthedocs.org/projects/pyrealtime/badge/?version=latest)](http://pyrealtime.readthedocs.io/en/latest/?badge=latest)
[![Build Status](https://travis-ci.org/ewhitmire/pyrealtime.svg?branch=master)](https://travis-ci.org/ewhitmire/pyrealtime)

PyRealtime is a package that simplifies building realtime pipeline systems Python. 
It is designed to be simple enough to start visualizing data in just a few lines and scalable enough to support more complex workflows.
It supports realtime plotting (Matplotlib), serial communication (Pyserial), and socket connections out of the box.
It uses a declarative data flow syntax, which means you specify *how* the pipeline should behave and then you *run* the pipeline.

For example, you can build a real time plot of data coming from a serial port in just three lines.
```python
import pyrealtime as prt

serial_layer = prt.SerialReadLayer(device_name='COM2', baud_rate=9600)
prt.TimePlotLayer(serial_layer, window_size=100, ylim=(0, 100))
prt.LayerManager.session().run()
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