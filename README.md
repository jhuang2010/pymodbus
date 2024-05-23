# pymodbus

A simple gui to read data from a Modbus device. 

## Description

The programme takes user input parameters including the port, protocol, baudrate, parity, stopbits and address, 
connects to the Modbus device via the USB port and displays the data for register 30001-30006. 

## Getting Started

### Dependencies

* python3.12, pymodbus, pyserial
* Windows, Linux

### Installing

* Download the project zip file and unzip locally
* Install the dependencies from the requirement file
```
pip3 install -r /path/to/requirements.txt
```

### Executing program

* Run the following script
```
python3 /path/to/modubs_reader.py
```

## License

This project is licensed under the MIT License - see the LICENSE.md file for details
