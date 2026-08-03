"""
Beamer QT
Copyright (C) 2024-2026  Jorge Guerrero - acroper@gmail.com

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

"""
Standalone CSV parsing helper for the Plot content item. Depends only on the
Python standard library, so it can be reused outside of the Qt widgets too.
"""

import csv
import os

DELIMITERS = {
    "Comma (,)": ",",
    "Semicolon (;)": ";",
    "Tab": "\t",
    "Pipe (|)": "|",
}

# Placeholders the LaTeX box shows instead of literal derived data (a
# categorical axis's unique values, a histogram's computed bin counts) --
# resolved with fresh values from the CSV only at actual compile time (see
# resolve_tags), so the box stays readable and edits to the source CSV are
# picked up automatically. Each is always placed on its own line by the
# generator, so if left unresolved, "%" turns that single line into a no-op
# LaTeX comment instead of corrupting the surrounding syntax.
TAG_XCOORDS = "%[BQT_XCOORDS]"
TAG_HISTDATA = "%[BQT_HISTDATA]"


def sniff_delimiter(path, sample_size=4096):
    """Best-effort guess of the column delimiter used by a CSV file."""
    try:
        with open(path, newline='', encoding='utf-8-sig') as f:
            sample = f.read(sample_size)
        dialect = csv.Sniffer().sniff(sample, delimiters=[',', ';', '\t', '|'])
        return dialect.delimiter
    except (csv.Error, OSError):
        return ","


def read_csv(path, delimiter=",", has_header=True):
    """
    Read a CSV file and return (headers, columns).

    - headers: list of column names, in file order (first row if has_header,
      otherwise auto-generated "Column 1", "Column 2", ...).
    - columns: dict mapping header -> list of raw string values (one per row).
    """
    with open(path, newline='', encoding='utf-8-sig') as f:
        reader = csv.reader(f, delimiter=delimiter)
        rows = [row for row in reader if row]

    if not rows:
        return [], {}

    if has_header:
        headers = [h.strip() for h in rows[0]]
        data_rows = rows[1:]
    else:
        headers = [f"Column {i + 1}" for i in range(len(rows[0]))]
        data_rows = rows

    columns = {h: [] for h in headers}
    for row in data_rows:
        for i, h in enumerate(headers):
            columns[h].append(row[i] if i < len(row) else "")

    return headers, columns


def to_float(value, decimal="."):
    """Convert a raw CSV string to float, honoring the decimal separator."""
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    if decimal == ",":
        value = value.replace(".", "").replace(",", ".")
    try:
        return float(value)
    except ValueError:
        return None


def get_numeric_column(columns, header, decimal="."):
    """Return the numeric (float or None) values of a column."""
    return [to_float(v, decimal) for v in columns.get(header, [])]


def is_numeric_column(columns, header, decimal="."):
    """True if every non-empty value in the column parses as a number."""
    values = columns.get(header, [])
    for v in values:
        if v is not None and v.strip() != "" and to_float(v, decimal) is None:
            return False
    return True


# With more categories than this showing on an axis, thin the visible tick
# labels automatically (unless the user forces a specific step) so they
# stop overlapping -- e.g. a 90-row date column would otherwise put 90
# crammed labels under the axis.
MAX_VISIBLE_TICKS = 10


def symbolic_x_coords_fragment(columns, x_header, decimal=".", step=0):
    """
    pgfplots axis-option fragment for a categorical X column: its unique
    values as `symbolic x coords`, and an `xtick={...}` listing only every
    `step`-th one (plus the last, for context) so labels don't overlap.
    step<=0 picks a step automatically from MAX_VISIBLE_TICKS; step=1 shows
    every label. Empty string if no column is given or it's actually numeric
    (no option needed).
    """
    if not x_header or is_numeric_column(columns, x_header, decimal):
        return ""

    unique = []
    for v in columns.get(x_header, []):
        if v not in unique:
            unique.append(v)

    if step <= 0:
        step = max(1, -(-len(unique) // MAX_VISIBLE_TICKS))  # ceil division

    tick_indices = list(range(0, len(unique), step))
    if tick_indices[-1] != len(unique) - 1:
        tick_indices.append(len(unique) - 1)
    ticks = [unique[i] for i in tick_indices]

    return (
        "symbolic x coords={" + ",".join(unique) + "}, "
        "xtick={" + ",".join(ticks) + "}"
    )


def histogram_bin_coordinates(values, bins):
    """
    Bin raw numeric values into `bins` equal-width buckets and return the
    pgfplots `coordinates {...}` content: '(edge0,count0) ... (edgeN,0)'.
    Empty string if there's nothing to bin.
    """
    values = [v for v in values if v is not None]
    if not values or bins < 1:
        return ""

    min_val = min(values)
    max_val = max(values)
    if min_val == max_val:
        min_val -= 0.5
        max_val += 0.5

    bin_width = (max_val - min_val) / bins
    counts = [0] * bins
    for v in values:
        idx = int((v - min_val) / bin_width)
        idx = max(0, min(idx, bins - 1))
        counts[idx] += 1

    edges = [min_val + i * bin_width for i in range(bins + 1)]
    coords = " ".join(f"({edges[i]:.6g},{counts[i]})" for i in range(bins))
    coords += f" ({edges[bins]:.6g},0)"
    return coords


def resolve_tags(latex_body, series, csv_path, delimiter, decimal, has_header, bins, xtick_step=0):
    """
    Replace any %[BQT_...] placeholders in latex_body with values freshly
    computed from the CSV, re-read at this exact moment -- so edits to the
    source CSV are picked up on the next compile even if the surrounding
    LaTeX was hand-edited. A no-op if neither tag is present, the CSV can't
    be read, or there's no series to resolve them against.
    """
    if TAG_XCOORDS not in latex_body and TAG_HISTDATA not in latex_body:
        return latex_body

    if not series or not csv_path or not os.path.exists(csv_path):
        return latex_body

    try:
        headers, columns = read_csv(csv_path, delimiter=delimiter, has_header=has_header)
    except OSError:
        return latex_body

    if TAG_XCOORDS in latex_body:
        x_header = series[0].get("X", "")
        fragment = symbolic_x_coords_fragment(columns, x_header, decimal, step=xtick_step)
        latex_body = latex_body.replace(TAG_XCOORDS, fragment)

    if TAG_HISTDATA in latex_body:
        y_header = series[0].get("Y", "")
        values = get_numeric_column(columns, y_header, decimal)
        coords = histogram_bin_coordinates(values, bins)
        latex_body = latex_body.replace(TAG_HISTDATA, coords)

    return latex_body


def write_normalized_csv(path, out_path, delimiter=",", decimal=".", has_header=True):
    """
    Re-read a CSV using its actual format (delimiter/decimal/header) and write a
    pgfplots-friendly version of it: comma-delimited, period-decimal numeric
    columns, text/categorical columns passed through unchanged. pgfplots' own
    `table` reader relies on TeX's number parser, which does not understand a
    comma as a decimal point and doesn't know the source delimiter, so the
    generated LaTeX is always written to expect this normalized form rather
    than the user's original file verbatim.

    Returns the (headers, columns) that were read, for convenience.
    """
    headers, columns = read_csv(path, delimiter=delimiter, has_header=has_header)

    row_count = max((len(v) for v in columns.values()), default=0)
    numeric = {h: is_numeric_column(columns, h, decimal) for h in headers}

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for i in range(row_count):
            row = []
            for h in headers:
                values = columns[h]
                raw = values[i] if i < len(values) else ""
                if numeric[h]:
                    num = to_float(raw, decimal)
                    row.append("" if num is None else repr(num))
                else:
                    row.append(raw)
            writer.writerow(row)

    return headers, columns
