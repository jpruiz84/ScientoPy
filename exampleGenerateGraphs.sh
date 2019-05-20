#!/bin/bash

# Pre process
python3 preProcess.py dataInExample --graphTitle "Pre process brief results" --savePlot "pre_process_brief.eps"

# Example time line graph
python3 scientoPy.py -c authorKeywords --startYear 2008 --endYear 2018 -g time_line --graphTitle "Top author keywords" --savePlot "graph_time_line.eps"

# Example horizontal graph bar
python3 scientoPy.py -c authorKeywords --startYear 2008 --endYear 2018 -g bar --graphTitle "Top author keywords" --savePlot "graph_bar.eps"

# Example horizontal graph bar with relative percentage growth
python3 scientoPy.py -c authorKeywords --startYear 2008 --endYear 2018 -g bar_trends --graphTitle "Top author keywords" --savePlot "graph_bar_trends.eps"

# Example evolution graph
python3 scientoPy.py -c authorKeywords --startYear 2008 --endYear 2018 -g evolution --graphTitle "Top author keywords" --savePlot "graph_evolution.eps"

# Example word cloud graph
python3 scientoPy.py -c authorKeywords --startYear 2008 --endYear 2018 -l 500 -g word_cloud --savePlot "graph_word_cloud.eps"

# Example top trending topics with the highest AGR using evolution graph
python3 scientoPy.py -c authorKeywords --trend --startYear 2008 --endYear 2018 -g evolution --agrForGraph --graphTitle "Trending top author keywords" --savePlot "graph_trending_with_agr.eps"

# Example custom topics in authorKeywords
python3 scientoPy.py -c authorKeywords -t "Smart City;Smart-Guide;Smart Library;Smart device;Smart Home;smart clothing system;smartphone;smart museum;Smart Environments;Smart devices;smart community;Smart cities;smart grid;smart sensors" -g bar --startYear 2008 --endYear 2018 --graphTitle "Smart applications in BLE" --savePlot "graph_smart_applications.eps"

# Example custom grouped topics in authorKeyrwords
python3 scientoPy.py -c authorKeywords -t "Internet of Things, IoT,Internet of Things (IoT); Indoor positioning, indoor localization; Beacon, iBeacon, Beacons; low power; wireless sensor networks, wireless sensor network, WSN" -g bar --startYear 2008 --endYear 2018 --graphTitle "Group of author keywords" --savePlot "graph_group_topics.eps"


# Example top countries graph
python3 scientoPy.py -c country --startYear 2008 --endYear 2018 -g evolution --graphTitle "Top countries" --savePlot "graph_top_countries.eps"

# Example top author graph
python3 scientoPy.py -c author --startYear 2008 --endYear 2018 -g evolution --graphTitle "Top authors" --savePlot "graph_top_authors.eps"

# Example of analysis based on the previous results, to get Canada's top authorKeywords and top collaboration countries
python3 scientoPy.py -c country -t "Canada" --noPlot
python3 scientoPy.py -c authorKeywords -r -g bar --graphTitle "Top Canada's author keywords" --savePlot "graph_canada_top_authors_keywords.eps"
python3 scientoPy.py -c country -r -g bar --graphTitle "Top Canada's collaboration countries" --savePlot "graph_canada_top_collaboration_countries.eps"

# Example of the filter to get the top institution of a specific country
python3 scientoPy.py -c institutionWithCountry -f "Colombia" --startYear 2008 --endYear 2018 -g bar --graphTitle "Top Colombia's institutions" --savePlot "graph_institutions_from_colombia.eps"

