# The MIT License (MIT)
# Copyright (c) 2026 - Universidad del Cauca, Juan Ruiz-Rosero
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

"""Country outlines, country name matching and map projection for the
world map graph (scientoPy.py -c country -g world_map).

The outlines are in worldMapData/countries.json (Natural Earth, public
domain), so the map needs no network access and no GIS packages.
"""

import json
import os
import re
import sys
import unicodedata

import numpy as np

DATA_DIR = "worldMapData"
DATA_FILE = "countries.json"

_countries = None
_alias_index = None

# Robinson projection table, one row every 5 degrees of latitude:
# parallel length and parallel distance from the equator
_ROBINSON_LAT = np.arange(0, 95, 5)
_ROBINSON_LEN = np.array([1.0000, 0.9986, 0.9954, 0.9900, 0.9822, 0.9730, 0.9600,
                          0.9427, 0.9216, 0.8962, 0.8679, 0.8350, 0.7986, 0.7597,
                          0.7186, 0.6732, 0.6213, 0.5722, 0.5322])
_ROBINSON_DIST = np.array([0.0000, 0.0620, 0.1240, 0.1860, 0.2480, 0.3100, 0.3720,
                           0.4340, 0.4958, 0.5571, 0.6176, 0.6769, 0.7346, 0.7903,
                           0.8435, 0.8936, 0.9394, 0.9761, 1.0000])


def _data_path():
    """Resolve the outlines file for both PyInstaller bundles and source mode."""
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, DATA_DIR, DATA_FILE)


def normalize_name(name):
    """Key to compare country names: no accents, punctuation or case."""
    text = unicodedata.normalize("NFKD", str(name))
    text = "".join(ch for ch in text if not unicodedata.combining(ch)).upper()
    text = text.replace("&", " AND ")
    text = re.sub(r"[^A-Z0-9 ]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    if text.startswith("THE "):
        text = text[4:]
    return text


def load_countries():
    """Countries as a list of {"name", "iso", "aliases", "polygons"}.

    Each polygon is a closed ring of [longitude, latitude] points.
    """
    global _countries, _alias_index
    if _countries is None:
        with open(_data_path(), "r", encoding="utf-8") as f:
            _countries = json.load(f)["countries"]
        _alias_index = {}
        # Display names first, so an alias never takes the name of a country
        for index, country in enumerate(_countries):
            _alias_index.setdefault(normalize_name(country["name"]), index)
        for index, country in enumerate(_countries):
            for alias in country["aliases"]:
                _alias_index.setdefault(normalize_name(alias), index)
    return _countries


def find_country(name):
    """Index in load_countries() of the country with this name, or None."""
    load_countries()
    return _alias_index.get(normalize_name(name))


def match_countries(counts):
    """Place {country name: value} on the map.

    Returns ({country index: value}, [names not found]). Names of the same
    country ("USA" and "United States") are added up.
    """
    matched = {}
    unmatched = []
    for name, value in counts.items():
        index = find_country(name)
        if index is None:
            unmatched.append(name)
        else:
            matched[index] = matched.get(index, 0) + value
    return matched, unmatched


def robinson(lon, lat):
    """Robinson projection of longitudes and latitudes in degrees.

    Returns (x, y) with x in [-2.666, 2.666] and y in [-1.352, 1.352].
    """
    lon = np.asarray(lon, dtype=float)
    lat = np.asarray(lat, dtype=float)
    abs_lat = np.abs(lat)
    length = np.interp(abs_lat, _ROBINSON_LAT, _ROBINSON_LEN)
    dist = np.interp(abs_lat, _ROBINSON_LAT, _ROBINSON_DIST)
    x = 0.8487 * length * np.radians(lon)
    y = 1.3523 * dist * np.sign(lat)
    return x, y
