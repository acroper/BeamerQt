"""
Central registry for content items that can be added to a block.

Keeping this in one place avoids hard-coding button/menu wiring across widgets.
"""

# `CONTENT_ITEMS` describes what appears in the "Add..." menu for blocks.
#
# Fields:
# - `type`: Required. The internal item type string used by `ContentItem.setItemType(...)`
#           and later by the LaTeX/XML pipeline (e.g. "Text", "RTF", "Image", "EquationQT").
# - `label`: Required. Human-friendly name shown in the UI menu.
# - `icon` (optional): Icon path (Qt resource or filesystem path) for the menu action.
# - `order` (optional): Integer sort key; lower values appear first (defaults to list order).
CONTENT_ITEMS = [
    {"type": "Text", "label": "Plain Text"},
    {"type": "RTF", "label": "Rich Text"},
    {"type": "Image", "label": "Image"},
    {"type": "EquationQT", "label": "Equation"},
    {"type": "Table", "label": "Table"},
]
