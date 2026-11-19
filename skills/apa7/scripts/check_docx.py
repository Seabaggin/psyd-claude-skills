#!/usr/bin/env python3
"""
check_docx.py -- Extract APA-7-relevant structure from a Word (.docx) file.

Why this exists
---------------
APA formatting is half *content* (citations, references, mechanics) and half
*visual layout* (margins, font, line spacing, page numbers, hanging indents).
An LLM reads content well but eyeballs layout poorly -- it cannot "see" that a
margin is 1.25" or that a reference paragraph uses a first-line indent instead
of a hanging indent. This script does the layout half deterministically so the
agent can trust those facts and spend its judgment on the content half.

A .docx is just a ZIP of XML parts, so this uses ONLY the Python standard
library (zipfile + ElementTree). No pip install required.

What it reports
---------------
  * Page margins and page size (inches)
  * Fonts and point sizes actually used in the body (with counts)
  * Line spacing values found in body paragraphs (double? single?)
  * Whether a page number exists, and where (header/footer, alignment)
  * Any running-head text (student papers should have none)
  * Every paragraph's effective formatting (style, alignment, indents,
    font/size/bold/italic, text preview) in document order
  * `structural_findings`: deterministic, layout-level rule violations it is
    confident about (each with a severity)

What it does NOT do
-------------------
It does not judge citations, reference-entry correctness, heading *wording*,
number style, etc. That is the agent's job, using references/apa7-rules.md and
the extracted paragraph text this script provides.

Usage
-----
    python3 check_docx.py /path/to/paper.docx           # readable report
    python3 check_docx.py /path/to/paper.docx --json    # JSON only (for the agent)
    python3 check_docx.py /path/to/paper.docx --full     # readable report + every paragraph
"""

import sys
import json
import zipfile

# A .docx is normally your own file, but parsing untrusted XML with the stdlib
# risks entity-expansion attacks (billion laughs / XXE). Prefer defusedxml when
# it is installed; otherwise fall back to the stdlib so the script keeps working
# with zero dependencies. Modern stdlib ElementTree does not fetch external
# entities, so the residual risk is small for ordinary documents.
try:
    import defusedxml.ElementTree as ET  # type: ignore
except ImportError:
    import xml.etree.ElementTree as ET

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
TWIPS_PER_INCH = 1440.0

# Recommended APA-7 fonts and their expected point size. Any legible font used
# consistently is technically allowed, so a font off this list is a soft warning,
# not a hard error.
APA_FONTS = {
    "Times New Roman": 12,
    "Georgia": 11,
    "Calibri": 11,
    "Arial": 11,
    "Lucida Sans Unicode": 10,
    "Computer Modern": 10,
    "CMU Serif": 10,
}


def q(tag):
    return f"{{{W}}}{tag}"


def onoff(el):
    """Interpret a toggle element like <w:b/> (on) or <w:b w:val="0"/> (off)."""
    if el is None:
        return None
    v = el.get(q("val"))
    if v is None:
        return True
    return v not in ("0", "false", "none", "off")


def parse_rpr(rpr):
    out = {}
    if rpr is None:
        return out
    rfonts = rpr.find(q("rFonts"))
    if rfonts is not None:
        font = rfonts.get(q("ascii")) or rfonts.get(q("hAnsi")) or rfonts.get(q("cs"))
        if font:
            out["font"] = font
    sz = rpr.find(q("sz"))
    if sz is not None and sz.get(q("val")):
        try:
            out["size"] = int(sz.get(q("val"))) / 2.0
        except ValueError:
            pass
    b = rpr.find(q("b"))
    if b is not None:
        out["bold"] = onoff(b)
    i = rpr.find(q("i"))
    if i is not None:
        out["italic"] = onoff(i)
    return out


def parse_ppr(ppr):
    out = {}
    if ppr is None:
        return out
    ps = ppr.find(q("pStyle"))
    if ps is not None:
        out["pStyle"] = ps.get(q("val"))
    jc = ppr.find(q("jc"))
    if jc is not None:
        out["align"] = jc.get(q("val"))
    spacing = ppr.find(q("spacing"))
    if spacing is not None:
        if spacing.get(q("line")):
            try:
                out["line"] = int(spacing.get(q("line")))
            except ValueError:
                pass
        if spacing.get(q("lineRule")):
            out["lineRule"] = spacing.get(q("lineRule"))
    ind = ppr.find(q("ind"))
    if ind is not None:
        for xml_key, out_key in (("firstLine", "firstLine"), ("hanging", "hanging"),
                                 ("left", "left"), ("start", "left")):
            v = ind.get(q(xml_key))
            if v is not None:
                try:
                    out[out_key] = int(v)
                except ValueError:
                    pass
    return out


def parse_styles(xml_bytes):
    styles, docdefaults, default_para_style = {}, {}, None
    if not xml_bytes:
        return styles, docdefaults, default_para_style
    root = ET.fromstring(xml_bytes)
    dd = root.find(q("docDefaults"))
    if dd is not None:
        docdefaults = {
            "rpr": parse_rpr(dd.find(f"{q('rPrDefault')}/{q('rPr')}")),
            "ppr": parse_ppr(dd.find(f"{q('pPrDefault')}/{q('pPr')}")),
        }
    for st in root.findall(q("style")):
        sid = st.get(q("styleId"))
        if sid is None:
            continue
        name_el = st.find(q("name"))
        based_el = st.find(q("basedOn"))
        styles[sid] = {
            "id": sid,
            "name": name_el.get(q("val")) if name_el is not None else sid,
            "basedOn": based_el.get(q("val")) if based_el is not None else None,
            "rpr": parse_rpr(st.find(q("rPr"))),
            "ppr": parse_ppr(st.find(q("pPr"))),
        }
        if st.get(q("type")) == "paragraph" and onoff(st.find(q("default"))) is True:
            default_para_style = sid
    return styles, docdefaults, default_para_style


def resolve_style(sid, styles, docdefaults):
    """Merge a style's basedOn chain over docDefaults; base-most applied first."""
    rpr = dict(docdefaults.get("rpr", {}))
    ppr = dict(docdefaults.get("ppr", {}))
    chain, seen, cur = [], set(), sid
    while cur and cur in styles and cur not in seen:
        seen.add(cur)
        chain.append(styles[cur])
        cur = styles[cur].get("basedOn")
    for st in reversed(chain):
        rpr.update(st["rpr"])
        ppr.update(st["ppr"])
    return {"rpr": rpr, "ppr": ppr}


def merge(base, overlay):
    out = {"rpr": dict(base["rpr"]), "ppr": dict(base["ppr"])}
    out["rpr"].update(overlay.get("rpr", {}))
    out["ppr"].update(overlay.get("ppr", {}))
    return out


def para_text(p):
    return "".join(t.text or "" for t in p.iter(q("t")))


def spacing_label(ppr):
    line, rule = ppr.get("line"), ppr.get("lineRule", "auto")
    if line is None:
        return None
    if rule in (None, "auto"):
        mult = line / 240.0
        return f"{mult:g}x" + (" (double)" if abs(mult - 2.0) < 0.05 else
                               " (single)" if abs(mult - 1.0) < 0.05 else "")
    return f"{line / 20.0:g}pt {rule}"


def is_double(ppr):
    line, rule = ppr.get("line"), ppr.get("lineRule", "auto")
    if line is None:
        return None  # unknown -> inherits default, judge separately
    if rule in (None, "auto"):
        return abs(line / 240.0 - 2.0) < 0.05
    return False


def inches(twips):
    return round(twips / TWIPS_PER_INCH, 3)


def find_page_number(parts):
    """Locate a PAGE field in any header/footer part; report location + alignment."""
    # Prefer headers over footers (APA wants the number in the header, top-right).
    for want in ("header", "footer"):
        for name, xmlb in parts.items():
            base = name.rsplit("/", 1)[-1]
            if not base.startswith(want):
                continue
            try:
                root = ET.fromstring(xmlb)
            except ET.ParseError:
                continue
            for p in root.iter(q("p")):
                has_page = any(
                    "PAGE" in (fs.get(q("instr")) or "").upper()
                    for fs in p.iter(q("fldSimple"))
                ) or any(
                    it.text and "PAGE" in it.text.upper()
                    for it in p.iter(q("instrText"))
                )
                if has_page:
                    jc = p.find(f"{q('pPr')}/{q('jc')}")
                    align = jc.get(q("val")) if jc is not None else "left"
                    return {"present": True, "location": want, "align": align}
    return {"present": False, "location": None, "align": None}


def header_text(parts):
    for name, xmlb in parts.items():
        base = name.rsplit("/", 1)[-1]
        if base.startswith("header"):
            try:
                root = ET.fromstring(xmlb)
            except ET.ParseError:
                continue
            txt = "".join(t.text or "" for t in root.iter(q("t"))).strip()
            if txt:
                return txt
    return ""


def analyze(path):
    with zipfile.ZipFile(path) as z:
        parts = {n: z.read(n) for n in z.namelist() if n.endswith(".xml")}

    if "word/document.xml" not in parts:
        raise ValueError("Not a valid .docx (no word/document.xml).")

    styles, docdefaults, default_ps = parse_styles(parts.get("word/styles.xml", b""))
    base_ppr = resolve_style(default_ps, styles, docdefaults) if default_ps else \
        {"rpr": dict(docdefaults.get("rpr", {})), "ppr": dict(docdefaults.get("ppr", {}))}

    doc = ET.fromstring(parts["word/document.xml"])
    body = doc.find(q("body"))

    paragraphs, font_counts, size_counts, body_spacings = [], {}, {}, []
    idx = 0
    for child in list(body):
        if child.tag != q("p"):
            continue
        idx += 1
        p = child
        eff = merge(base_ppr, {"ppr": parse_ppr(p.find(q("pPr")))})
        style_id = eff["ppr"].get("pStyle")
        if style_id and style_id in styles:
            eff = merge(resolve_style(style_id, styles, docdefaults),
                        {"ppr": parse_ppr(p.find(q("pPr")))})
        style_name = styles.get(style_id, {}).get("name", style_id or "Normal")

        # Run-level fonts/sizes: paragraph props overlaid by each run's own rPr.
        run_fonts, run_sizes, first = [], [], {}
        for r in p.findall(q("r")):
            rpr = merge({"rpr": eff["rpr"], "ppr": {}}, {"rpr": parse_rpr(r.find(q("rPr")))})["rpr"]
            if "".join(t.text or "" for t in r.iter(q("t"))).strip():
                if rpr.get("font"):
                    run_fonts.append(rpr["font"])
                if rpr.get("size"):
                    run_sizes.append(rpr["size"])
                if not first:
                    first = rpr
        font = (run_fonts[0] if run_fonts else eff["rpr"].get("font"))
        size = (run_sizes[0] if run_sizes else eff["rpr"].get("size"))
        text = para_text(p)

        rec = {
            "i": idx,
            "style": style_name,
            "align": eff["ppr"].get("align", "left"),
            "spacing": spacing_label(eff["ppr"]),
            "is_double": is_double(eff["ppr"]),
            "firstLine_in": inches(eff["ppr"]["firstLine"]) if "firstLine" in eff["ppr"] else 0,
            "hanging_in": inches(eff["ppr"]["hanging"]) if "hanging" in eff["ppr"] else 0,
            "left_in": inches(eff["ppr"]["left"]) if "left" in eff["ppr"] else 0,
            "font": font,
            "size": size,
            "bold": bool(first.get("bold") or eff["rpr"].get("bold")),
            "italic": bool(first.get("italic") or eff["rpr"].get("italic")),
            "fonts_all": sorted(set(run_fonts)),
            "sizes_all": sorted(set(run_sizes)),
            "text": text,
        }
        paragraphs.append(rec)
        if text.strip():
            if font:
                font_counts[font] = font_counts.get(font, 0) + 1
            if size:
                size_counts[size] = size_counts.get(size, 0) + 1
            lbl = rec["spacing"]
            if lbl:
                body_spacings.append(lbl)

    # Section / page setup (final sectPr in the body).
    margins, page_size = {}, {}
    sectPr = body.find(q("sectPr"))
    if sectPr is not None:
        pgMar = sectPr.find(q("pgMar"))
        if pgMar is not None:
            for side in ("top", "bottom", "left", "right"):
                v = pgMar.get(q(side))
                if v is not None:
                    try:
                        margins[side] = inches(int(v))
                    except ValueError:
                        pass
        pgSz = sectPr.find(q("pgSz"))
        if pgSz is not None:
            for dim in ("w", "h"):
                v = pgSz.get(q(dim))
                if v is not None:
                    try:
                        page_size[dim] = inches(int(v))
                    except ValueError:
                        pass

    page_number = find_page_number(parts)
    head_txt = header_text(parts)

    result = {
        "file": path,
        "margins_in": margins,
        "page_size_in": page_size,
        "default_font": base_ppr["rpr"].get("font"),
        "default_size_pt": base_ppr["rpr"].get("size"),
        "fonts_used": font_counts,
        "sizes_used_pt": size_counts,
        "body_spacing_values": sorted(set(body_spacings)),
        "page_number": page_number,
        "header_text": head_txt,
        "paragraph_count": len(paragraphs),
        "paragraphs": paragraphs,
    }
    result["structural_findings"] = derive_findings(result)
    return result


def derive_findings(r):
    """Deterministic, high-confidence layout violations. Severity: error|warning|check."""
    f = []

    # Margins: 1" on all sides.
    for side, val in r["margins_in"].items():
        if abs(val - 1.0) > 0.02:
            f.append({"severity": "error", "area": "Document format",
                      "issue": f"{side.capitalize()} margin is {val}\", not the required 1\".",
                      "fix": f"Set the {side} margin to 1 inch."})

    # Page size: US Letter 8.5 x 11.
    ps = r["page_size_in"]
    if ps and (abs(ps.get("w", 8.5) - 8.5) > 0.02 or abs(ps.get("h", 11) - 11) > 0.02):
        f.append({"severity": "warning", "area": "Document format",
                  "issue": f"Page size is {ps.get('w')}\" x {ps.get('h')}\", not 8.5\" x 11\".",
                  "fix": "Set paper size to Letter (8.5\" x 11\")."})

    # Fonts.
    body_fonts = [font for font in r["fonts_used"]]
    non_apa = [font for font in body_fonts if font not in APA_FONTS]
    if len(body_fonts) > 1:
        listing = ", ".join(f"{k} ({v})" for k, v in sorted(r["fonts_used"].items(), key=lambda x: -x[1]))
        f.append({"severity": "warning", "area": "Document format",
                  "issue": f"More than one font appears in the body: {listing}.",
                  "fix": "Use a single, consistent font throughout (headings and body alike)."})
    if non_apa:
        f.append({"severity": "warning", "area": "Document format",
                  "issue": f"Font(s) not in APA's recommended set: {', '.join(non_apa)}.",
                  "fix": "APA recommends Times New Roman 12, Calibri 11, Arial 11, Georgia 11, "
                         "or Lucida Sans Unicode 10. Any font is allowed if legible and consistent, "
                         "but confirm your instructor accepts it."})
    # Size vs font expectation.
    for font, expected in APA_FONTS.items():
        if font in r["fonts_used"]:
            used = [s for s in r["sizes_used_pt"]]
            if used and expected not in [round(s) for s in used]:
                f.append({"severity": "warning", "area": "Document format",
                          "issue": f"{font} is used but the expected APA size is {expected}pt; "
                                   f"sizes found: {sorted(set(round(s,1) for s in used))}.",
                          "fix": f"Use {font} at {expected}pt."})

    # Line spacing: the whole paper is double-spaced.
    non_double = [s for s in r["body_spacing_values"] if "double" not in s and s is not None]
    if non_double and not any("double" in s for s in r["body_spacing_values"]):
        f.append({"severity": "error", "area": "Document format",
                  "issue": f"Body does not appear to be double-spaced (spacing found: {r['body_spacing_values']}).",
                  "fix": "Set line spacing to Double (2.0) for the entire document, with no extra "
                         "space before/after paragraphs."})
    elif non_double:
        f.append({"severity": "check", "area": "Document format",
                  "issue": f"Mixed line spacing detected: {r['body_spacing_values']}. APA is double throughout "
                           "(block quotes and references included).",
                  "fix": "Confirm every part of the paper is double-spaced."})

    # Page number.
    pn = r["page_number"]
    if not pn["present"]:
        f.append({"severity": "error", "area": "Document format",
                  "issue": "No page-number field was found in the header or footer.",
                  "fix": "Insert a page number in the top-right of the header; it appears on every page "
                         "starting with page 1 (student papers use the page number alone -- no running head)."})
    else:
        if pn["location"] != "header":
            f.append({"severity": "error", "area": "Document format",
                      "issue": f"Page number is in the {pn['location']}, but APA places it in the header (top of page).",
                      "fix": "Move the page number to the header, flush right."})
        if pn["align"] not in ("right", "end"):
            f.append({"severity": "error", "area": "Document format",
                      "issue": f"Page number alignment is '{pn['align']}', not right-aligned.",
                      "fix": "Right-align the page number (top-right corner)."})

    # Running head text on a student paper.
    letters = "".join(c for c in r["header_text"] if c.isalpha())
    if letters:
        prof = r["header_text"].isupper()
        f.append({"severity": "check", "area": "Title page / header",
                  "issue": f"The header contains text: \"{r['header_text']}\". "
                           + ("This looks like a professional running head. "
                              if prof else "")
                           + "Student papers omit the running head -- the header should hold only the page number.",
                  "fix": "If this is a student paper, remove the running-head text and keep only the page number. "
                         "If professional, the running head must be the title in ALL CAPS (<=50 chars), flush left."})

    # References hanging indent.
    ref_i = next((p["i"] for p in r["paragraphs"]
                  if p["text"].strip().lower() in ("references", "reference")), None)
    if ref_i is not None:
        end_i = next((p["i"] for p in r["paragraphs"]
                      if p["i"] > ref_i and p["text"].strip().lower().startswith("appendix")), None)
        entries = [p for p in r["paragraphs"]
                   if p["i"] > ref_i and (end_i is None or p["i"] < end_i) and p["text"].strip()]
        bad = [p for p in entries if not (0.45 <= p["hanging_in"] <= 0.55)]
        firstline = [p for p in entries if p["firstLine_in"] > 0.1]
        if firstline:
            f.append({"severity": "error", "area": "Reference list",
                      "issue": f"{len(firstline)} of {len(entries)} reference entries use a first-line "
                               "indent instead of a hanging indent.",
                      "fix": "Switch to a 0.5\" hanging indent (first line flush left, later lines "
                             "indented). Don't fake it with tabs or a first-line indent."})
        elif entries and len(bad) == len(entries):
            f.append({"severity": "error", "area": "Reference list",
                      "issue": "Reference entries do not use a 0.5\" hanging indent "
                               f"(checked {len(entries)} entries).",
                      "fix": "Apply a hanging indent of 0.5\" to every reference entry (Format > Paragraph > "
                             "Special > Hanging). Do not fake it with tabs or first-line indents."})
        elif bad:
            f.append({"severity": "check", "area": "Reference list",
                      "issue": f"{len(bad)} of {len(entries)} reference entries may lack a proper 0.5\" hanging indent.",
                      "fix": "Confirm each reference entry has a 0.5\" hanging indent."})

    return f


def print_report(r, full=False):
    print(f"APA-7 structural scan: {r['file']}")
    print("=" * 70)
    m = r["margins_in"]
    print(f"Margins (in):   top={m.get('top','?')} bottom={m.get('bottom','?')} "
          f"left={m.get('left','?')} right={m.get('right','?')}")
    print(f"Page size (in): {r['page_size_in'].get('w','?')} x {r['page_size_in'].get('h','?')}")
    print(f"Default font:   {r['default_font']} {r['default_size_pt']}pt")
    print(f"Fonts used:     {r['fonts_used']}")
    print(f"Sizes used:     {r['sizes_used_pt']}")
    print(f"Body spacing:   {r['body_spacing_values']}")
    pn = r["page_number"]
    print(f"Page number:    present={pn['present']} location={pn['location']} align={pn['align']}")
    print(f"Header text:    {r['header_text']!r}")
    print(f"Paragraphs:     {r['paragraph_count']}")
    print()
    print(f"STRUCTURAL FINDINGS ({len(r['structural_findings'])}):")
    if not r["structural_findings"]:
        print("  (none -- layout looks APA-compliant at the structural level)")
    for x in r["structural_findings"]:
        print(f"  [{x['severity'].upper()}] {x['area']}: {x['issue']}")
        print(f"          Fix: {x['fix']}")
    if full:
        print("\nPARAGRAPHS (document order):")
        for p in r["paragraphs"]:
            t = p["text"].strip().replace("\n", " ")
            if len(t) > 90:
                t = t[:90] + "..."
            tags = []
            if p["bold"]:
                tags.append("B")
            if p["italic"]:
                tags.append("I")
            print(f"  {p['i']:>3} [{p['style']}|{p['align']}|{p['spacing']}|"
                  f"fl={p['firstLine_in']} hang={p['hanging_in']}|{p['font']} {p['size']}pt "
                  f"{''.join(tags)}] {t!r}")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = [a for a in sys.argv[1:] if a.startswith("--")]
    if not args:
        print(__doc__)
        sys.exit(1)
    path = args[0]
    try:
        r = analyze(path)
    except (zipfile.BadZipFile, ValueError) as e:
        print(f"ERROR: could not read '{path}' as a .docx: {e}", file=sys.stderr)
        sys.exit(2)
    if "--json" in flags:
        print(json.dumps(r, indent=2, ensure_ascii=False))
    else:
        print_report(r, full="--full" in flags)


if __name__ == "__main__":
    main()
