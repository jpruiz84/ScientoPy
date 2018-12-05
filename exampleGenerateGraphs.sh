#!/bin/bash

# Pre process
python3 preProcess.py dataInExample --graphTitle "Pre process results" --savePlot "preProcessResult.eps" 

# Example time line graph
python3 scientoPy.py authorKeywords --startYear 2010 --endYear 2016 --graphTitle "Internet of things top author keywords" --savePlot "graph_timeline.eps"

# Example time line graph
python3 scientoPy.py authorKeywords --startYear 2010 --endYear 2016 --bar --graphTitle "Internet of things top author keywords" --savePlot "graph_bar.eps"

# Example time line graph
python3 scientoPy.py authorKeywords --startYear 2010 --endYear 2016 -l 500 --wordCloud --savePlot "graph_word_cloud.eps"

# Example time line graph
python3 scientoPy.py authorKeywords --startYear 2010 --endYear 2016 --parametric --graphTitle "Internet of things top author keywords" --savePlot "graph_parametric.eps"


python3 scientoPy.py authorKeywords --startYear 2006 --endYear 2017 -l 10 -s 8 --trend --parametric --agrForGraph --graphTitle "Internet of things trending topics" --savePlot "trend_parametric.eps"


# Top topics:
python3 scientoPy.py authorKeywords -t "WSN,Wireless sensor network,Wireless sensor networks;RFID,RADIO FREQUENCY IDENTIFICATION;Cloud computing;Security;Big data;Privacy;Smart City;6LoWPAN;Sensors;Zigbee" --startYear 2006 --graphTitle "Internet of things top topics" --savePlot "keywords.eps"

# Applications:
python3 scientoPy.py authorKeywords -t "Cyber-physical systems,CYBER PHYSICAL SYSTEMS,CPS;Healthcare,E-Health;Energy efficiency;Social networks,Social networks,Social media;Education,Learning,E-Learning,mobile learning" --startYear 2006 --graphTitle "Internet of things top applications" --savePlot "applications.eps"

# Smart things
python3 scientoPy.py authorKeywords -t "Smart city,Smart cities;Smart home,Smart homes;Smart grid,Smart grids;Smart objects,Smart object,Smart enviroments,Smart enviroment;Smart buildings,Smart Building;Smart devices;Smart factory" --startYear 2006 --graphTitle "Internet of things top smart things" --savePlot "smart_things.eps"

# Software processing:
python3 scientoPy.py authorKeywords -t "Machine learning;Data mining;Complex event processing,CEP;Hadoop" --startYear 2006 --graphTitle "Internet of things top software processing"  --savePlot "software.eps"

# Operating systems:
python3 scientoPy.py authorKeywords -t "Android,Android OS;Contiki,Contiki OS;Linux,Linux OS;iOS,iPhone Operating System,iPhone Operating System (iOS);Windows,Windows OS" --startYear 2006 --graphTitle "Internet of things top operating systems" --savePlot "operating.eps"

# Hardware processing:
python3 scientoPy.py authorKeywords -t "Raspberry Pi;Arduino,Arduino board;Smartphone,Smartphones,Smart phone,Smart phones;FPGA,Field-programmable gate array,Field programmable gate array;Microcontroller,Microcontrollers" --startYear 2006 --graphTitle "Internet of things top hardware devices" --savePlot "hardware.eps"

# Media layers:
python3 scientoPy.py authorKeywords -t "RFID,RADIO FREQUENCY IDENTIFICATION;6LoWPAN;ZigBee;BLE,Bluetooth Low Energy;WiFi,Wi-Fi;5G;RPL" --startYear 2006 --graphTitle "Internet of things media layer protocols" --savePlot "media_layers.eps"

# Host layers:
python3 scientoPy.py authorKeywords -t "CoAP,Constrained Application Protocol;MQTT,Message Queue Telemetry Transport;DTLS,Datagram Transport Layer Security;TCP;iBeacon;JSON;UDP" --startYear 2006 --graphTitle "Internet of things host layer protocols" --savePlot "host_layers.eps"

# Countries:
python3 scientoPy.py country --startYear 2002 -l 7 --pYear --graphTitle "Internet of things top countries" --savePlot "countries.eps"
#python3 scientoPy.py country -t "Colombia;Argentina;Ecuador"

# Authors:
python3 scientoPy.py author --startYear 2006 -l 5 --graphTitle "Internet of things top authors" --savePlot "authors.eps"

# Subject
python3 scientoPy.py subject --startYear 2006 -l 7 --graphTitle "Internet of things top subjects" --savePlot "subject.eps"


# Parametric *************************
python3 scientoPy.py authorKeywords -t "WSN,Wireless sensor network,Wireless sensor networks;RFID,RADIO FREQUENCY IDENTIFICATION;Cloud computing;Security;Big data;Privacy;Smart City;6LoWPAN;Sensors;Zigbee" --endYear 2016 --parametric --startYear 2014 --graphTitle "Internet of things top topics" --savePlot "keywords_parametric.eps"

python3 scientoPy.py authorKeywords -t "Android,Android OS;Contiki,Contiki OS;Linux,Linux OS;iOS,iPhone Operating System,iPhone Operating System (iOS);Windows,Windows OS" --endYear 2016 --parametric --graphTitle "Internet of things top operating systems" --savePlot "operating_parametric.eps"
