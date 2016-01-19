#OOT Module for GNU Radio
This OOT module includes blocks to build a packetized transceiver system using USRPs. 
It was developed as part of a M.Sc thesis at RWTH-Aachen University. This transceiver is part of a mm-wave research platform used at the Institute for Networked System.

##Install
```
mkdir build
cd build
cmake ..
make && make install
```

##Usage
For an example which uses most of the parts of this project see the `transceiver.grc` in the `examples` folder.

This flowgraph sets up a transceiver that accepts UDP input and forwards output also via UDP. It is intended for use with a USRP x3x0 SDR device.
