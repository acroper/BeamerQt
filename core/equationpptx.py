"""
Beamer QT
Copyright (C) 2025  Jorge Guerrero - acroper@gmail.com

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

# Converts Office Math (OMML) equations, as stored in PowerPoint files, to LaTeX.
# Covers the common elements; anything unknown is converted from its contents.


M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"


def m(tag):
    return "{" + M_NS + "}" + tag


SYMBOLS = {
    # Greek
    "α": "\\alpha", "β": "\\beta", "γ": "\\gamma", "δ": "\\delta", "ε": "\\varepsilon",
    "ϵ": "\\epsilon", "ζ": "\\zeta", "η": "\\eta", "θ": "\\theta", "ϑ": "\\vartheta",
    "ι": "\\iota", "κ": "\\kappa", "λ": "\\lambda", "μ": "\\mu", "ν": "\\nu", "ξ": "\\xi",
    "π": "\\pi", "ϖ": "\\varpi", "ρ": "\\rho", "ϱ": "\\varrho", "σ": "\\sigma",
    "ς": "\\varsigma", "τ": "\\tau", "υ": "\\upsilon", "φ": "\\varphi", "ϕ": "\\phi",
    "χ": "\\chi", "ψ": "\\psi", "ω": "\\omega",
    "Γ": "\\Gamma", "Δ": "\\Delta", "Θ": "\\Theta", "Λ": "\\Lambda", "Ξ": "\\Xi",
    "Π": "\\Pi", "Σ": "\\Sigma", "Υ": "\\Upsilon", "Φ": "\\Phi", "Ψ": "\\Psi", "Ω": "\\Omega",
    # Operators and relations
    "±": "\\pm", "∓": "\\mp", "×": "\\times", "÷": "\\div", "·": "\\cdot", "⋅": "\\cdot",
    "∗": "*", "∘": "\\circ", "−": "-", "≤": "\\leq", "≥": "\\geq", "≠": "\\neq",
    "≈": "\\approx", "≡": "\\equiv", "∼": "\\sim", "≃": "\\simeq", "≅": "\\cong",
    "∝": "\\propto", "≪": "\\ll", "≫": "\\gg", "∈": "\\in", "∉": "\\notin", "∋": "\\ni",
    "⊂": "\\subset", "⊆": "\\subseteq", "⊃": "\\supset", "⊇": "\\supseteq",
    "∪": "\\cup", "∩": "\\cap", "∖": "\\setminus", "∅": "\\emptyset", "∀": "\\forall",
    "∃": "\\exists", "∄": "\\nexists", "¬": "\\neg", "∧": "\\wedge", "∨": "\\vee",
    "⊕": "\\oplus", "⊗": "\\otimes", "⊥": "\\perp", "∥": "\\parallel", "∠": "\\angle",
    # Arrows
    "→": "\\to", "←": "\\leftarrow", "↔": "\\leftrightarrow", "⇒": "\\Rightarrow",
    "⇐": "\\Leftarrow", "⇔": "\\Leftrightarrow", "↦": "\\mapsto", "↑": "\\uparrow",
    "↓": "\\downarrow",
    # Misc
    "∞": "\\infty", "∂": "\\partial", "∇": "\\nabla", "ℏ": "\\hbar", "ℓ": "\\ell",
    "…": "\\ldots", "⋯": "\\cdots", "⋮": "\\vdots", "⋱": "\\ddots", "′": "'", "″": "''",
    "°": "^\\circ", "ℝ": "\\mathbb{R}", "ℕ": "\\mathbb{N}", "ℤ": "\\mathbb{Z}",
    "ℚ": "\\mathbb{Q}", "ℂ": "\\mathbb{C}", "√": "\\surd",
    # Characters with a meaning in LaTeX
    "{": "\\{", "}": "\\}", "%": "\\%", "#": "\\#", "$": "\\$", "_": "\\_",
    "\\": "\\backslash", "~": "\\sim", "^": "\\hat{}",
}

NARY = {
    "∑": "\\sum", "∏": "\\prod", "∐": "\\coprod", "∫": "\\int", "∬": "\\iint",
    "∭": "\\iiint", "∮": "\\oint", "⋃": "\\bigcup", "⋂": "\\bigcap", "⋁": "\\bigvee",
    "⋀": "\\bigwedge", "⨁": "\\bigoplus", "⨂": "\\bigotimes",
}

ACCENTS = {
    "̂": "\\hat", "̃": "\\tilde", "̄": "\\bar", "̅": "\\bar",
    "⃗": "\\vec", "̇": "\\dot", "̈": "\\ddot", "̌": "\\check",
    "́": "\\acute", "̀": "\\grave", "̆": "\\breve",
}

DELIMITERS = {
    "(": "(", ")": ")", "[": "[", "]": "]", "{": "\\{", "}": "\\}", "|": "|",
    "‖": "\\|", "⟨": "\\langle", "⟩": "\\rangle", "〈": "\\langle", "〉": "\\rangle",
    "⌊": "\\lfloor", "⌋": "\\rfloor", "⌈": "\\lceil", "⌉": "\\rceil", "": ".",
}

FUNCTIONS = ("sin", "cos", "tan", "cot", "sec", "csc", "arcsin", "arccos", "arctan",
             "sinh", "cosh", "tanh", "coth", "log", "ln", "lg", "exp", "lim", "max",
             "min", "sup", "inf", "det", "dim", "ker", "deg", "gcd", "arg", "Pr")


def omml_to_latex(element):
    """LaTeX for an m:oMathPara or m:oMath element (without $ or \\[ \\])."""
    return Convert(element).strip()


def Prop(element, prop_tag, attr="val", default=None):
    # Value of a property like <m:fPr><m:type m:val="lin"/></m:fPr>
    pr = element.find(m(element.tag.split("}")[1] + "Pr"))
    if pr is None:
        return default
    node = pr.find(m(prop_tag))
    if node is None:
        return default
    return node.get(m(attr), default if default is not None else "1")


def Child(element, tag):
    node = element.find(m(tag))
    return Convert(node) if node is not None else ""


def Group(text):
    return "{" + text + "}"


def Text(text):
    out = []
    for ch in text:
        symbol = SYMBOLS.get(ch)
        if symbol is None:
            out.append(ch)
        elif symbol[0] == "\\" and symbol[-1].isalpha():
            out.append(symbol + " ")
        else:
            out.append(symbol)
    return "".join(out)


def Convert(element):
    tag = element.tag.split("}")[1] if "}" in element.tag else element.tag

    if tag.endswith("Pr"):
        return ""

    if tag == "oMathPara":
        return " \\\\ ".join(Convert(e) for e in element.findall(m("oMath")))

    if tag == "r":
        text = "".join(t.text or "" for t in element.findall(m("t")))
        if text in FUNCTIONS:
            return "\\" + text + " "
        return Text(text)

    if tag == "f":
        num, den = Child(element, "num"), Child(element, "den")
        kind = Prop(element, "type")
        if kind == "lin":
            return Group(num) + "/" + Group(den)
        if kind == "noBar":
            return "\\genfrac{}{}{0pt}{}" + Group(num) + Group(den)
        return "\\frac" + Group(num) + Group(den)

    if tag == "sSup":
        return Group(Child(element, "e")) + "^" + Group(Child(element, "sup"))

    if tag == "sSub":
        return Group(Child(element, "e")) + "_" + Group(Child(element, "sub"))

    if tag == "sSubSup":
        return (Group(Child(element, "e")) + "_" + Group(Child(element, "sub"))
                + "^" + Group(Child(element, "sup")))

    if tag == "sPre":
        return ("{}_" + Group(Child(element, "sub")) + "^" + Group(Child(element, "sup"))
                + Group(Child(element, "e")))

    if tag == "rad":
        degree = Child(element, "deg")
        if Prop(element, "degHide") in ("1", "on", "true") or degree == "":
            return "\\sqrt" + Group(Child(element, "e"))
        return "\\sqrt[" + degree + "]" + Group(Child(element, "e"))

    if tag == "nary":
        op = NARY.get(Prop(element, "chr", default="∫"), "\\int")
        out = op
        if Prop(element, "subHide") not in ("1", "on", "true"):
            sub = Child(element, "sub")
            if sub:
                out += "_" + Group(sub)
        if Prop(element, "supHide") not in ("1", "on", "true"):
            sup = Child(element, "sup")
            if sup:
                out += "^" + Group(sup)
        return out + " " + Child(element, "e")

    if tag == "d":
        begin = Prop(element, "begChr", default="(")
        end = Prop(element, "endChr", default=")")
        sep = Prop(element, "sepChr", default="|")
        inner = (" " + DELIMITERS.get(sep, sep) + " ").join(Convert(e) for e in element.findall(m("e")))
        return ("\\left" + DELIMITERS.get(begin, begin) + " " + inner + " \\right"
                + DELIMITERS.get(end, end))

    if tag == "m":
        rows = []
        for row in element.findall(m("mr")):
            rows.append(" & ".join(Convert(e) for e in row.findall(m("e"))))
        return "\\begin{matrix} " + " \\\\ ".join(rows) + " \\end{matrix}"

    if tag == "eqArr":
        rows = [Convert(e) for e in element.findall(m("e"))]
        return "\\begin{aligned} " + " \\\\ ".join(rows) + " \\end{aligned}"

    if tag == "func":
        name = Child(element, "fName").strip()
        if not name.startswith("\\") and name.isalpha():
            name = "\\operatorname{" + name + "}"
        return name + " " + Child(element, "e")

    if tag == "acc":
        command = ACCENTS.get(Prop(element, "chr", default="̂"), "\\hat")
        return command + Group(Child(element, "e"))

    if tag == "bar":
        command = "\\overline" if Prop(element, "pos", default="bot") == "top" else "\\underline"
        return command + Group(Child(element, "e"))

    if tag == "groupChr":
        command = "\\overbrace" if Prop(element, "pos", default="bot") == "top" else "\\underbrace"
        return command + Group(Child(element, "e"))

    if tag == "limLow":
        base = Child(element, "e").strip()
        if base in ("\\lim", "\\max", "\\min", "\\sup", "\\inf"):
            return base + "_" + Group(Child(element, "lim"))
        return Group(base) + "_" + Group(Child(element, "lim"))

    if tag == "limUpp":
        return "\\overset" + Group(Child(element, "lim")) + Group(Child(element, "e"))

    if tag == "borderBox":
        return "\\boxed" + Group(Child(element, "e"))

    # oMath, e, num, den, sub, sup, box, phant and anything unknown: just the contents
    return "".join(Convert(child) for child in element)
