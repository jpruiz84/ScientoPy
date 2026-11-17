#!/usr/bin/env python3

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

"""Builds worldMapData/countries.json, the country outlines of the world map.

Only needed to regenerate the file. The outlines come from Natural Earth
(public domain, https://www.naturalearthdata.com), Admin 0 - Countries:

    ne_110m_admin_0_countries.geojson   outlines of the 177 larger countries
    ne_50m_admin_0_countries.geojson    the small countries the 110m file leaves
                                        out (Singapore, Hong Kong, Malta, ...)

Both are in https://github.com/nvkelso/natural-earth-vector under geojson/.

Usage:
    python3 worldMapData/buildCountries.py ne_110m_admin_0_countries.geojson \
        ne_50m_admin_0_countries.geojson
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from worldMap import normalize_name  # noqa: E402

# Display names follow the country names ScientoPy writes in the preprocess
DISPLAY_NAMES = {
    "United States of America": "United States",
    "Russia": "Russian Federation",
    "Republic of Serbia": "Serbia",
    "United Republic of Tanzania": "Tanzania",
    "The Bahamas": "Bahamas",
    "Hong Kong S.A.R.": "Hong Kong",
    "Macao S.A.R": "Macao",
    "Republic of the Congo": "Congo",
    "eSwatini": "Eswatini",
    "East Timor": "Timor-Leste",
    "Federated States of Micronesia": "Micronesia",
}

# Names used by Scopus and WoS that Natural Earth does not list
EXTRA_ALIASES = {
    "United States of America": ["USA", "US", "U S A", "United States"],
    "United Kingdom": ["UK", "England", "Scotland", "Wales", "North Ireland",
                       "Northern Ireland", "Great Britain"],
    "China": ["Peoples R China", "PR China", "P R China", "Mainland China"],
    "Russia": ["Russian Federation", "USSR"],
    "South Korea": ["Korea", "Republic of Korea", "Korea Republic", "Korea South",
                    "Rep of Korea"],
    "North Korea": ["DPR Korea", "Democratic Peoples Republic of Korea", "Korea North"],
    "Vietnam": ["Viet Nam"],
    "Iran": ["Islamic Republic of Iran", "Iran Islamic Republic of"],
    "Syria": ["Syrian Arab Republic"],
    "Libya": ["Libyan Arab Jamahiriya"],
    "Czechia": ["Czech Republic", "Czech Rep"],
    "Turkey": ["Turkiye", "Republic of Turkiye"],
    "Ivory Coast": ["Cote d'Ivoire", "Cote Ivoire", "Cote dIvoire"],
    "Democratic Republic of the Congo": ["Democratic Republic Congo", "Dem Rep Congo",
                                         "DR Congo", "Congo Democratic Republic", "Zaire"],
    "Republic of the Congo": ["Congo", "Rep Congo", "Congo Republic", "Peoples R Congo"],
    "Brunei": ["Brunei Darussalam"],
    "Palestine": ["State of Palestine", "Palestinian Territory", "West Bank", "Gaza"],
    "North Macedonia": ["Macedonia", "Republic of North Macedonia", "FYROM"],
    "Moldova": ["Republic of Moldova"],
    "Laos": ["Lao PDR", "Lao Peoples Democratic Republic"],
    "eSwatini": ["Swaziland", "Eswatini"],
    "Myanmar": ["Burma"],
    "East Timor": ["Timor Leste", "Timor-Leste"],
    "Cabo Verde": ["Cape Verde"],
    "Bosnia and Herzegovina": ["Bosnia & Herceg", "Bosnia Herceg", "Bosnia"],
    "Trinidad and Tobago": ["Trinid & Tobago", "Trinidad Tobago"],
    "United Arab Emirates": ["U Arab Emirates", "UAE"],
    "Dominican Republic": ["Dominican Rep"],
    "Central African Republic": ["Cent Afr Republ"],
    "Equatorial Guinea": ["Equat Guinea"],
    "Papua New Guinea": ["Papua N Guinea"],
    "Guinea-Bissau": ["Guinea Bissau"],
    "Saudi Arabia": ["Kingdom of Saudi Arabia"],
    "Belarus": ["Byelarus"],
    "Germany": ["Fed Rep Ger", "Federal Republic of Germany"],
    "Netherlands": ["The Netherlands", "Holland"],
    # Overseas departments that Scopus lists as countries; they are part of
    # the France outline
    "France": ["French Guiana", "Guadeloupe", "Martinique", "Reunion", "Mayotte"],
    "Hong Kong S.A.R.": ["Hong Kong"],
    "Macao S.A.R": ["Macao", "Macau"],
    "Republic of Serbia": ["Serbia"],
    "United Republic of Tanzania": ["Tanzania"],
    "The Bahamas": ["Bahamas"],
    "Gambia": ["The Gambia"],
    "Vatican": ["Vatican City", "Holy See"],
    "Saint Kitts and Nevis": ["St Kitts & Nevis"],
    "Saint Vincent and the Grenadines": ["St Vincent"],
    "Saint Lucia": ["St Lucia"],
    "São Tomé and Principe": ["Sao Tome & Prin", "Sao Tome and Principe"],
    "Federated States of Micronesia": ["Micronesia"],
}

# Natural Earth property fields that hold a usable country name
NAME_FIELDS = ["ADMIN", "NAME", "NAME_LONG", "FORMAL_EN", "BRK_NAME", "NAME_CIAWF",
               "NAME_EN", "ISO_A3_EH"]

LEFT_OUT = {"Antarctica"}


def _simplify(ring, tolerance):
    """Douglas-Peucker on a closed ring of [lon, lat] points."""
    if len(ring) < 5 or tolerance <= 0:
        return ring

    def reduce(points):
        if len(points) < 3:
            return points
        (x1, y1), (x2, y2) = points[0], points[-1]
        dx, dy = x2 - x1, y2 - y1
        norm = (dx * dx + dy * dy) ** 0.5
        worst, index = 0.0, 0
        for k in range(1, len(points) - 1):
            px, py = points[k]
            if norm == 0:
                dist = ((px - x1) ** 2 + (py - y1) ** 2) ** 0.5
            else:
                dist = abs(dy * px - dx * py + x2 * y1 - y2 * x1) / norm
            if dist > worst:
                worst, index = dist, k
        if worst <= tolerance:
            return [points[0], points[-1]]
        return reduce(points[:index + 1])[:-1] + reduce(points[index:])

    half = len(ring) // 2
    out = reduce(ring[:half + 1])[:-1] + reduce(ring[half:])
    return out if len(out) >= 4 else ring


def _rings(geometry, tolerance):
    """Exterior rings of a Polygon or MultiPolygon, rounded to 0.01 degrees."""
    if geometry["type"] == "Polygon":
        polygons = [geometry["coordinates"]]
    else:
        polygons = geometry["coordinates"]
    rings = []
    for polygon in polygons:
        ring = _simplify([[p[0], p[1]] for p in polygon[0]], tolerance)
        rounded = []
        for lon, lat in ring:
            point = [round(lon, 2), round(lat, 2)]
            if not rounded or rounded[-1] != point:
                rounded.append(point)
        if len(rounded) >= 4:
            rings.append(rounded)
    return rings


def _country(feature, tolerance, owner):
    """owner maps every name key to the country that holds it: a name belongs
    to the first country that takes it."""
    props = feature["properties"]
    admin = props["ADMIN"]
    name = DISPLAY_NAMES.get(admin, admin)
    candidates = [name] + EXTRA_ALIASES.get(admin, [])
    candidates += [props.get(field) for field in NAME_FIELDS]
    aliases = []
    for value in candidates:
        if not value or value == "-99":
            continue
        key = normalize_name(value)
        if owner.setdefault(key, admin) == admin and value not in aliases:
            aliases.append(value)
    return {
        "name": name,
        "iso": props.get("ISO_A3_EH") if props.get("ISO_A3_EH") != "-99" else props.get("ADM0_A3"),
        "aliases": aliases,
        "polygons": _rings(feature["geometry"], tolerance),
    }


def build(path_110m, path_50m, out_path):
    with open(path_110m, "r", encoding="utf-8") as f:
        large = json.load(f)["features"]
    with open(path_50m, "r", encoding="utf-8") as f:
        detailed = json.load(f)["features"]

    # Display names and the Scopus / WoS names are taken before any other
    # name, then the larger countries go first
    owner = {}
    for feature in large + detailed:
        admin = feature["properties"]["ADMIN"]
        owner.setdefault(normalize_name(DISPLAY_NAMES.get(admin, admin)), admin)
    for admin, names in EXTRA_ALIASES.items():
        for value in names:
            owner.setdefault(normalize_name(value), admin)

    countries = []
    seen = set()
    for feature in large:
        admin = feature["properties"]["ADMIN"]
        if admin in LEFT_OUT:
            continue
        seen.add(admin)
        countries.append(_country(feature, 0, owner))
    for feature in detailed:
        admin = feature["properties"]["ADMIN"]
        if admin in LEFT_OUT or admin in seen:
            continue
        country = _country(feature, 0.02, owner)
        if country["polygons"]:
            countries.append(country)

    countries.sort(key=lambda c: c["name"])
    data = {
        "source": "Natural Earth (public domain), naturalearthdata.com, Admin 0 - Countries, "
                  "1:110m with the small countries of 1:50m",
        "countries": countries,
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    points = sum(len(r) for c in countries for r in c["polygons"])
    print("%d countries, %d points, %.0f kB -> %s"
          % (len(countries), points, os.path.getsize(out_path) / 1000.0, out_path))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    build(sys.argv[1], sys.argv[2],
          os.path.join(os.path.dirname(os.path.abspath(__file__)), "countries.json"))
