#!/bin/bash

# Applications:
python analizeTopic.py authorKeywords -t "Smart city,Smart cities;Smart home,Smart homes;Smart grid,Smart grids;Healthcare,E-Health;Cyber-physical systems,CYBER PHYSICAL SYSTEMS,CPS;Energy efficiency;Energy Harvesting" --startYear 2006 -s "applications.eps"

# Communications:
python analizeTopic.py authorKeywords -t "RFID,RADIO FREQUENCY IDENTIFICATION;6LowPAN;ZigBee;Bluetooth Low Energy,BLE;WiFi,Wi-Fi;5G;IEEE 802.15.4" --startYear 2006 -s "comms.eps"

# Software processing:
python analizeTopic.py authorKeywords -t "Machine learning;Hadoop;Artificial intelligence;Fuzzy logic;Genetic Algorithm" --startYear 2006 -s "software.eps"

# Operating systems:
python analizeTopic.py authorKeywords -t "Android;Contiki;Linux;Windows" --startYear 2006 -s "operating.eps"

# Hardware processing:
python analizeTopic.py authorKeywords -t "Raspberry Pi;Arduino;FPGA;Smartphone,Smartphones;Microcontroller;ARM" --startYear 2006 -s "hardware.eps"

# Protocols:
python analizeTopic.py authorKeywords -t "CoAP;IPv6;REST;Mqtt;DTLS" --startYear 2006 -s "protocols.eps"

# Countries:
python topResults.py country --startYear 2002 -l 7 --pYear -s "countries.eps"
#python analizeTopic.py country -t "Colombia;Argentina;Ecuador"

# Authors:
python topResults.py authors --startYear 2006 -l 5 -s "authors.eps"

# Subject
python topResults.py subject --startYear 2006 -l 7 -s "subject.eps"

# Trend analisys: 
# python trendResults.py authors -l 5

# Data Base:
python analizeTopic.py dataBase -t "Scopus;WoS" -s "dataBase_postFilter.eps"

# Buzzwords:
python analizeTopic.py authorKeywords -t "Cloud computing;Big Data;Wireless sensor networks,WSN" --startYear 2006 -s "buzz1.eps"
python analizeTopic.py authorKeywords -t "Fog computing;M2M;Embedded systems;SDN;Ubiquitous computing;Industrial internet of things;Web of things;Edge computing" --startYear 2006 -s "buzz2.eps"



