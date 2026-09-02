#!/usr/bin/env python3
"""DV Keywords.xlsx -> seo/data/keywords.json

Reads the workbook with the stdlib only (an .xlsx is a zip of XML), so this runs
anywhere without openpyxl. Each sheet is one keyword cluster mapped to the page
it targets; the highest-volume keyword becomes that page's default focus
keyphrase, which the dashboard lets you override per page.

Usage:  python3 build_keywords.py [path/to/DV Keywords.xlsx]
"""
import json, os, re, sys, zipfile
import xml.etree.ElementTree as ET

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_XLSX = os.path.join(os.path.dirname(HERE), "DV Keywords.xlsx")

# Sheet name -> site path. "AI Services" has no landing page yet; that gap is
# reported rather than silently dropped.
SHEET_TO_PATH = {
    "Home Page":                      "/",
    "Organic Marketing Services":     "/services/organic-marketing/",
    "Pay-Per-Click":                  "/services/pay-per-click/",
    "Paid Social Media Advertising":  "/services/paid-social-media-advertising/",
    "Performance Marketing Services": "/services/performance-marketing-agency/",
    "GEO":                            "/services/generative-search-optimisation/",
    "Whatsapp":                       "/services/whatsapp-marketing/",
    "SEO":                            "/services/seo/",
    "Branding":                       "/services/branding-and-design/",
    "Native":                         "/services/native-advertising/",
    "E-Commerce":                     "/services/ecommerce-marketing/",
    "Data stratergy":                 "/services/data-strategy-consulting-services/",
    "CRM":                            "/services/crm-services/",
    "Web development services":       "/services/website-development/",
    "AI Services":                    None,
}


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def read_workbook(path):
    z = zipfile.ZipFile(path)
    shared = []
    if "xl/sharedStrings.xml" in z.namelist():
        for si in ET.fromstring(z.read("xl/sharedStrings.xml")).iter(NS + "si"):
            shared.append("".join(t.text or "" for t in si.iter(NS + "t")))

    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = {r.get("Id"): r.get("Target") for r in
            ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
    sheets = []
    for sh in wb.iter(NS + "sheet"):
        rid = sh.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
        target = rels.get(rid, "")
        p = ("xl/" + target.lstrip("/")).replace("xl/xl/", "xl/")
        sheets.append((sh.get("name"), p))

    out = {}
    for name, path_in_zip in sheets:
        if path_in_zip not in z.namelist():
            continue
        rows = []
        for row in ET.fromstring(z.read(path_in_zip)).iter(NS + "row"):
            cells = []
            for c in row.iter(NS + "c"):
                v = c.find(NS + "v")
                if v is None:
                    is_el = c.find(NS + "is")
                    txt = "".join(t.text or "" for t in is_el.iter(NS + "t")) if is_el is not None else ""
                else:
                    txt = shared[int(v.text)] if c.get("t") == "s" else (v.text or "")
                cells.append((txt or "").strip())
            while cells and not cells[-1]:
                cells.pop()
            if cells:
                rows.append(cells)
        out[name] = rows
    return out


def main():
    xlsx = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_XLSX
    if not os.path.isfile(xlsx):
        sys.exit(f"workbook not found: {xlsx}")

    sheets = read_workbook(xlsx)
    clusters, unmapped = {}, []

    for name, rows in sheets.items():
        if not rows:
            continue
        header = [h.lower() for h in rows[0]]
        def col(*names, default=None):
            for n in names:
                if n in header:
                    return header.index(n)
            return default
        i_kw   = col("keyword", default=0)
        i_int  = col("intent")
        i_vol  = col("volume")
        i_kd   = col("keyword difficulty", "kd")

        kws = []
        for row in rows[1:]:
            def cell(i):
                return row[i] if (i is not None and i < len(row)) else ""
            kw = cell(i_kw)
            if not kw:
                continue
            # A few sheets shift columns (CRM puts volume where intent belongs).
            intent, vol, kd = cell(i_int), _num(cell(i_vol)), cell(i_kd)
            if vol is None and _num(intent) is not None:
                vol, intent = _num(intent), ""
            kws.append({
                "keyword": kw,
                "intent": intent or None,
                "volume": int(vol) if vol is not None else None,
                "difficulty": (int(_num(kd)) if _num(kd) is not None else (kd or None)),
            })
        if not kws:
            continue

        kws.sort(key=lambda k: (k["volume"] or 0), reverse=True)
        path = SHEET_TO_PATH.get(name, "__missing__")
        if path is None:
            unmapped.append({"sheet": name, "keywords": len(kws),
                             "top": kws[0]["keyword"],
                             "volume": sum(k["volume"] or 0 for k in kws)})
            continue
        if path == "__missing__":
            unmapped.append({"sheet": name, "keywords": len(kws),
                             "top": kws[0]["keyword"], "volume": None})
            continue

        clusters[path] = {
            "sheet": name,
            "focus": kws[0]["keyword"],
            "keywords": kws,
            "total_volume": sum(k["volume"] or 0 for k in kws),
        }

    data = {"source": os.path.basename(xlsx), "clusters": clusters, "unmapped": unmapped}
    out = os.path.join(HERE, "data", "keywords.json")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=1, ensure_ascii=False)

    print(f"{len(clusters)} clusters -> {out}")
    for p, c in sorted(clusters.items(), key=lambda kv: -kv[1]["total_volume"]):
        print(f"  {c['total_volume']:>8,}  {p:<52} focus: {c['focus']}")
    for u in unmapped:
        print(f"  [no landing page] sheet '{u['sheet']}' — {u['keywords']} keywords, top: {u['top']}")


if __name__ == "__main__":
    main()
