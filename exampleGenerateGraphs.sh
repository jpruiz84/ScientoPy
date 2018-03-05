#!/bin/bash

# Top keywords:
python scientoPy.py authorKeywords -t "WSN,Wireless sensor network,Wireless sensor networks;RFID,RADIO FREQUENCY IDENTIFICATION;Cloud computing;Security;Big data;Privacy;Smart City;6LoWPAN;Sensors;Zigbee" --startYear 2006 --savePlot "keywords.eps"

# Applications:
python scientoPy.py authorKeywords -t "Cyber-physical systems,CYBER PHYSICAL SYSTEMS,CPS;Healthcare,E-Health;Energy efficiency;Social networks,Social networks,Social media;Education,Learning,E-Learning,mobile learning" --startYear 2006 --savePlot "applications.eps"

# Smart things
python scientoPy.py authorKeywords -t "Smart city,Smart cities;Smart home,Smart homes;Smart grid,Smart grids;Smart objects,Smart object,Smart enviroments,Smart enviroment;Smart buildings,Smart Building;Smart devices;Smart factory" --startYear 2006 --savePlot "smart_things.eps"

# Software processing:
python scientoPy.py authorKeywords -t "Machine learning;Data mining;Complex event processing,CEP;Hadoop" --startYear 2006 --savePlot "software.eps"

# Operating systems:
python scientoPy.py authorKeywords -t "Android,Android OS;Contiki,Contiki OS;Linux,Linux OS;iOS,iPhone Operating System,iPhone Operating System (iOS);Windows,Windows OS" --startYear 2006 --savePlot "operating.eps"

# Hardware processing:
python scientoPy.py authorKeywords -t "Raspberry Pi;Arduino,Arduino board;Smartphone,Smartphones,Smart phone,Smart phones;FPGA,Field-programmable gate array,Field programmable gate array;Microcontroller,Microcontrollers" --startYear 2006 --savePlot "hardware.eps"

# Media layers:
python scientoPy.py authorKeywords -t "RFID,RADIO FREQUENCY IDENTIFICATION;6LoWPAN;ZigBee;BLE,Bluetooth Low Energy;WiFi,Wi-Fi;5G;RPL" --startYear 2006 --savePlot "media_layers.eps"

# Host layers:
python scientoPy.py authorKeywords -t "CoAP,Constrained Application Protocol;MQTT,Message Queue Telemetry Transport;DTLS,Datagram Transport Layer Security;TCP;iBeacon;JSON;UDP" --startYear 2006 --savePlot "host_layers.eps"

# Countries:
python scientoPy.py country --startYear 2002 -l 7 --pYear --savePlot "countries.eps"
#python scientoPy.py country -t "Colombia;Argentina;Ecuador"

# Authors:
python scientoPy.py authors --startYear 2006 -l 5 --savePlot "authors.eps"

# Subject
python scientoPy.py subject --startYear 2006 -l 7 --savePlot "subject.eps"

# Trend analisys: 
# python trendResults.py authors -l 5

# Data Base:
python scientoPy.py dataBase -t "Scopus;WoS" --savePlot "dataBase_postFilter.eps"

# Buzzwords:
python trendResults.py authorKeywords -t "Cloud computing;Security;Big Data;Wireless sensor networks;Privacy;Industry 4.0;Fog computing;SDN" --savePlot "trending.eps"


# Parametric *************************

python scientoPy.py authorKeywords -t "WSN,Wireless sensor network,Wireless sensor networks;RFID,RADIO FREQUENCY IDENTIFICATION;Cloud computing;Security;Big data;Privacy;Smart City;6LoWPAN;Sensors;Zigbee" --endYear 2016 --parametric --startYear 2014

python scientoPy.py authorKeywords -t "Cloud computing;Security;Big Data;Wireless sensor networks;Privacy;Industry 4.0;Fog computing;SDN" --endYear 2016 --parametric --startYear 2000
python scientoPy.py authorKeywords -t "Android,Android OS;Contiki,Contiki OS;Linux,Linux OS;iOS,iPhone Operating System,iPhone Operating System (iOS);Windows,Windows OS" --endYear 2016 --parametric
