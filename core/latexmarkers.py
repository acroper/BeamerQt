"""
Beamer QT
Copyright (C) 2026  Jorge Guerrero - acroper@gmail.com
Generated with AI help.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

# Comment lines written into the generated LaTeX so that BeamerQt can read it
# back (see core/importlatex.py). LaTeX ignores them. A marker looks like
#
#   % BQT:block type=Normal title=Overview
#
# Values are URL-quoted, so they never contain spaces. Item markers carry the
# item's saved XML, compressed, in a "data" value.

import base64
import zlib
from urllib.parse import quote, unquote
import xml.etree.ElementTree as ET


PREFIX = "% BQT:"

VERSION = "1"


def Marker(kind, **attrs):
    parts = [PREFIX + kind]
    for key, value in attrs.items():
        parts.append(key + "=" + quote(str(value), safe=""))
    return " ".join(parts)


def ParseMarker(line):
    """(kind, attrs) for a marker line, or None for any other line."""
    line = line.strip()
    if not line.startswith(PREFIX):
        return None
    parts = line[len(PREFIX):].split()
    if not parts:
        return None
    attrs = {}
    for part in parts[1:]:
        key, _, value = part.partition("=")
        attrs[key] = unquote(value)
    return parts[0], attrs


def EncodeXML(element):
    return base64.b64encode(zlib.compress(ET.tostring(element, encoding="utf-8"))).decode("ascii")


def DecodeXML(data):
    return ET.fromstring(zlib.decompress(base64.b64decode(data)))
