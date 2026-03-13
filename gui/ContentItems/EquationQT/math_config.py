# math_config.py
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

# 1. SIMPLE SYMBOLS (Expansion Engine)
SYMBOLS = {
    # Operators
    "\\pm": "\u00B1", "\\oplus": "\u2295", "\\times": "\u00D7", 
    "\\otimes": "\u2297", "\\div": "\u00F7", "\\cdot": "\u22C5", 
    "\\bigcirc": "\u25EF", "\\bullet": "\u2219",
    # Arrows
    "\\leftarrow": "\u2190", "\\rightarrow": "\u2192", "\\uparrow": "\u2191", 
    "\\downarrow": "\u2193", "\\Leftarrow": "\u21D0", "\\Rightarrow": "\u21D2",
    "\\Uparrow": "\u21D1", "\\Downarrow": "\u21D3", "\\nearrow": "\u2197",
    "\\nwarrow": "\u2196", "\\searrow": "\u2198", "\\swarrow": "\u2199",
    # Greek
    "\\alpha": "\u03B1", "\\Alpha": "\u0391", "\\beta": "\u03B2", "\\Beta": "\u0392",
    "\\gamma": "\u03B3", "\\Gamma": "\u0393", "\\delta": "\u03B4", "\\Delta": "\u0394",
    "\\epsilon": "\u03B5", "\\Epsilon": "\u0395", "\\zeta": "\u03B6", "\\Zeta": "\u0396",
    "\\eta": "\u03B7", "\\Eta": "\u0397", "\\theta": "\u03B8", "\\Theta": "\u0398",
    "\\lambda": "\u03BB", "\\Lambda": "\u039B", "\\pi": "\u03C0", "\\Pi": "\u03A0",
    "\\sigma": "\u03C3", "\\Sigma": "\u03A3", "\\omega": "\u03C9", "\\Omega": "\u03A9",
    # Other symbols
    "\\nabla": "\u2207", "\\partial": "\u2202", "\\infty": "\u221E", "\\prime": "\u2032",
    "\\exists": "\u2203", "\\mathcal{F}": "\u2131", "\\mathcal{O}": "\u2134",
}

# 2. BLOCKS AND MODIFIERS (No changes)
BLOCKS = {
    "\\frac": {"type": "fraction"}, "\\sum": {"type": "operator", "symbol": "\u2211"},
    "\\int": {"type": "operator", "symbol": "\u222B"},
    "\\sqrt": {"type": "root"}, "\\matrix": {"type": "matrix"}
}
MODIFIERS = {"^": {"slot": "sup"}, "_": {"slot": "sub"}}

# 3. CATALOG FOR THE INTERFACE (Buttons)
SYMBOL_CATALOG = {
    "Operators": [
        ["±", "\\pm"], ["⊕", "\\oplus"], ["×", "\\times"], 
        ["⊗", "\\otimes"], ["÷", "\\div"], ["·", "\\cdot"], 
        ["○", "\\bigcirc"], ["∙", "\\bullet"]
    ],
    "Arrows": [
        ["←", "\\leftarrow"], ["→", "\\rightarrow"], ["↑", "\\uparrow"], ["↓", "\\downarrow"],
        ["⇐", "\\Leftarrow"], ["⇒", "\\Rightarrow"], ["⇑", "\\Uparrow"], ["⇓", "\\Downarrow"],
        ["↗", "\\nearrow"], ["↖", "\\nwarrow"], ["↘", "\\searrow"], ["↙", "\\swarrow"]
    ],
    "Greek": [
        ["α", "\\alpha"], ["Α", "\\Alpha"], ["β", "\\beta"], ["Β", "\\Beta"],
        ["γ", "\\gamma"], ["Γ", "\\Gamma"], ["δ", "\\delta"], ["Δ", "\\Delta"],
        ["ε", "\\epsilon"], ["Ε", "\\Epsilon"], ["θ", "\\theta"], ["Θ", "\\Theta"],
        ["π", "\\pi"], ["Π", "\\Pi"], ["σ", "\\sigma"], ["Σ", "\\Sigma"],
        ["ω", "\\omega"], ["Ω", "\\Omega"]
    ],
    "Symbols": [
        ["∇", "\\nabla"], ["∂", "\\partial"], ["∞", "\\infty"], ["′", "\\prime"],
        ["∃", "\\exists"], ["ℱ", "\\mathcal{F}"], ["ℴ", "\\mathcal{O}"]
    ],
}

BLOCK_CATALOG = {
    "Structures": [
        ["⬚/⬚", "\\frac"], ["∑", "\\sum"], ["∫", "\\int"], ["√", "\\sqrt"], ["⊞", "\\matrix"]
    ]
}
