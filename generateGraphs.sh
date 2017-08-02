#!/bin/bash

# Top keywords:
python analizeTopic.py authorKeywords -t "WSN,Wireless sensor network,Wireless sensor networks;RFID,RADIO FREQUENCY IDENTIFICATION;Cloud computing;Security;Big data;Privacy;Smart City;6LoWPAN;Sensors;Zigbee" --startYear 2006 --savePlot "keywords.eps"

# Applications:
python analizeTopic.py authorKeywords -t "Cyber-physical systems,CYBER PHYSICAL SYSTEMS,CPS;Healthcare,E-Health;Energy efficiency;Social networks,Social networks,Social media;Augmented reality;Ambient intelligence;Education" --startYear 2006 --savePlot "applications.eps"

# Smart things
python analizeTopic.py authorKeywords -t "Smart city,Smart cities;Smart home,Smart homes;Smart grid,Smart grids;Smart objects,Smart object,Smart enviroments,Smart enviroment;Smart buildings,Smart Building;Smart devices;Smart factory" --startYear 2006 --savePlot "smart_things.eps"


# Communications:
python analizeTopic.py authorKeywords -t "RFID,RADIO FREQUENCY IDENTIFICATION;6LowPAN;ZigBee;Bluetooth Low Energy,BLE;WiFi,Wi-Fi;5G;IEEE 802.15.4" --startYear 2006 --savePlot "comms.eps"

# Software processing:
python analizeTopic.py authorKeywords -t "Machine learning;Hadoop;Artificial intelligence;Fuzzy logic;Genetic Algorithm" --startYear 2006 --savePlot "software.eps"

# Operating systems:
python analizeTopic.py authorKeywords -t "Android;Contiki;Linux;Windows" --startYear 2006 --savePlot "operating.eps"

# Hardware processing:
python analizeTopic.py authorKeywords -t "Raspberry Pi;Arduino;FPGA;Smartphone,Smartphones;Microcontroller;ARM" --startYear 2006 --savePlot "hardware.eps"

# Protocols:
python analizeTopic.py authorKeywords -t "CoAP;IPv6;REST;Mqtt;DTLS" --startYear 2006 --savePlot "protocols.eps"

# Countries:
python topResults.py country --startYear 2002 -l 7 --pYear --savePlot "countries.eps"
#python analizeTopic.py country -t "Colombia;Argentina;Ecuador"

# Authors:
python topResults.py authors --startYear 2006 -l 5 --savePlot "authors.eps"

# Subject
python topResults.py subject --startYear 2006 -l 7 --savePlot "subject.eps"

# Trend analisys: 
# python trendResults.py authors -l 5

# Data Base:
python analizeTopic.py dataBase -t "Scopus;WoS" --savePlot "dataBase_postFilter.eps"

# Buzzwords:
python analizeTopic.py authorKeywords -t "Cloud computing;Big Data;Wireless sensor networks,WSN" --startYear 2006 --savePlot "buzz1.eps"
python analizeTopic.py authorKeywords -t "Fog computing;M2M;Embedded systems;SDN;Ubiquitous computing;Industrial internet of things;Web of things;Edge computing" --startYear 2006 --savePlot "buzz2.eps"



